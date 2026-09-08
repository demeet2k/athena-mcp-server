"""Discover and read committed Wiki drafts without checkout or repository execution.

Validation binds bytes to an explicit commit and its internal source/plan
identities. It does not authenticate a producer or repeat semantic LINT.
"""
import hashlib
import json
import re

from .wiki_git import canonical
from .wiki_git_draft import ARTIFACT as DRAFT_ARTIFACT, _git, _text, _resolve_ref
from .wiki_git_snapshot import read_snapshot, decode_snapshot, sha, MAX_BYTES
from .wiki_memory import VERSION, digest, checked_text, identifier

ARTIFACT = 'ATHENA.MCP.WIKI_GIT_REVIEW.V1'
REF = r'^refs/heads/codex/wiki-draft-[0-9a-f]{32}$'


class WikiGitReview:
    def __init__(self, server):
        self.git = server.git

    def review(self, *, action, ref=None, expected_commit=None, limit=20,
               offset=0, include_source=False):
        try:
            return self._review(action=action, ref=ref, expected_commit=expected_commit,
                                limit=limit, offset=offset, include_source=include_source)
        except (KeyError, TypeError, UnicodeError, IndexError) as exc:
            raise ValueError('WIKI_REVIEW_MALFORMED_COMMITTED_DRAFT') from exc

    def _review(self, *, action, ref, expected_commit, limit, offset, include_source):
        if not self.git.enabled:
            raise ValueError('WIKI_REVIEW_ROOT_NOT_CONFIGURED')
        if type(include_source) is not bool:
            raise ValueError('WIKI_REVIEW_BOOLEAN_REQUIRED')
        if action == 'LIST':
            if ref is not None or expected_commit is not None or include_source:
                raise ValueError('WIKI_REVIEW_LIST_ARGUMENTS')
            if type(limit) is not int or not 1 <= limit <= 100 or type(offset) is not int or not 0 <= offset <= 10000:
                raise ValueError('WIKI_REVIEW_PAGE_BOUNDS')
            raw = _text(self.git.root, 'for-each-ref', '--sort=refname',
                        '--count=' + str(offset + limit + 1),
                        '--format=%(refname)%00%(objectname)%00%(objecttype)%00%(symref)',
                        'refs/heads/codex/wiki-draft-*')
            rows = []
            for line in raw.splitlines()[offset:]:
                name, commit, kind, symbolic = line.split('\0')
                rows.append(dict(ref=name, commit=commit, object_type=kind,
                                 symbolic_target=symbolic or None, verified=False))
            more = len(rows) > limit
            return dict(artifact=ARTIFACT, standing='UNVERIFIED_REF_INVENTORY',
                        drafts=rows[:limit], truncated=more,
                        next_offset=offset + limit if more else None,
                        inventory_atomic=False, mutation_applied=False)
        if action != 'READ' or type(ref) is not str or not re.fullmatch(REF, ref):
            raise ValueError('WIKI_REVIEW_EXACT_DRAFT_REF_REQUIRED')
        if type(expected_commit) is not str or not re.fullmatch('[0-9a-f]{40}', expected_commit):
            raise ValueError('WIKI_REVIEW_EXACT_COMMIT_REQUIRED')
        if limit != 20 or offset != 0:
            raise ValueError('WIKI_REVIEW_READ_HAS_NO_PAGINATION')
        root = self.git.root
        if _resolve_ref(root, ref) != expected_commit:
            raise ValueError('WIKI_REVIEW_STALE_REF')
        if _text(root, 'cat-file', '-t', expected_commit) != 'commit':
            raise ValueError('WIKI_REVIEW_COMMIT_REQUIRED')
        if int(_text(root, 'cat-file', '-s', expected_commit)) > 65536:
            raise ValueError('WIKI_REVIEW_COMMIT_TOO_LARGE')
        message = _text(root, 'show', '-s', '--format=%B', expected_commit)
        prefix = 'Athena Wiki observation draft\n\n'
        if not message.startswith(prefix):
            raise ValueError('WIKI_REVIEW_DRAFT_BINDING_REQUIRED')
        binding = json.loads(message[len(prefix):])
        keys = {'artifact', 'base', 'snapshot_id', 'page_id', 'document_id',
                'plan_sha256', 'carrier_sha256', 'scope'}
        if type(binding) is not dict or set(binding) != keys or message != prefix + canonical(binding).decode('utf-8'):
            raise ValueError('WIKI_REVIEW_CANONICAL_BINDING_REQUIRED')
        if binding['artifact'] != DRAFT_ARTIFACT or binding['scope'] != 'LOCAL_REVIEW_BRANCH_ONLY':
            raise ValueError('WIKI_REVIEW_BINDING_SCOPE')
        for key, size in [('base', 40), ('snapshot_id', 64), ('document_id', 64), ('plan_sha256', 64)]:
            if type(binding[key]) is not str or not re.fullmatch('[0-9a-f]{' + str(size) + '}', binding[key]):
                raise ValueError('WIKI_REVIEW_BINDING_IDENTITY')
        identifier(binding['page_id'])
        draft_id = hashlib.sha256(canonical(binding)).hexdigest()
        if ref != 'refs/heads/codex/wiki-draft-' + draft_id[:32]:
            raise ValueError('WIKI_REVIEW_REF_BINDING_MISMATCH')
        base = binding['base']
        if _text(root, 'rev-list', '--parents', '-n', '1', expected_commit).split() != [expected_commit, base]:
            raise ValueError('WIKI_REVIEW_PARENT_MISMATCH')
        # The supplied runner strips Git environment overrides and disables
        # replacement objects. This path never runs the semantic repository.
        run = lambda *args: _git(root, *args).stdout
        before = read_snapshot(self.git, base, run=run)
        after = read_snapshot(self.git, expected_commit, run=run)
        if set(before) - set(after):
            raise ValueError('WIKI_REVIEW_UNEXPECTED_DELETION')
        plan = []
        for path, value in sorted(after.items()):
            if path in before and sha(value) == sha(before[path]):
                continue
            text = value.decode('utf-8') if type(value) is bytes else value
            plan.append(dict(action='REPLACE_IF_DIGEST' if path in before else 'CREATE',
                             path=path, expected_sha256=sha(before[path]) if path in before else None,
                             content=text, content_sha256=sha(text)))
        changed = {p.decode('utf-8') for p in run('diff-tree', '--no-commit-id', '--name-only', '-r', '-z', base, expected_commit).split(b'\0') if p}
        if not plan or changed != {p['path'] for p in plan}:
            raise ValueError('WIKI_REVIEW_UNEXPECTED_CHANGED_PATHS')
        if hashlib.sha256(canonical(plan)).hexdigest() != binding['plan_sha256']:
            raise ValueError('WIKI_REVIEW_PLAN_DIGEST_MISMATCH')
        path = 'knowledge/raw/drive/' + binding['document_id'] + '.json'
        if path in before or path not in after or sha(after[path]) != binding['carrier_sha256']:
            raise ValueError('WIKI_REVIEW_CARRIER_MISMATCH')
        carrier = json.loads(after[path])
        if (carrier.get('artifact') != 'ATHENA.DRIVE.WIKI.OBSERVATION.CARRIER.V1'
                or carrier.get('scope') != 'EXACT_DOCUMENT_AND_PAGE_CONTEXT_NOT_COMPLETE_REGISTRY'
                or carrier.get('live_currentness') != 'UNVERIFIED'
                or carrier.get('source_claims_independently_verified') is not False):
            raise ValueError('WIKI_REVIEW_CARRIER_SCOPE')
        registry, page, doc = (carrier[k] for k in ('registry_observation', 'page', 'document'))
        registry_id = digest(json.dumps([VERSION, registry['source_id'], registry['observed_at'], registry['source_sha256']], ensure_ascii=False))
        if registry_id != binding['snapshot_id'] or registry['snapshot_id'] != registry_id or page['PAGE_ID'] != binding['page_id']:
            raise ValueError('WIKI_REVIEW_REGISTRY_IDENTITY')
        checked_text(doc['source_text'], doc['source_sha256'])
        document_id = digest(json.dumps([VERSION, registry_id, page['PAGE_ID'], page['DRIVE_FILE_ID'], doc['source_revision'], doc['source_sha256']], ensure_ascii=False))
        if document_id != binding['document_id'] or doc['document_id'] != document_id:
            raise ValueError('WIKI_REVIEW_DOCUMENT_IDENTITY')
        # Verify the source ledger's carrier references and structural page
        # metadata without invoking repository code or importing the observation.
        state = decode_snapshot(after)
        if _resolve_ref(root, ref) != expected_commit:
            raise ValueError('WIKI_REVIEW_REF_CHANGED_DURING_READ')
        result = dict(artifact=ARTIFACT, standing='VERIFIED_DRAFT_BYTES', ref=ref,
                      commit=expected_commit, draft_id=draft_id, binding=binding,
                      configured_head=_text(root, 'rev-parse', 'HEAD'),
                      changed_files=[{k: v for k, v in p.items() if k != 'content'} for p in plan],
                      source_document={k: v for k, v in doc.items() if k != 'source_text'},
                      source_record_counts={k: len(v) for k, v in carrier['records'].items()},
                      original_claim_labels=[c.get('EPI', 'UNSPECIFIED') for c in carrier['records']['claims']],
                      wiki_page_count=len(state['pages']), semantic_lint='NOT_RUN',
                      producer_authenticated=False, database_required=False,
                      source_claims_independently_verified=False,
                      live_currentness='UNVERIFIED', behavioral_gain='UNKNOWN',
                      mutation_applied=False, source_included=include_source)
        if include_source:
            result['source_carrier'] = carrier
        if len(canonical(result)) > MAX_BYTES:
            raise ValueError('WIKI_REVIEW_RESPONSE_TOO_LARGE')
        return result
