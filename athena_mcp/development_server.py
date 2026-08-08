from __future__ import annotations

import argparse
import json
import os
import sys

from .authority_server import AuthorityServer
from .orchestration_equivalence import EquivalenceLedger
from .orchestration_equivalence_protocol import EQUIVALENCE_RESOURCE, EQUIVALENCE_TOOLS
from .orchestration_equivalence_surface import EQUIVALENCE_TOOL_NAMES, call_equivalence_tool, equivalence_resource_value
from .orchestration_extract import ExtractionLedger
from .orchestration_extract_protocol import EXTRACTION_RESOURCE, EXTRACTION_TOOLS
from .orchestration_extract_surface import EXTRACTION_TOOL_NAMES, call_extraction_tool, extraction_resource_value
from .validate import validate


class DevelopmentServer(AuthorityServer):
    """Composed AOR developmental server.

    Layer order:
    base mature runtime -> branch evolution -> authority -> witnessed equivalence
    -> recursive extraction. Every unknown tool/resource delegates downward.
    """

    def __init__(self, db, git_root=None):
        super().__init__(db, git_root)
        self.equivalence = EquivalenceLedger(self.core)
        self.extraction = ExtractionLedger(self.core)
        self._development_tools = {
            tool['name']: tool
            for tool in list(EQUIVALENCE_TOOLS) + list(EXTRACTION_TOOLS)
        }

    def call_tool(self, name, args):
        if name in EQUIVALENCE_TOOL_NAMES:
            return call_equivalence_tool(self.equivalence, name, args)
        if name in EXTRACTION_TOOL_NAMES:
            return call_extraction_tool(self.extraction, name, args)
        if name == 'athena_benchmark':
            result = super().call_tool(name, args)
            result.update(self.equivalence.benchmark())
            result.update(self.extraction.benchmark())
            return result
        return super().call_tool(name, args)

    def _tool_call(self, message, tool_map, tool_names):
        params = message.get('params') or {}
        name = params.get('name')
        if name not in tool_names:
            return None
        mid = message.get('id')
        args = params.get('arguments') or {}
        if not self.rate.allow(name):
            return self.result(mid, {
                'content': [{'type': 'text', 'text': 'Rate limit exceeded; retry later.'}],
                'isError': True,
            })
        try:
            validate(tool_map[name]['inputSchema'], args)
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

    def handle(self, message):
        method = message.get('method')
        params = message.get('params') or {}
        mid = message.get('id')

        if method == 'tools/list':
            base = super().handle(message)
            tools = list(base['result']['tools']) + list(self._development_tools.values())
            dedup = {tool['name']: tool for tool in tools}
            base['result']['tools'] = sorted(dedup.values(), key=lambda x: x['name'])
            return base

        if method == 'tools/call':
            response = self._tool_call(message, self._development_tools, set(self._development_tools))
            if response is not None:
                return response

        if method == 'resources/list':
            base = super().handle(message)
            resources = list(base['result']['resources'])
            known = {r['uri'] for r in resources}
            for resource in (EQUIVALENCE_RESOURCE, EXTRACTION_RESOURCE):
                if resource['uri'] not in known:
                    resources.append(resource)
            base['result']['resources'] = resources
            return base

        if method == 'resources/read' and params.get('uri') == EQUIVALENCE_RESOURCE['uri']:
            value = equivalence_resource_value(self.equivalence)
            return self.result(mid, {
                'contents': [{
                    'uri': EQUIVALENCE_RESOURCE['uri'],
                    'mimeType': 'application/json',
                    'text': json.dumps(value, ensure_ascii=False, sort_keys=True),
                }]
            })

        if method == 'resources/read' and params.get('uri') == EXTRACTION_RESOURCE['uri']:
            value = extraction_resource_value(self.extraction)
            return self.result(mid, {
                'contents': [{
                    'uri': EXTRACTION_RESOURCE['uri'],
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
15 EXTRACTION/EQUIVALENCE: `SX+ = dedup(SX U T(SX))` is two lawful stages, not similarity compression. Use SX.1 to create bounded typed transform tasks for decompose/formalize/dual/invert/compose/recur/edge/contradict/fail/falsify/bridge/implement/test/compress/reconstruct/successor. PLANNED != EXECUTED; complete/fail only with verified witnesses. Feed verified EXTRES outputs recursively within declared depth/task limits. Before quotienting outputs, use EQ.1 witnessed equivalence. UNKNOWN sameness preserves identity. EQUIVALENT requires proven sameness across semantic object, functional role, proof route, carrier, lineage, boundary and failure role. Direct/transitive contradiction produces PRESERVE_ALL_CONFLICT until explicitly authorized resolution. dedup != erase; quotient members and witness routes remain reconstructable.
"""
            return base

        return super().handle(message)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default=os.getenv('ATHENA_DB', './state/athena.db'))
    parser.add_argument('--git-root', default=os.getenv('ATHENA_GIT_ROOT'))
    args = parser.parse_args(argv)
    server = DevelopmentServer(args.db, args.git_root)
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
