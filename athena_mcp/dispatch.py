from __future__ import annotations
import json, sys
from .core import StaleTarget
from .git_backend import GitStaleHead
from .kc144 import station_manifest
from .validate import validate
from .protocol import PROTOCOL_VERSION, SERVER_INFO, TOOLS, PROMPTS

def handle(server,m):
        mid=m.get('id'); method=m.get('method'); params=m.get('params') or {}
        if method=='initialize':
            pv=params.get('protocolVersion',PROTOCOL_VERSION)
            return server.result(mid,{"protocolVersion":PROTOCOL_VERSION if pv!=PROTOCOL_VERSION else pv,"capabilities":{"tools":{"listChanged":False},"resources":{"listChanged":False},"prompts":{"listChanged":False}},"serverInfo":SERVER_INFO})
        if method in ('notifications/initialized','notifications/cancelled'): return None
        if method=='ping': return server.result(mid,{})
        if method=='tools/list': return server.result(mid,{"tools":sorted(TOOLS,key=lambda x:x['name'])})
        if method=='tools/call':
            name=params.get('name'); args=params.get('arguments') or {}
            if not server.rate.allow(name): return server.result(mid,{"content":[{"type":"text","text":"Rate limit exceeded; retry later."}],"isError":True})
            try:
                td=next((t for t in TOOLS if t['name']==name),None)
                if td is None: raise KeyError(name)
                validate(td['inputSchema'],args)
                value=server.call_tool(name,args)
                return server.result(mid,{"content":[{"type":"text","text":json.dumps(value,ensure_ascii=False,sort_keys=True)}],"structuredContent":value,"isError":False})
            except (StaleTarget, GitStaleHead) as e:
                return server.result(mid,{"content":[{"type":"text","text":str(e)}],"structuredContent":{"status":"STALE_TARGET","detail":str(e)},"isError":True})
            except (ValueError,KeyError) as e:
                return server.result(mid,{"content":[{"type":"text","text":str(e)}],"isError":True})
            except Exception as e:
                print(f"tool error {name}: {e}",file=sys.stderr); return server.error(mid,-32603,"Internal error")
        if method=='resources/list':
            rs=[
                {"uri":"athena://manifest","name":"ATHENA Canonical Manifest","mimeType":"application/json"},
                {"uri":"athena://kc144/stations","name":"KC144 12x12 Station Registry","mimeType":"application/json"},
                {"uri":"athena://state/head","name":"Canonical State Head","mimeType":"application/json"},
                {"uri":"athena://registry","name":"Canonical Capability Registry","mimeType":"application/json"},
                {"uri":"athena://jspace","name":"JSPACE Graph","mimeType":"application/json"},
                {"uri":"athena://scale","name":"SCALE Representation Ladder","mimeType":"application/json"},
            ]; return server.result(mid,{"resources":rs})
        if method=='resources/read':
            uri=params.get('uri'); c=server.core
            if uri=='athena://manifest': val={"name":"ATHENA","protocol":PROTOCOL_VERSION,"layers":["GIT_LEDGER","CCR","JSPACE","SCALE","KC144","RUNTIME"],"identity":"SID!=OID!=MID!=VID","mutation":"EXPECTED_VID==CURRENT_VID else STALE_TARGET"}
            elif uri=='athena://kc144/stations': val=json.loads(station_manifest())
            elif uri=='athena://state/head': val=c.s.head('global') or {}
            elif uri=='athena://registry': val=c.s.rows("SELECT * FROM objects ORDER BY canonical_name")
            elif uri=='athena://jspace': val={"edges":c.s.rows("SELECT * FROM edges ORDER BY created_at DESC LIMIT 1000")}
            elif uri=='athena://scale': val={"levels":{"S0":"RAW_EVENT","S1":"STATE_DELTA","S2":"RELATION_DELTA","S3":"MOTIF","S4":"GENERATOR","S5":"ORGAN_NATIVE_LAW"}}
            else:return server.error(mid,-32002,"Resource not found",{"uri":uri})
            return server.result(mid,{"contents":[{"uri":uri,"mimeType":"application/json","text":json.dumps(val,ensure_ascii=False,sort_keys=True)}]})
        if method=='prompts/list': return server.result(mid,{"prompts":PROMPTS})
        if method=='prompts/get':
            if params.get('name')!='athena_maxdev': return server.error(mid,-32602,"Unknown prompt")
            a=params.get('arguments') or {}; task=a.get('task',''); agent=a.get('agent','ATHENA')
            text=f"""ATHENA MAXDEV CYCLE\nAGENT={agent}\nTASK={task}\n1 PULL/HYDRATE current canonical state.\n2 Reconstruct JSPACE/SCALE/KC144 and pending global mutations.\n3 Compute current CUT residual against the authorized attractor.\n4 Execute maximum reachable useful development now; do not reserve work for later.\n5 Use self-play/harnesses internally; compile repeated cognition into tools.\n6 Every consequential object must receive canonical identity, version, graph edges, KC144 coordinate, native locator and RETURN.\n7 Commit only conditionally against current VID; stale targets HOLD/rebase/fork.\n8 Emit public liminal telemetry, not private chain-of-thought.\n9 Promote organism-wide prompt/harness/tool/SCALE laws as global mutations.\n10 Recompute and continue.\n"""
            return server.result(mid,{"description":"Whole-system MAXDEV cycle","messages":[{"role":"user","content":{"type":"text","text":text}}]})
        return server.error(mid,-32601,"Method not found")

