"""Open a cited source at an exact Wiki commit without executing repository code."""
import base64
import hashlib
import re

from .wiki_git import canonical, MAX_RESPONSE_BYTES
from .wiki_git_draft import _git
from .wiki_git_snapshot import read_snapshot, decode_snapshot, sha

ARTIFACT = 'ATHENA.MCP.WIKI_GIT_SOURCE.V1'


class WikiGitSource:
    def __init__(self, server):
        self.git = server.git

    def read(self, *, wiki_commit, source_id, expected_content_sha256):
        if type(wiki_commit) is not str or not re.fullmatch('[0-9a-f]{40}', wiki_commit):
            raise ValueError('WIKI_SOURCE_EXACT_COMMIT_REQUIRED')
        if type(source_id) is not str or not source_id.strip() or len(source_id) > 512:
            raise ValueError('WIKI_SOURCE_BOUNDED_ID_REQUIRED')
        if (type(expected_content_sha256) is not str
                or not re.fullmatch('sha256:[0-9a-f]{64}', expected_content_sha256)):
            raise ValueError('WIKI_SOURCE_EXPECTED_DIGEST_REQUIRED')
        if not self.git.enabled:
            raise ValueError('WIKI_SOURCE_ROOT_NOT_CONFIGURED')
        run = lambda *args: _git(self.git.root, *args).stdout
        if run('cat-file', '-t', wiki_commit).strip() != b'commit':
            raise ValueError('WIKI_SOURCE_DATA_COMMIT_REQUIRED')
        tree = run('rev-parse', wiki_commit + '^{tree}').decode('ascii').strip()
        try:
            files = read_snapshot(self.git, wiki_commit, run=run)
            state = decode_snapshot(files)
            identities = [s['source_id'] for s in state['sources']]
            if (any(type(s) is not str or not s.strip() for s in identities)
                    or len(set(identities)) != len(identities)):
                raise ValueError('WIKI_SOURCE_AMBIGUOUS_SOURCE_IDENTITIES')
            matches = [s for s in state['sources'] if s['source_id'] == source_id]
            if not matches:
                raise ValueError('WIKI_SOURCE_NOT_FOUND')
            source = matches[0]
            raw = files[source['raw_path']]
        except (KeyError, TypeError, UnicodeError, IndexError) as exc:
            raise ValueError('WIKI_SOURCE_MALFORMED_COMMITTED_WIKI') from exc
        if sha(raw) != expected_content_sha256:
            raise ValueError('WIKI_SOURCE_CITATION_DIGEST_MISMATCH')
        try:
            content, encoding = raw.decode('utf-8'), 'utf-8'
        except UnicodeDecodeError:
            content, encoding = base64.b64encode(raw).decode('ascii'), 'base64'
        readset = {path: sha(value) for path, value in sorted(files.items())}
        result = dict(artifact=ARTIFACT, standing='COMMITTED_SOURCE_BYTES_VERIFIED',
                      wiki_commit=wiki_commit, wiki_tree=tree, source=source,
                      content=content, content_encoding=encoding, content_bytes=len(raw),
                      content_sha256=sha(raw), readset=readset,
                      readset_sha256=hashlib.sha256(canonical(readset)).hexdigest(),
                      repository_code_executed=False, data_checkout_materialized=False,
                      mutation_applied=False, database_imported=False,
                      draft_binding_verified=False, producer_authenticated=False,
                      live_currentness='UNVERIFIED', behavioral_gain='UNKNOWN')
        if len(canonical(result)) > MAX_RESPONSE_BYTES:
            raise ValueError('WIKI_SOURCE_RESPONSE_TOO_LARGE')
        return result
