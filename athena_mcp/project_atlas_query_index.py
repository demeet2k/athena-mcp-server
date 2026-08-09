from __future__ import annotations

from collections import defaultdict
from pathlib import PurePosixPath

from .identity import digest

INDEX_VERSION="ATHENA.PROJECT_ATLAS.QUERY_INDEX.V2"


def typed_mcp_identifier(identifier: str):
    ident=str(identifier)
    for prefix,kind in (("mcp:tool:","tool"),("mcp:prompt:","prompt"),("tool:","tool"),("prompt:","prompt")):
        if ident.startswith(prefix) and len(ident)>len(prefix):return kind,ident[len(prefix):]
    return None


def _entry_sort_key(entry):
    source,rec=entry;native=rec["native"]
    return (source,str(native.get("repo") or ""),str(native.get("head") or ""),str(native.get("path") or ""),str(rec.get("poid") or ""))


def _dedup(entries):
    unique={}
    for source,rec in entries:
        unique[(source,rec["poid"],rec["native"].get("head"))]=(source,rec)
    return sorted(unique.values(),key=_entry_sort_key)


def _identity(entry):
    source,rec=entry;native=rec["native"]
    return {
        "source":source,
        "poid":rec["poid"],
        "version_fiber":rec.get("version_fiber"),
        "repo":native.get("repo"),
        "head":native.get("head"),
        "path":native.get("path"),
        "git_type":native.get("git_type"),
    }


def _freeze_map(mapping):
    return {str(k):[_identity(e) for e in sorted(v,key=_entry_sort_key)] for k,v in sorted(mapping.items(),key=lambda kv:str(kv[0]))}


def build_query_index(entries):
    entries=_dedup(list(entries))
    maps={name:defaultdict(list) for name in (
        "by_source","by_poid","by_address","by_return","by_path","by_raw_mcp_name","by_typed_mcp",
        "by_project_gid","by_reference_gid","by_directory","by_blob",
    )}
    for entry in entries:
        source,rec=entry;native=rec["native"]
        maps["by_source"][source].append(entry)
        maps["by_poid"][rec["poid"]].append(entry)
        maps["by_address"][rec["address"]].append(entry)
        uri=rec.get("return",{}).get("uri")
        if uri:maps["by_return"][uri].append(entry)
        path=native.get("path")
        if path is not None:maps["by_path"][path].append(entry)
        maps["by_project_gid"][int(rec["project_kc144"]["gid"])].append(entry)
        maps["by_reference_gid"][int(rec["kc144_reference"]["gid"])].append(entry)
        parent=str(PurePosixPath(path).parent) if path else ""
        if parent==".":parent=""
        maps["by_directory"][parent].append(entry)
        blob=native.get("object_sha")
        if blob:maps["by_blob"][blob].append(entry)
        mcp=rec.get("mcp")
        if mcp:
            name=mcp.get("name");kind=mcp.get("kind")
            if name:
                maps["by_raw_mcp_name"][name].append(entry)
                maps["by_typed_mcp"][f"{kind}:{name}"].append(entry)

    frozen={name:_freeze_map(mapping) for name,mapping in maps.items()}
    index_digest=digest({"version":INDEX_VERSION,"maps":frozen},32)
    return {
        "version":INDEX_VERSION,
        "entries":entries,
        **{name:{k:_dedup(v) for k,v in mapping.items()} for name,mapping in maps.items()},
        "digest":index_digest,
        "counts":{
            "records":len(entries),
            "sources":len(maps["by_source"]),
            "poids":len(maps["by_poid"]),
            "addresses":len(maps["by_address"]),
            "returns":len(maps["by_return"]),
            "paths":len(maps["by_path"]),
            "typed_mcp":len(maps["by_typed_mcp"]),
            "project_stations":len(maps["by_project_gid"]),
            "reference_stations":len(maps["by_reference_gid"]),
            "directories":len(maps["by_directory"]),
            "blobs":len(maps["by_blob"]),
        },
    }


def lookup_identifier(index,identifier: str):
    ident=str(identifier)
    typed=typed_mcp_identifier(ident)
    if typed:
        kind,name=typed
        return list(index["by_typed_mcp"].get(f"{kind}:{name}",[])),"TYPED_MCP"
    if ident.startswith("POID."):
        return list(index["by_poid"].get(ident,[])),"POID"
    if ident.startswith("PROJECT_KC144."):
        return list(index["by_address"].get(ident,[])),"PROJECT_ADDRESS"
    if ident.startswith("athena+git://") or ident.startswith("athena+mcp://"):
        return list(index["by_return"].get(ident,[])),"RETURN_URI"
    convenience=ident[2:] if ident.startswith("./") else ident
    rows=[]
    rows.extend(index["by_path"].get(convenience,[]))
    rows.extend(index["by_raw_mcp_name"].get(ident,[]))
    return _dedup(rows),"OPEN_WORLD"


def seed_list_candidates(index,args: dict,runtime_is_configured: bool):
    source=args.get("source","all")
    if source=="configured_git":return list(index["by_source"].get("configured_git",[])),"source"
    if source=="runtime_git":
        if runtime_is_configured:return list(index["by_source"].get("configured_git",[])),"source"
        return list(index["by_source"].get("runtime_git",[])),"source"
    if source=="mcp":return list(index["by_source"].get("mcp",[])),"source"
    if source=="git":
        rows=list(index["by_source"].get("configured_git",[]))
        if not runtime_is_configured:rows.extend(index["by_source"].get("runtime_git",[]))
        return _dedup(rows),"source"
    if args.get("project_gid") is not None:return list(index["by_project_gid"].get(int(args["project_gid"]),[])),"project_gid"
    if args.get("reference_gid") is not None:return list(index["by_reference_gid"].get(int(args["reference_gid"]),[])),"reference_gid"
    if args.get("directory") is not None:
        directory=args.get("directory")
        if directory==".":directory=""
        elif directory and directory.startswith("./"):directory=directory[2:]
        return list(index["by_directory"].get(directory,[])),"directory"
    return list(index["entries"]),"all"
