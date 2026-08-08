from __future__ import annotations

import argparse
import json
import os
import sys

from .orchestration_authority import AuthorityLedger
from .orchestration_authority_protocol import AUTHORITY_RESOURCE, AUTHORITY_TOOLS
from .orchestration_authority_runtime import AuthorityOrchestrationRuntime
from .orchestration_authority_surface import AUTHORITY_TOOL_NAMES, authority_resource_value, call_authority_tool
from .server import Server
from .validate import validate


class AuthorityServer(Server):
    """Fully composed MCP server with typed claim authority.

    It inherits the current server so transform execution, emission verification,
    branch evolution, sessions, Git CAS, crystals, coordinates and every other
    mature surface remain intact. Only orchestration is replaced with the
    authority-aware adapter, and authority-specific tools/resources are added.
    """

    def __init__(self, db, git_root=None):
        super().__init__(db, git_root)
        self.authority = AuthorityLedger(self.core)
        self.orchestration = AuthorityOrchestrationRuntime(
            self.core,
            branches=getattr(self, 'branches', None),
            authority=self.authority,
        )
        self._authority_tool_map = {tool['name']: tool for tool in AUTHORITY_TOOLS}

    def call_tool(self, name, args):
        if name in AUTHORITY_TOOL_NAMES:
            return call_authority_tool(self.authority, name, args)
        if name == 'athena_benchmark':
            result = super().call_tool(name, args)
            result.update(self.authority.benchmark())
            return result
        return super().call_tool(name, args)

    def handle(self, message):
        method = message.get('method')
        params = message.get('params') or {}
        mid = message.get('id')

        if method == 'tools/list':
            base = super().handle(message)
            tools = list(base['result']['tools']) + list(AUTHORITY_TOOLS)
            dedup = {tool['name']: tool for tool in tools}
            base['result']['tools'] = sorted(dedup.values(), key=lambda x: x['name'])
            return base

        if method == 'tools/call' and params.get('name') in AUTHORITY_TOOL_NAMES:
            name = params['name']
            args = params.get('arguments') or {}
            if not self.rate.allow(name):
                return self.result(mid, {
                    'content': [{'type': 'text', 'text': 'Rate limit exceeded; retry later.'}],
                    'isError': True,
                })
            try:
                validate(self._authority_tool_map[name]['inputSchema'], args)
                value = self.call_tool(name, args)
                return self.result(mid, {
                    'content': [{'type': 'text', 'text': json.dumps(value, ensure_ascii=False, sort_keys=True)}],
                    'structuredContent': value,
                    'isError': False,
                })
            except (ValueError, KeyError) as exc:
                return self.result(mid, {
                    'content': [{'type': 'text', 'text': str(exc)}],
                    'isError': True,
                })

        if method == 'resources/list':
            base = super().handle(message)
            resources = list(base['result']['resources'])
            if AUTHORITY_RESOURCE['uri'] not in {r['uri'] for r in resources}:
                resources.append(AUTHORITY_RESOURCE)
            base['result']['resources'] = resources
            return base

        if method == 'resources/read' and params.get('uri') == AUTHORITY_RESOURCE['uri']:
            value = authority_resource_value(self.authority)
            return self.result(mid, {
                'contents': [{
                    'uri': AUTHORITY_RESOURCE['uri'],
                    'mimeType': 'application/json',
                    'text': json.dumps(value, ensure_ascii=False, sort_keys=True),
                }]
            })

        if method == 'prompts/get' and params.get('name') == 'athena_maxdev':
            base = super().handle(message)
            messages = base.get('result', {}).get('messages', [])
            if messages:
                content = messages[0].get('content', {})
                text = content.get('text', '')
                content['text'] = text + """
14 AUTHORITY: Y∈{?,+,!,#} is a persistent non-skippable claim state, not confidence or branch reward. Link work through claim_id and declare min_authority when execution requires a threshold. ?->+ requires verified support/derive/reproduce evidence; +->! requires procedure+observation+result+witness; !-># requires explicit authorized canonical ref. CHALLENGED or CANONICAL_CHALLENGED claims are excluded from automatic routing until resolved. AORRUN freezes authority snapshots so later promotion/challenge resolution cannot rewrite historical decisions.
"""
            return base

        return super().handle(message)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default=os.getenv('ATHENA_DB', './state/athena.db'))
    parser.add_argument('--git-root', default=os.getenv('ATHENA_GIT_ROOT'))
    args = parser.parse_args(argv)
    server = AuthorityServer(args.db, args.git_root)
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            message = json.loads(raw)
            response = server.handle(message)
        except Exception as exc:
            response = {
                'jsonrpc': '2.0',
                'id': None,
                'error': {'code': -32700, 'message': f'Parse error: {exc}'},
            }
        if response is not None:
            sys.stdout.write(json.dumps(response, separators=(',', ':'), ensure_ascii=False) + '\n')
            sys.stdout.flush()


if __name__ == '__main__':
    main()
