"""Materialize a reviewed observation on an immutable local review branch.

The configured checkout/index and its current branch are never written. A
temporary clone supplies the commit and fresh compiler check; only its objects
and a create-only codex/wiki-draft-* ref return to the configured repository.
This is not Room ownership, a shared-branch update, or a push operation.
"""
import hashlib
import os
from pathlib import Path
import re
import subprocess
import tempfile

from .git_backend import GitBackend
from .wiki_git import GitWikiCompiler, canonical
from .wiki_git_ingest import WikiGitIngest
from .wiki_git_snapshot import decode_snapshot, read_snapshot, safe_path, sha, simulate

ARTIFACT = 'ATHENA.MCP.WIKI_GIT_DRAFT.V1'
_DEVICE = re.compile(r'^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)', re.I)


def _git(root, *args, input=None, check=True):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1', GIT_NO_REPLACE_OBJECTS='1')
    result = subprocess.run(['git', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false',
                             '-C', str(root), *args], input=input, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env, timeout=180)
    if check and result.returncode:
        raise ValueError('WIKI_DRAFT_GIT_FAILED:' + result.stderr.decode('utf-8', errors='replace')[-1000:])
    return result


def _text(root, *args):
    return _git(root, *args).stdout.decode('utf-8').strip()


def _resolve_ref(root, ref):
    if _git(root, 'symbolic-ref', '--quiet', ref, check=False).returncode == 0:
        raise ValueError('WIKI_DRAFT_SYMBOLIC_REF_FORBIDDEN')
    result = _git(root, 'rev-parse', '--verify', '--quiet', ref, check=False)
    if result.returncode == 1:
        return None
    if result.returncode:
        raise ValueError('WIKI_DRAFT_REF_READ_FAILED')
    return result.stdout.decode('ascii').strip()


def _fingerprints(files):
    return {path: sha(content) for path, content in files.items()}


def _validate_commit(root, head, base, message, projected, paths):
    if _text(root, 'rev-list', '--parents', '-n', '1', head).split() != [head, base]:
        raise ValueError('WIKI_DRAFT_REF_PARENT_MISMATCH')
    if _text(root, 'show', '-s', '--format=%B', head) != message.strip():
        raise ValueError('WIKI_DRAFT_REF_BINDING_MISMATCH')
    changed = _git(root, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', base, head).stdout
    if {p.decode('utf-8') for p in changed.split(b'\0') if p} != set(paths):
        raise ValueError('WIKI_DRAFT_UNEXPECTED_CHANGED_PATHS')
    if _fingerprints(read_snapshot(GitBackend(root), head)) != _fingerprints(projected):
        raise ValueError('WIKI_DRAFT_COMMITTED_BYTES_MISMATCH')


class WikiGitDraft:
    def __init__(self, server):
        self.server = server

    def stage(self, *, expected_git_head, snapshot_id, page_id, document_id, expected_plan_sha256):
        if type(expected_plan_sha256) is not str or not re.fullmatch('[0-9a-f]{64}', expected_plan_sha256):
            raise ValueError('WIKI_DRAFT_REVIEWED_PLAN_DIGEST_REQUIRED')
        original = self.server.git
        initial = original.status()
        proposal = WikiGitIngest(self.server).compile(expected_git_head=expected_git_head,
                         snapshot_id=snapshot_id, page_id=page_id, document_id=document_id)
        if proposal.get('standing') != 'READY_PROPOSAL':
            raise ValueError('WIKI_DRAFT_READY_PROPOSAL_REQUIRED')
        plan = proposal['mutation_plan']
        if (hashlib.sha256(canonical(plan)).hexdigest() != expected_plan_sha256
                or proposal['plan_sha256'] != expected_plan_sha256):
            raise ValueError('WIKI_DRAFT_REVIEWED_PLAN_CHANGED')
        before = read_snapshot(original, expected_git_head)
        if _fingerprints(before) != proposal['base_readset']:
            raise ValueError('WIKI_DRAFT_BASE_READSET_CHANGED')
        paths = []
        for item in plan:
            path = safe_path(item['path'])
            if any(part.endswith(('.', ' ')) or _DEVICE.match(part) for part in path.split('/')):
                raise ValueError('WIKI_DRAFT_NONPORTABLE_PATH')
            if item['action'] not in ('CREATE', 'REPLACE_IF_DIGEST') or sha(item['content']) != item['content_sha256']:
                raise ValueError('WIKI_DRAFT_INVALID_PLAN_ITEM')
            paths.append(path)
        if not paths or len({p.casefold() for p in paths}) != len(paths):
            raise ValueError('WIKI_DRAFT_EMPTY_OR_COLLIDING_PLAN')
        projected = simulate(before, plan)
        if len({p.casefold() for p in projected}) != len(projected):
            raise ValueError('WIKI_DRAFT_CASE_COLLISION')
        binding = dict(artifact=ARTIFACT, base=expected_git_head, snapshot_id=snapshot_id,
                       page_id=page_id, document_id=document_id, plan_sha256=expected_plan_sha256,
                       carrier_sha256=proposal['carrier_sha256'], scope='LOCAL_REVIEW_BRANCH_ONLY')
        draft_id = hashlib.sha256(canonical(binding)).hexdigest()
        ref = 'refs/heads/codex/wiki-draft-' + draft_id[:32]
        message = 'Athena Wiki observation draft\n\n' + canonical(binding).decode('utf-8') + '\n'
        existing = _resolve_ref(original.root, ref)
        if existing:
            _validate_commit(original.root, existing, expected_git_head, message, projected, paths)
        with tempfile.TemporaryDirectory(prefix='athena-wiki-draft-') as temporary:
            owned = Path(temporary).resolve()
            target = owned / 'checkout'
            # This owned checkout is the only filesystem target. No caller path,
            # branch name, command, identity, or arbitrary plan is accepted.
            _git(owned, '-c', 'core.autocrlf=false', 'clone', '--quiet', '--no-checkout',
                 '--shared', str(original.root), str(target))
            _git(target, '-c', 'core.autocrlf=false', 'checkout', '--quiet', '--detach', existing or expected_git_head)
            if not existing:
                for item in plan:
                    destination = target / item['path']
                    if not destination.resolve().is_relative_to(target.resolve()):
                        raise ValueError('WIKI_DRAFT_PATH_ESCAPE')
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(item['content'].encode('utf-8'))
                for path in paths:
                    _git(target, '-c', 'core.filemode=false', 'add', '--', path)
                hooks = owned / 'empty-hooks'
                hooks.mkdir()
                _git(target, '-c', 'core.hooksPath=' + str(hooks), '-c', 'commit.gpgSign=false',
                     '-c', 'user.name=Athena Wiki Bridge', '-c', 'user.email=athena-wiki@example.invalid',
                     'commit', '--quiet', '--file=-', input=message.encode('utf-8'))
            head = _text(target, 'rev-parse', 'HEAD')
            _validate_commit(target, head, expected_git_head, message, projected, paths)
            state = decode_snapshot(read_snapshot(GitBackend(target), head))
            lint = GitWikiCompiler(GitBackend(target)).compile(expected_git_head=head,
                    request={'operation': 'LINT', 'wiki': state['config'],
                             **{k: state[k] for k in ('pages', 'sources', 'claims', 'contradictions')},
                             'index_paths': [p['path'] for p in state['pages']]})
            if lint.get('standing') != 'COMPLETE' or lint.get('wiki_standing') != 'READY':
                raise ValueError('WIKI_DRAFT_COMMITTED_LINT_NOT_READY')
            if original.status() != initial:
                raise ValueError('WIKI_DRAFT_SOURCE_CHANGED_BEFORE_PUBLICATION')
            if not existing:
                # Import immutable objects first. Publishing the one ref is a
                # create-only CAS; a concurrent writer is never overwritten.
                _git(original.root, 'fetch', '--quiet', '--no-tags', '--no-write-fetch-head', str(target), head)
                if original.status() != initial:
                    raise ValueError('WIKI_DRAFT_SOURCE_CHANGED_BEFORE_PUBLICATION')
                _git(original.root, 'update-ref', '--no-deref', ref, head, '0' * 40)
            if _resolve_ref(original.root, ref) != head:
                raise ValueError('WIKI_DRAFT_REF_CHANGED_AFTER_PUBLICATION')
        return dict(artifact=ARTIFACT, standing='READY_LOCAL_DRAFT', draft_id=draft_id,
                    ref=ref, commit=head, base_commit=expected_git_head, reused=bool(existing),
                    snapshot_id=snapshot_id, page_id=page_id, document_id=document_id,
                    plan_sha256=expected_plan_sha256, carrier_sha256=proposal['carrier_sha256'],
                    changed_paths=paths, committed_lint=lint, source_checkout_unchanged=original.status() == initial,
                    mutation_scope='LOCAL_DRAFT_REF_ONLY', shared_state_applied=False, pushed=False,
                    room_admission=False, live_currentness='UNVERIFIED', behavioral_gain='UNKNOWN')
