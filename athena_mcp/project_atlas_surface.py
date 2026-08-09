from __future__ import annotations

from pathlib import Path, PurePosixPath

from .identity import digest
from .project_atlas import compile_git_atlas, federate_atlases, mcp_surface_atlas, route_records
from .project_atlas_protocol import PROJECT_ATLAS_RESOURCE, PROJECT_ATLAS_TOOL_NAMES
from .project_atlas_runtime_provenance import runtime_frontier, same_runtime_frontier

PROJECT_ATLAS_SURFACE_VERSION="ATHENA.PROJECT_ATLAS.MCP_SURFACE.V2"
PROJECT_ATLAS_MAX_PAGE=100
PROJECT_ATLAS_LAWS=[
    "KC144_STATION != OBJECT_IDENTITY",
    "POID != OID != MID != VID",
    "CONFIGURED_GIT_HEAD != RUNTIME_GIT_HEAD",
    "PACKAGE_VERSION != RUNTIME_SOURCE_HEAD",
    "MCP_VIRTUAL_OBJECT != GIT_BLOB",
    "MCP_DEFINITION_COORDINATE_REQUIRES_RUNTIME_SOURCE_HEAD",
    "UNKNOWN_RUNTIME_TREE != EMPTY_RUNTIME_TREE",
    "PROJECT_ATLAS_SNAPSHOT_ID != PROMOTION_RECEIPT",
    "PROJECT_QUERY != PROMOTION_AUTHORITY",
    "PROJECT_ROUTE != SEMANTIC_EQUIVALENCE",
    "AMBIGUOUS_RESOLVE -> HOLD",
    "HEAD_CHANGE -> RECOMPILE_BEFORE_CONSEQUENTIAL_ROUTE",
    "RUNTIME_HEAD_CHANGE -> RECOMPILE_BEFORE_QUERY",
    "MCP_SURFACE_CHANGE -> RECOMPILE_BEFORE_QUERY",
    "CROSS_REPO_ROUTE_REQUIRES_EXACT_REPO_HEAD",
    "PROJECT_QUERY != PERSISTENT_STATE_MUTATION",
]


class ProjectAtlasSurface:
    """Read-only federated query projection over the V1 Project Atlas."""

    def __init__(self, server):
        self.server=server
        self._cache_key=None
        self._cache_head=None
        self._cache_runtime_head=None
        self._cache_surface_signature=None
        self._cache_snapshot_id=None
        self._cache=None

    def _hold(self, status: str, **extra):
        return {
            "status":status,
            "surface_version":PROJECT_ATLAS_SURFACE_VERSION,
            "authority":"NONE",
            "laws":list(PROJECT_ATLAS_LAWS),
            **extra,
        }

    @staticmethod
    def _surface_signature():
        from .protocol import PROMPTS, TOOLS
        return digest({"tools":TOOLS,"prompts":PROMPTS},32)

    @staticmethod
    def _runtime_key(frontier: dict):
        return tuple(frontier.get(k) for k in ("status","mode","repo_key","head","root","attestation_level"))

    def _invalidate_cache(self):
        self._cache_key=None
        self._cache_head=None
        self._cache_runtime_head=None
        self._cache_surface_signature=None
        self._cache_snapshot_id=None
        self._cache=None

    @staticmethod
    def _snapshot_identity(configured_atlas: dict, runtime_atlas: dict | None, runtime_provenance: dict, mcp_surface: dict, federation: dict, surface_signature: str):
        configured_repo=configured_atlas["repository"]
        runtime_repo=runtime_atlas["repository"] if runtime_atlas is not None else None
        basis={
            "schema":"ATHENA.KC144.FEDERATED_RUNTIME_PROJECT_ATLAS.V2",
            "configured":{
                "repo":configured_repo["repo_key"],"head":configured_repo["head"],"tree":configured_repo["tree"],
                "atlas_digest":configured_atlas["atlas_digest"],
            },
            "runtime_provenance":{k:runtime_provenance.get(k) for k in ("status","mode","repo_key","head","attestation_level")},
            "runtime_git":None if runtime_repo is None else {
                "repo":runtime_repo["repo_key"],"head":runtime_repo["head"],"tree":runtime_repo["tree"],"atlas_digest":runtime_atlas["atlas_digest"],
            },
            "mcp":{"head":mcp_surface.get("head"),"repo":mcp_surface.get("repo_key"),"surface_digest":mcp_surface.get("surface_digest")},
            "live_surface_signature":surface_signature,
            "federation_digest":federation.get("federation_digest"),
        }
        return "PATLASV2."+digest(basis,32),basis

    def _compile_snapshot(self, configured_head: str, runtime_before: dict, surface_signature: str) -> dict:
        configured_atlas=compile_git_atlas(self.server.git.root,ref=configured_head,include_trees=True)
        runtime_atlas=None
        runtime_is_configured=False

        if runtime_before.get("status")=="RESOLVED":
            runtime_head=runtime_before["head"]
            runtime_repo=runtime_before["repo_key"]
            runtime_root=runtime_before.get("root")
            if runtime_root:
                root=Path(runtime_root).resolve()
                if root==Path(self.server.git.root).resolve() and runtime_head==configured_head:
                    runtime_atlas=configured_atlas;runtime_is_configured=True
                else:
                    runtime_atlas=compile_git_atlas(root,ref=runtime_head,include_trees=True)
                runtime_repo=runtime_atlas["repository"]["repo_key"]
                runtime_head=runtime_atlas["repository"]["head"]
            from .protocol import PROMPTS, SERVER_INFO, TOOLS
            mcp_surface=mcp_surface_atlas(
                repo_key=runtime_repo,head=runtime_head,server_name=SERVER_INFO.get("name","athena-canonical-mcp"),tools=TOOLS,prompts=PROMPTS,
            )
        else:
            mcp_surface={
                "schema":"ATHENA.KC144.MCP_SURFACE_ATLAS.v1","status":"HOLD_RUNTIME_PROVENANCE","reason":runtime_before.get("reason"),
                "repo_key":runtime_before.get("repo_key"),"head":runtime_before.get("head"),"server":None,"count":0,"records":[],"surface_digest":None,
            }

        git_atlases=[configured_atlas]
        if runtime_atlas is not None and not runtime_is_configured:git_atlases.append(runtime_atlas)
        surfaces=[mcp_surface] if mcp_surface.get("status")!="HOLD_RUNTIME_PROVENANCE" else []
        federation=federate_atlases(git_atlases,surfaces)
        snapshot_id,snapshot_basis=self._snapshot_identity(configured_atlas,runtime_atlas,runtime_before,mcp_surface,federation,surface_signature)
        if runtime_before.get("status")!="RESOLVED":standing="PARTIAL_RUNTIME_PROVENANCE_HOLD"
        elif runtime_atlas is None:standing="PARTIAL_RUNTIME_TREE_UNAVAILABLE"
        else:standing="GENERATED"
        return {
            "schema":"ATHENA.KC144.FEDERATED_RUNTIME_PROJECT_ATLAS.V2","status":standing,
            "snapshot_id":snapshot_id,"snapshot_basis":snapshot_basis,
            "configured_git":configured_atlas,"runtime_git":runtime_atlas,"runtime_git_is_configured":runtime_is_configured,
            "runtime_provenance":dict(runtime_before),"runtime_tree_available":runtime_atlas is not None,
            "mcp_surface":mcp_surface,"federation":federation,"surface_signature":surface_signature,
        }

    def _snapshot(self, expected_head=None, expected_runtime_head=None):
        git=getattr(self.server,"git",None)
        if git is None or not git.enabled:
            return None,self._hold("HOLD_GIT_UNAVAILABLE",reason="Project Atlas query surface requires a configured ATHENA_GIT_ROOT checkout.",configured_head=None,runtime_head=None),None

        expected=str(expected_head).lower().strip() if expected_head else None
        expected_runtime=str(expected_runtime_head).lower().strip() if expected_runtime_head else None
        for _ in range(2):
            configured_before=git.status();configured_head=configured_before["head"];runtime_before=runtime_frontier();surface_signature=self._surface_signature()
            if expected is not None and configured_head!=expected:
                return None,self._hold(
                    "HOLD_STALE_CONFIGURED_HEAD",expected_head=expected,current_head=configured_head,current_runtime_head=runtime_before.get("head"),
                    configured_head=configured_head,runtime_head=runtime_before.get("head"),reason="Expected configured Git head does not match ATHENA_GIT_ROOT.",
                ),configured_before
            if expected_runtime is not None:
                if runtime_before.get("status")!="RESOLVED":
                    return None,self._hold(
                        "HOLD_RUNTIME_PROVENANCE",expected_runtime_head=expected_runtime,configured_head=configured_head,runtime_head=runtime_before.get("head"),
                        runtime_provenance=runtime_before,reason="Cannot validate expected runtime head without exact runtime-source provenance.",
                    ),configured_before
                if runtime_before.get("head")!=expected_runtime:
                    return None,self._hold(
                        "HOLD_STALE_RUNTIME_HEAD",expected_runtime_head=expected_runtime,current_runtime_head=runtime_before.get("head"),
                        configured_head=configured_head,runtime_head=runtime_before.get("head"),runtime_provenance=runtime_before,
                    ),configured_before

            cache_key=(configured_head,self._runtime_key(runtime_before),surface_signature)
            if self._cache_key==cache_key and self._cache is not None:snapshot=self._cache
            else:
                snapshot=self._compile_snapshot(configured_head,runtime_before,surface_signature)
                if snapshot["configured_git"]["repository"]["head"]!=configured_head:self._invalidate_cache();continue
                runtime_atlas=snapshot.get("runtime_git")
                if runtime_atlas is not None:
                    if runtime_atlas["repository"]["head"]!=runtime_before.get("head"):self._invalidate_cache();continue
                    if runtime_atlas["repository"]["repo_key"]!=runtime_before.get("repo_key"):self._invalidate_cache();continue

            configured_after=git.status();runtime_after=runtime_frontier();after_signature=self._surface_signature()
            stable=(configured_after["head"]==configured_head==snapshot["configured_git"]["repository"]["head"] and same_runtime_frontier(runtime_before,runtime_after) and after_signature==surface_signature)
            if stable:
                self._cache_key=cache_key;self._cache_head=configured_head;self._cache_runtime_head=runtime_before.get("head")
                self._cache_surface_signature=surface_signature;self._cache_snapshot_id=snapshot["snapshot_id"];self._cache=snapshot
                observation={
                    "configured_git":{"branch":configured_after.get("branch"),"head":configured_head,"dirty":bool(configured_after.get("dirty"))},
                    "runtime_source":dict(runtime_after),"mcp_surface_signature":surface_signature,
                }
                return snapshot,None,observation
            self._invalidate_cache()

        current=git.status();runtime_current=runtime_frontier();current_signature=self._surface_signature()
        return None,self._hold(
            "HOLD_VOLATILE_FRONTIER",current_head=current.get("head"),current_runtime_head=runtime_current.get("head"),current_surface_signature=current_signature,
            configured_head=current.get("head"),runtime_head=runtime_current.get("head"),runtime_provenance=runtime_current,
            reason="Configured Git, runtime-source Git, or the live MCP surface moved while compiling the federated Project Atlas.",
        ),current

    @staticmethod
    def _summary_record(source: str, rec: dict) -> dict:
        native=dict(rec["native"]);project=rec["project_kc144"];reference=rec["kc144_reference"]
        out={
            "source":source,"poid":rec["poid"],"address":rec["address"],
            "native":{"repo":native.get("repo"),"ref":native.get("ref"),"head":native.get("head"),"tree":native.get("tree"),"path":native.get("path"),"object_sha":native.get("object_sha"),"git_type":native.get("git_type"),"mode":native.get("mode")},
            "project_kc144":{"gid":project["gid"],"sid":project["sid"],"row":project["row"],"col":project["col"],"row_semantic":project.get("row_semantic"),"col_semantic":project.get("col_semantic")},
            "kc144_reference":{"gid":reference["gid"],"sid":reference["sid"],"row":reference["row"],"col":reference["col"]},
            "return":rec["return"],
        }
        if rec.get("mcp") is not None:out["mcp"]=dict(rec["mcp"])
        if rec.get("navigation") is not None:
            out["navigation"]={"parent_path":rec["navigation"].get("parent_path"),"station_ordinal":rec["navigation"].get("station_ordinal"),"station_population":rec["navigation"].get("station_population")}
        return out

    @staticmethod
    def _all_records(snapshot: dict):
        rows=[("configured_git",r) for r in snapshot.get("configured_git",{}).get("records",[])]
        runtime=snapshot.get("runtime_git")
        if runtime is not None and not snapshot.get("runtime_git_is_configured"):rows.extend(("runtime_git",r) for r in runtime.get("records",[]))
        rows.extend(("mcp",r) for r in snapshot.get("mcp_surface",{}).get("records",[]))
        return rows

    @staticmethod
    def _typed_mcp_identifier(identifier: str):
        ident=str(identifier)
        for prefix,kind in (("mcp:tool:","tool"),("mcp:prompt:","prompt"),("tool:","tool"),("prompt:","prompt")):
            if ident.startswith(prefix) and len(ident)>len(prefix):return kind,ident[len(prefix):]
        return None

    @staticmethod
    def _strong_identifier(identifier: str, source: str, rec: dict) -> bool:
        ident=str(identifier)
        if ident in {rec.get("poid"),rec.get("address"),rec.get("return",{}).get("uri")}:return True
        typed=ProjectAtlasSurface._typed_mcp_identifier(ident);mcp=rec.get("mcp")
        if source=="mcp" and typed and mcp:return typed==(mcp.get("kind"),mcp.get("name"))
        return False

    def _resolve_in_snapshot(self, snapshot: dict, identifier: str) -> dict:
        ident=str(identifier);typed=self._typed_mcp_identifier(ident);matches=[]
        if typed:
            kind,name=typed
            for rec in snapshot.get("mcp_surface",{}).get("records",[]):
                mcp=rec.get("mcp") or {}
                if mcp.get("kind")==kind and mcp.get("name")==name:matches.append(("mcp",rec))
        else:
            convenience=ident[2:] if ident.startswith("./") else ident
            for source,rec in self._all_records(snapshot):
                native=rec["native"]
                aliases={rec["poid"],rec["address"],native.get("path"),rec.get("return",{}).get("uri")}
                mcp=rec.get("mcp")
                if mcp:aliases.add(mcp.get("name"))
                if ident in aliases or (source.endswith("_git") and convenience==native.get("path")):matches.append((source,rec))
        matches=list({(source,rec["poid"]):(source,rec) for source,rec in matches}.values())
        configured_head=snapshot["configured_git"]["repository"]["head"];runtime_head=snapshot.get("runtime_provenance",{}).get("head")
        runtime_status=snapshot.get("runtime_provenance",{}).get("status");tree_available=bool(snapshot.get("runtime_tree_available"));snapshot_id=snapshot["snapshot_id"]
        if not matches:
            if runtime_status!="RESOLVED":
                return self._hold(
                    "HOLD_RUNTIME_PROVENANCE",identifier=ident,snapshot_id=snapshot_id,configured_head=configured_head,runtime_head=runtime_head,
                    runtime_provenance=snapshot.get("runtime_provenance"),reason="Identifier was not found in configured Git, but runtime/MCP provenance is incomplete.",
                )
            if not tree_available and not typed:
                return self._hold(
                    "HOLD_RUNTIME_TREE_UNAVAILABLE",identifier=ident,snapshot_id=snapshot_id,configured_head=configured_head,runtime_head=runtime_head,
                    runtime_provenance=snapshot.get("runtime_provenance"),reason="Runtime head is known but its Git tree is not enumerated; UNKNOWN_RUNTIME_TREE != EMPTY_RUNTIME_TREE.",
                )
            return self._hold("HOLD_NOT_FOUND",identifier=ident,snapshot_id=snapshot_id,configured_head=configured_head,runtime_head=runtime_head,candidates=[])
        if len(matches)>1:
            return self._hold(
                "HOLD_AMBIGUOUS",identifier=ident,snapshot_id=snapshot_id,configured_head=configured_head,runtime_head=runtime_head,
                candidate_count=len(matches),candidates=[self._summary_record(source,rec) for source,rec in matches[:20]],
            )
        source,rec=matches[0]
        if runtime_status=="RESOLVED" and not tree_available and not self._strong_identifier(ident,source,rec):
            return self._hold(
                "HOLD_RUNTIME_TREE_UNAVAILABLE",identifier=ident,snapshot_id=snapshot_id,configured_head=configured_head,runtime_head=runtime_head,
                candidate=self._summary_record(source,rec),runtime_provenance=snapshot.get("runtime_provenance"),
                reason="One visible candidate exists, but an unenumerated runtime Git tree could contain an equal unscoped identifier; use a POID/address/native RETURN or typed MCP locator.",
            )
        return {
            "status":"RESOLVED","surface_version":PROJECT_ATLAS_SURFACE_VERSION,"authority":"NONE","snapshot_id":snapshot_id,
            "configured_head":configured_head,"runtime_head":runtime_head,"runtime_provenance":snapshot.get("runtime_provenance"),
            "identifier":ident,"record":self._summary_record(source,rec),"full_record":rec,"laws":list(PROJECT_ATLAS_LAWS),
        }

    @staticmethod
    def _bounded_git_summary(atlas: dict | None):
        if atlas is None:return None
        repo=atlas["repository"]
        return {"repo_key":repo["repo_key"],"ref":repo["ref"],"head":repo["head"],"tree":repo["tree"],"atlas_digest":atlas["atlas_digest"],"counts":atlas["counts"]}

    def summary(self, args=None):
        args=args or {};snapshot,hold,observation=self._snapshot(args.get("expected_head"),args.get("expected_runtime_head"))
        if hold:return hold
        configured=snapshot["configured_git"];runtime=snapshot.get("runtime_git");mcp=snapshot.get("mcp_surface",{});federation=snapshot.get("federation",{});rp=snapshot.get("runtime_provenance",{})
        if rp.get("status")!="RESOLVED":standing="PARTIAL_RUNTIME_PROVENANCE_HOLD"
        elif runtime is None:standing="PARTIAL_RUNTIME_TREE_UNAVAILABLE"
        else:standing="PASS"
        return {
            "status":standing,"surface_version":PROJECT_ATLAS_SURFACE_VERSION,"authority":"NONE","snapshot_id":snapshot["snapshot_id"],
            "configured_head":configured["repository"]["head"],"runtime_head":rp.get("head"),
            "repository":self._bounded_git_summary(configured),"configured_git":self._bounded_git_summary(configured),"runtime_git":self._bounded_git_summary(runtime),
            "runtime_tree_available":runtime is not None,"runtime_git_is_configured":bool(snapshot.get("runtime_git_is_configured")),"runtime_provenance":rp,
            "mcp_surface":{"status":mcp.get("status","RESOLVED"),"repo_key":mcp.get("repo_key"),"head":mcp.get("head"),"server":mcp.get("server"),"count":mcp.get("count",0),"surface_digest":mcp.get("surface_digest"),"live_signature":snapshot.get("surface_signature")},
            "federation":{"count":federation.get("count",0),"federation_digest":federation.get("federation_digest"),"roots":federation.get("roots",[])},
            "completeness":{"configured_git":"COMPLETE","runtime_git":"COMPLETE" if runtime is not None else "UNKNOWN","mcp_surface":"COMPLETE" if mcp.get("status")!="HOLD_RUNTIME_PROVENANCE" else "UNKNOWN"},
            "checkout_observation":observation,"pagination":{"default_limit":50,"max_limit":PROJECT_ATLAS_MAX_PAGE},"laws":list(PROJECT_ATLAS_LAWS),
        }

    def resolve(self, args: dict):
        snapshot,hold,_=self._snapshot(args.get("expected_head"),args.get("expected_runtime_head"))
        if hold:return hold
        result=self._resolve_in_snapshot(snapshot,args["identifier"])
        if result.get("status")=="RESOLVED":result.pop("full_record",None)
        return result

    @staticmethod
    def _source_selected(source_filter: str, source: str, runtime_is_configured: bool):
        if source_filter=="all":return True
        if source_filter=="git":return source in {"configured_git","runtime_git"}
        if source_filter==source:return True
        if source_filter=="runtime_git" and runtime_is_configured and source=="configured_git":return True
        return False

    def list_records(self, args: dict):
        snapshot,hold,_=self._snapshot(args.get("expected_head"),args.get("expected_runtime_head"))
        if hold:return hold
        source_filter=args.get("source","all");rp=snapshot.get("runtime_provenance",{});snapshot_id=snapshot["snapshot_id"]
        if source_filter in {"runtime_git","mcp"} and rp.get("status")!="RESOLVED":
            return self._hold("HOLD_RUNTIME_PROVENANCE",snapshot_id=snapshot_id,configured_head=snapshot["configured_git"]["repository"]["head"],runtime_head=None,runtime_provenance=rp,reason=f"source={source_filter} requires exact runtime-source provenance")
        if source_filter=="runtime_git" and snapshot.get("runtime_git") is None:
            return self._hold("HOLD_RUNTIME_TREE_UNAVAILABLE",snapshot_id=snapshot_id,configured_head=snapshot["configured_git"]["repository"]["head"],runtime_head=rp.get("head"),runtime_provenance=rp,reason="Runtime repository/head is known but the runtime Git tree is not available for enumeration.")
        prefix=args.get("path_prefix");prefix=prefix[2:] if prefix and prefix.startswith("./") else prefix
        directory=args.get("directory")
        if directory==".":directory=""
        elif directory and directory.startswith("./"):directory=directory[2:]
        poid_prefix=args.get("poid_prefix");rows=[]
        for source,rec in self._all_records(snapshot):
            if not self._source_selected(source_filter,source,bool(snapshot.get("runtime_git_is_configured"))):continue
            native=rec["native"];project=rec["project_kc144"];reference=rec["kc144_reference"]
            if prefix is not None and not native["path"].startswith(prefix):continue
            if args.get("git_type") is not None and native["git_type"]!=args["git_type"]:continue
            if args.get("project_gid") is not None and project["gid"]!=int(args["project_gid"]):continue
            if args.get("project_row") is not None and project["row"]!=int(args["project_row"]):continue
            if args.get("project_col") is not None and project["col"]!=int(args["project_col"]):continue
            if args.get("reference_gid") is not None and reference["gid"]!=int(args["reference_gid"]):continue
            parent=str(PurePosixPath(native["path"]).parent);parent="" if parent=="." else parent
            if directory is not None and parent!=directory:continue
            mcp=rec.get("mcp")
            if args.get("mcp_kind") is not None and (not mcp or mcp.get("kind")!=args["mcp_kind"]):continue
            if poid_prefix is not None and not rec["poid"].startswith(poid_prefix):continue
            rows.append((source,rec))
        rows.sort(key=lambda x:(x[0],x[1]["native"]["repo"],x[1]["native"]["path"],x[1]["native"]["git_type"],x[1]["poid"]))
        total=len(rows);offset=int(args.get("offset",0));limit=min(PROJECT_ATLAS_MAX_PAGE,int(args.get("limit",50)));page=rows[offset:offset+limit];next_offset=offset+len(page);next_offset=None if next_offset>=total else next_offset
        standing="PASS"
        if source_filter in {"all","git"} and rp.get("status")=="RESOLVED" and snapshot.get("runtime_git") is None:standing="PARTIAL_RUNTIME_TREE_UNAVAILABLE"
        elif source_filter in {"all","git"} and rp.get("status")!="RESOLVED":standing="PARTIAL_RUNTIME_PROVENANCE_HOLD"
        return {
            "status":standing,"surface_version":PROJECT_ATLAS_SURFACE_VERSION,"authority":"NONE","snapshot_id":snapshot_id,
            "configured_head":snapshot["configured_git"]["repository"]["head"],"runtime_head":rp.get("head"),"runtime_provenance":rp,
            "total":total,"offset":offset,"limit":limit,"next_offset":next_offset,"items":[self._summary_record(source,rec) for source,rec in page],
            "filters":{k:v for k,v in args.items() if k not in {"expected_head","expected_runtime_head","offset","limit"} and v is not None},"laws":list(PROJECT_ATLAS_LAWS),
        }

    def route(self, args: dict):
        snapshot,hold,_=self._snapshot(args.get("expected_head"),args.get("expected_runtime_head"))
        if hold:return hold
        snapshot_id=snapshot["snapshot_id"];rp=snapshot.get("runtime_provenance",{})
        src=self._resolve_in_snapshot(snapshot,args["src"])
        if src.get("status")!="RESOLVED":return self._hold("HOLD_ROUTE_SOURCE",snapshot_id=snapshot_id,configured_head=snapshot["configured_git"]["repository"]["head"],runtime_head=rp.get("head"),source_resolution=src)
        dst=self._resolve_in_snapshot(snapshot,args["dst"])
        if dst.get("status")!="RESOLVED":return self._hold("HOLD_ROUTE_DESTINATION",snapshot_id=snapshot_id,configured_head=snapshot["configured_git"]["repository"]["head"],runtime_head=rp.get("head"),destination_resolution=dst)
        route=route_records(src["full_record"],dst["full_record"],wrap=bool(args.get("wrap",False)))
        s_native=src["full_record"]["native"];d_native=dst["full_record"]["native"];same_repo=s_native.get("repo")==d_native.get("repo");same_head=s_native.get("head")==d_native.get("head")
        route["cross_repository"]=not same_repo;route["cross_version"]=same_repo and not same_head;route["cross_frontier"]=not (same_repo and same_head)
        if route["cross_frontier"]:
            route["federation_transition"]={
                "federation_digest":snapshot.get("federation",{}).get("federation_digest"),
                "src":{"repo":s_native.get("repo"),"head":s_native.get("head")},"dst":{"repo":d_native.get("repo"),"head":d_native.get("head")},
                "law":"CROSS_REPO_ROUTE_REQUIRES_EXACT_REPO_HEAD",
            }
        return {
            "status":"ROUTED","surface_version":PROJECT_ATLAS_SURFACE_VERSION,"authority":"NONE","snapshot_id":snapshot_id,
            "configured_head":snapshot["configured_git"]["repository"]["head"],"runtime_head":rp.get("head"),"runtime_provenance":rp,
            "src":src["record"],"dst":dst["record"],"route":route,"laws":list(PROJECT_ATLAS_LAWS),
        }

    @staticmethod
    def _ensure_non_metering():
        import sys
        mod=sys.modules.get("athena_mcp.dispatch")
        if mod is not None and hasattr(mod,"NON_SELF_METERING"):mod.NON_SELF_METERING.update(PROJECT_ATLAS_TOOL_NAMES)

    def call_tool(self, name: str, args: dict):
        if name not in PROJECT_ATLAS_TOOL_NAMES:return False,None
        self._ensure_non_metering()
        if name=="athena_project_atlas_summary":return True,self.summary(args)
        if name=="athena_project_resolve":return True,self.resolve(args)
        if name=="athena_project_list":return True,self.list_records(args)
        if name=="athena_project_route":return True,self.route(args)
        return False,None

    def read_resource(self, uri: str):
        if uri!=PROJECT_ATLAS_RESOURCE["uri"]:raise KeyError(uri)
        result=self.summary({});result["resource"]=PROJECT_ATLAS_RESOURCE["uri"];result["resource_role"]="bounded federated Project Atlas summary; use tools for resolve/list/route";return result

    def benchmark(self):
        return {
            "project_atlas_surface":PROJECT_ATLAS_SURFACE_VERSION,"project_atlas_max_page":PROJECT_ATLAS_MAX_PAGE,
            "project_atlas_cached_head":self._cache_head,"project_atlas_cached_runtime_head":self._cache_runtime_head,
            "project_atlas_cached_surface_signature":self._cache_surface_signature,"project_atlas_cached_snapshot_id":self._cache_snapshot_id,
            "project_atlas_query_tools":4,"project_atlas_resource":PROJECT_ATLAS_RESOURCE["uri"],
            "project_atlas_boundary":"READ_ONLY; configured Git != runtime-source Git; unknown runtime tree != empty; snapshot identity=configured Git x runtime provenance/tree x MCP surface x federation; PROJECT_QUERY != PERSISTENT_STATE_MUTATION; PROJECT_ROUTE != SEMANTIC_EQUIVALENCE",
        }
