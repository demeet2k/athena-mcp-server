"""Query complete committed Wiki data with the configured trusted compiler.

The data commit is read as Git objects, without a separate checkout. Compiler
code remains bound to the explicit clean configured HEAD. Neither identity is
evidence of source truth, producer authentication or live Drive currentness.
"""
import hashlib
import re

from .wiki_git import GitWikiCompiler, canonical, MAX_RESPONSE_BYTES
from .wiki_git_draft import _git
from .wiki_git_snapshot import read_snapshot, decode_snapshot, sha

ARTIFACT = 'ATHENA.MCP.WIKI_GIT_QUERY.V1'


class WikiGitQuery:
    def __init__(self, server):
        self.git = server.git

    def query(self, *, expected_git_head, wiki_commit, query, limit=12):
        for value in (expected_git_head, wiki_commit):
            if type(value) is not str or not re.fullmatch('[0-9a-f]{40}', value):
                raise ValueError('WIKI_QUERY_EXACT_COMMITS_REQUIRED')
        if type(query) is not str or not query.strip() or len(query) > 4096:
            raise ValueError('WIKI_QUERY_NONEMPTY_BOUNDED_TEXT_REQUIRED')
        if type(limit) is not int or not 1 <= limit <= 50:
            raise ValueError('WIKI_QUERY_LIMIT_BOUNDS')
        if not self.git.enabled:
            raise ValueError('WIKI_QUERY_ROOT_NOT_CONFIGURED')
        before = self.git.status()
        if before['head'] != expected_git_head or before['dirty']:
            raise ValueError('WIKI_QUERY_CLEAN_EXPECTED_HEAD_REQUIRED')
        run = lambda *args, **kwargs: _git(self.git.root, *args, **kwargs).stdout
        if run('cat-file', '-t', wiki_commit).strip() != b'commit':
            raise ValueError('WIKI_QUERY_DATA_COMMIT_REQUIRED')
        tree = run('rev-parse', wiki_commit + '^{tree}').decode('ascii').strip()
        try:
            files = read_snapshot(self.git, wiki_commit, run=run)
            state = decode_snapshot(files)
        except (KeyError, TypeError, UnicodeError, IndexError) as exc:
            raise ValueError('WIKI_QUERY_MALFORMED_COMMITTED_WIKI') from exc
        readset = {path: sha(content) for path, content in sorted(files.items())}
        request = dict(operation='QUERY', wiki=state['config'], query=query, limit=limit,
                       **{k: state[k] for k in ('pages', 'claims', 'sources', 'contradictions')})
        receipt = GitWikiCompiler(self.git).compile(expected_git_head=expected_git_head,
                                                   request=request)
        if self.git.status() != before:
            raise ValueError('WIKI_QUERY_CONFIGURED_STATE_CHANGED')
        result = dict(artifact=ARTIFACT, standing=receipt['standing'],
                      wiki_standing=receipt.get('wiki_standing', 'NOT_EXECUTED'),
                      compiler_commit=expected_git_head, wiki_commit=wiki_commit,
                      wiki_tree=tree, readset=readset,
                      readset_sha256=hashlib.sha256(canonical(readset)).hexdigest(),
                      snapshot_counts={k: len(state[k]) for k in ('pages', 'claims', 'sources', 'contradictions')},
                      snapshot_scope='COMPLETE_COMMITTED_WIKI_NOT_CALLER_SUPPLIED_COLLECTIONS',
                      compiler_receipt=receipt, mutation_applied=False,
                      data_checkout_materialized=False,
                      execution_source='CONFIGURED_COMPILER_CHECKOUT', producer_authenticated=False,
                      live_currentness='UNVERIFIED', behavioral_gain='UNKNOWN')
        if len(canonical(result)) > MAX_RESPONSE_BYTES:
            raise ValueError('WIKI_QUERY_RESPONSE_TOO_LARGE')
        return result
