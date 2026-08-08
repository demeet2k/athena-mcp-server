from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping

COMPOSITION_VERSION="ATHENA.COMPOSITION.1"

EXPECTED_MRO=(
    "FieldServer","StackServer","GapServer","HugServer","RetrievalServer",
    "DevelopmentServer","AuthorityServer","Server",
)

REQUIRED_ORGANS={
    "base":("core","crystal","git"),
    "aor":("orchestration",),
    "branch":("branches",),
    "authority":("authority",),
    "development":("equivalence","extraction"),
    "retrieval":("retrieval",),
    "hug":("hug",),
    "gap":("gap",),
    "field":("field",),
}

READ_ONLY_PROBES={
    "branch":("athena_branch_list",{}),
    "authority":("athena_claim_list",{}),
    "retrieval":("athena_retrieval_recent",{}),
    "hug":("athena_hug_list",{}),
    "gap":("athena_gap_recent",{}),
    "field":("athena_field_recent",{}),
}


def _is_subsequence(expected: Iterable[str], observed: Iterable[str]) -> bool:
    iterator=iter(observed)
    return all(any(actual==wanted for actual in iterator) for wanted in expected)


def _probe(server, name: str, args: Mapping[str,Any], seq: int):
    response=server.handle({"jsonrpc":"2.0","id":f"composition:{seq}","method":"tools/call","params":{"name":name,"arguments":dict(args)}})
    result=(response or {}).get("result")
    if not isinstance(result,dict):
        return {"status":"FAIL","reason":"missing MCP result envelope","response":response}
    if result.get("isError"):
        return {"status":"FAIL","reason":"read-only probe returned tool error","detail":result.get("content")}
    return {"status":"PASS"}


def composition_certificate(server, run_probes: bool=True) -> Dict[str,Any]:
    mro=[cls.__name__ for cls in server.__class__.mro()]
    mro_pass=_is_subsequence(EXPECTED_MRO,mro)

    organs={}
    missing=[]
    for group,names in REQUIRED_ORGANS.items():
        absent=[name for name in names if not hasattr(server,name) or getattr(server,name) is None]
        organs[group]={"status":"PASS" if not absent else "FAIL","required":list(names),"missing":absent}
        missing.extend(f"{group}:{name}" for name in absent)

    probes={}
    if run_probes:
        for seq,(group,(name,args)) in enumerate(READ_ONLY_PROBES.items(),1):
            probes[group]={"tool":name,**_probe(server,name,args,seq)}
    probe_pass=all(packet.get("status")=="PASS" for packet in probes.values()) if run_probes else None

    status="PASS" if mro_pass and not missing and (probe_pass is not False) else "FAIL"
    return {
        "version":COMPOSITION_VERSION,
        "status":status,
        "mro":{"status":"PASS" if mro_pass else "FAIL","expected_subsequence":list(EXPECTED_MRO),"observed":mro},
        "organs":organs,
        "missing_organs":sorted(missing),
        "read_only_probes":probes,
        "probe_status":"PASS" if probe_pass else ("FAIL" if probe_pass is False else "NOT_RUN"),
        "law":"composition integrity requires expected inheritance geometry, initialized mature organ instances, and successful representative read-only execution paths",
        "boundary":"this certifies runtime composition/dispatch reachability, not semantic correctness of every organ",
    }
