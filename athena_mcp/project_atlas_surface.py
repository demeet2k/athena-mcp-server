from __future__ import annotations

from pathlib import PurePosixPath

from .identity import digest
from .project_atlas import compile_runtime_atlas, route_records
from .project_atlas_protocol import PROJECT_ATLAS_RESOURCE, PROJECT_ATLAS_TOOL_NAMES

PROJECT_ATLAS_SURFACE_VERSION="ATHENA.PROJECT_ATLAS.MCP_SURFACE.V2"
PROJECT_ATLAS_MAX_PAGE=100
PROJECT_ATLAS_LAWS=[
    "KC144_STATION != OBJECT_IDENTITY",
    "POID != OID != MID != VID",
    "MCP_VIRTUAL_OBJECT != GIT_BLOB",
    "PROJECT_QUERY != PROMOTION_AUTHORITY",
    "PROJECT_ROUTE != SEMANTIC_EQUIVALENCE",
    "AMBIGUOUS_RESOLVE -> HOLD",
    "HEAD_CHANGE -> RECOMPILE_BEFORE_CONSEQUENTIAL_ROUTE",
    "MCP_SURFACE_CHANGE -> RECOMPILE_BEFORE_QUERY",
    "CROSS_REPO_ROUTE_REQUIRES_EXACT_REPO_HEAD",
    "PROJECT_QUERY != PERSISTENT_STATE_MUTATION",
]


class ProjectAtlasSurface:
    """Read-only bounded query projection over the exact-head V1 Project Atlas."""

    def __init__(self, server):
        self.server=server
        self._cache_key=None
        self._cache_head=None
        self._cache_surface_signature=None
        self._cache=None

    def _hold(self, status: str, **extra):
        return {
            "status":status,
            "surface_version":PROJECT_ATLAS_SURFACE_VERSION,
            "laws":list(PROJECT_ATLAS_LAWS),
            **extra,
        }

    @staticmethod
    def _surface_signature():
        # Protocol TOOLS/PROMPTS are process-live surfaces: dispatch can lawfully
        # compose additional tool modules after server import without moving Git.
        # A Git-only cache key would therefore return stale MCP coordinates.
        from .protocol import PROMPTS, TOOLS
        return digest({"tools":TOOLS,"prompts":PROMPTS},32)

    def _invalidate_cache(self):
        self._cache_key=None
        self._cache_head=None
        self._cache_surface_signature=None
        self._cache=None

    def _snapshot(self, expected_head=None):
        git=getattr(self.server,"git",None)
        if git is None or not git.enabled:
            return None,self._hold(
                "HOLD_GIT_UNAVAILABLE",
                reason="Project Atlas query surface requires a configured ATHENA_GIT_ROOT checkout.",
                head=None,
            ),None

        expected=str(expected_head).strip() if expected_head else None
        for _ in range(2):
            before=git.status()
            head=before["head"]
            surface_signature=self._surface_signature()
            cache_key=(head,surface_signature)
            if expected is not None and head != expected:
                return None,self._hold(
                    "HOLD_STALE_HEAD",
                    expected_head=expected,
                    current_head=head,
                    current_surface_signature=surface_signature,
                    head=head,
                    reason="Expected Git head does not match the current configured project frontier.",
                ),before

            if self._cache_key == cache_key and self._cache is not None:
                atlas=self._cache
            else:
                # Compile against the immutable SHA, not the moving symbolic HEAD.
                atlas=compile_runtime_atlas(git.root, ref=head, include_trees=True)
                atlas_head=atlas.get("git",{}).get("repository",{}).get("head")
                if atlas_head != head:
                    self._invalidate_cache()
                    continue

            after=git.status()
            after_signature=self._surface_signature()
            atlas_head=atlas.get("git",{}).get("repository",{}).get("head")
            if after["head"] == head == atlas_head and after_signature == surface_signature:
                # Cache only a doubly stable frontier: committed Git + live MCP ABI.
                self._cache_key=cache_key
                self._cache_head=head
                self._cache_surface_signature=surface_signature
                self._cache=atlas
                observation={
                    "branch":after.get("branch"),
                    "head":head,
                    "dirty":bool(after.get("dirty")),
                    "git_enabled":True,
                    "mcp_surface_signature":surface_signature,
                }
                return atlas,None,observation
            self._invalidate_cache()

        current=git.status()
        current_signature=self._surface_signature()
        return None,self._hold(
            "HOLD_VOLATILE_FRONTIER",
            current_head=current.get("head"),
            current_surface_signature=current_signature,
            head=current.get("head"),
            reason="Git HEAD or the live MCP tool/prompt surface moved while compiling the Project Atlas; retry against a stable frontier.",
        ),current

    @staticmethod
    def _summary_record(source: str, rec: dict) -> dict:
        native=dict(rec["native"])
        project=rec["project_kc144"]
        reference=rec["kc144_reference"]
        out={
            "source":source,
            "poid":rec["poid"],
            "address":rec["address"],
            "native":{
                "repo":native.get("repo"),
                "ref":native.get("ref"),
                "head":native.get("head"),
                "tree":native.get("tree"),
                "path":native.get("path"),
                "object_sha":native.get("object_sha"),
                "git_type":native.get("git_type"),
                "mode":native.get("mode"),
            },
            "project_kc144":{
                "gid":project["gid"],
                "sid":project["sid"],
                "row":project["row"],
                "col":project["col"],
                "row_semantic":project.get("row_semantic"),
                "col_semantic":project.get("col_semantic"),
            },
            "kc144_reference":{
                "gid":reference["gid"],
                "sid":reference["sid"],
                "row":reference["row"],
                "col":reference["col"],
            },
            "return":rec["return"],
        }
        if rec.get("mcp") is not None:
            out["mcp"]=dict(rec["mcp"])
        if rec.get("navigation") is not None:
            out["navigation"]={
                "parent_path":rec["navigation"].get("parent_path"),
                "station_ordinal":rec["navigation"].get("station_ordinal"),
                "station_population":rec["navigation"].get("station_population"),
            }
        return out

    @staticmethod
    def _all_records(atlas: dict):
        rows=[("git",r) for r in atlas.get("git",{}).get("records",[])]
        rows.extend(("mcp",r) for r in atlas.get("mcp_surface",{}).get("records",[]))
        return rows

    def _resolve_in_atlas(self, atlas: dict, identifier: str) -> dict:
        ident=str(identifier)
        convenience=ident[2:] if ident.startswith("./") else ident
        matches=[]
        for source,rec in self._all_records(atlas):
            native=rec["native"]
            aliases={
                rec["poid"],
                rec["address"],
                native.get("path"),
                rec.get("return",{}).get("uri"),
            }
            mcp=rec.get("mcp")
            if mcp:
                aliases.update({
                    mcp.get("name"),
                    f"{mcp.get('kind')}:{mcp.get('name')}",
                    f"mcp:{mcp.get('kind')}:{mcp.get('name')}",
                })
            if ident in aliases or (source=="git" and convenience==native.get("path")):
                matches.append((source,rec))

        # Defensive de-dup if multiple alias forms point to the same record.
        uniq={}
        for source,rec in matches:
            uniq[(source,rec["poid"])]=(source,rec)
        matches=list(uniq.values())
        head=atlas["git"]["repository"]["head"]
        if not matches:
            return self._hold(
                "HOLD_NOT_FOUND",
                identifier=ident,
                head=head,
                candidates=[],
            )
        if len(matches)>1:
            return self._hold(
                "HOLD_AMBIGUOUS",
                identifier=ident,
                head=head,
                candidate_count=len(matches),
                candidates=[self._summary_record(source,rec) for source,rec in matches[:20]],
            )
        source,rec=matches[0]
        return {
            "status":"RESOLVED",
            "surface_version":PROJECT_ATLAS_SURFACE_VERSION,
            "head":head,
            "identifier":ident,
            "record":self._summary_record(source,rec),
            "full_record":rec,
            "laws":list(PROJECT_ATLAS_LAWS),
        }

    def summary(self, args=None):
        args=args or {}
        atlas,hold,observation=self._snapshot(args.get("expected_head"))
        if hold:return hold
        git_atlas=atlas["git"]
        repo=git_atlas["repository"]
        surface=atlas.get("mcp_surface",{})
        federation=atlas.get("federation",{})
        return {
            "status":"PASS",
            "surface_version":PROJECT_ATLAS_SURFACE_VERSION,
            "head":repo["head"],
            "repository":{
                "repo_key":repo["repo_key"],
                "ref":repo["ref"],
                "head":repo["head"],
                "tree":repo["tree"],
                "atlas_digest":git_atlas["atlas_digest"],
                "counts":git_atlas["counts"],
            },
            "mcp_surface":{
                "server":surface.get("server"),
                "count":surface.get("count",0),
                "surface_digest":surface.get("surface_digest"),
                "live_signature":observation.get("mcp_surface_signature") if observation else None,
            },
            "federation":{
                "count":federation.get("count",0),
                "federation_digest":federation.get("federation_digest"),
            },
            "checkout_observation":observation,
            "pagination":{"default_limit":50,"max_limit":PROJECT_ATLAS_MAX_PAGE},
            "laws":list(PROJECT_ATLAS_LAWS),
        }

    def resolve(self, args: dict):
        atlas,hold,_=self._snapshot(args.get("expected_head"))
        if hold:return hold
        result=self._resolve_in_atlas(atlas,args["identifier"])
        if result.get("status")=="RESOLVED":
            # Expose exactly one bounded record; never the whole project atlas.
            result.pop("full_record",None)
        return result

    def list_records(self, args: dict):
        atlas,hold,_=self._snapshot(args.get("expected_head"))
        if hold:return hold
        source_filter=args.get("source","all")
        prefix=args.get("path_prefix")
        if prefix is not None:
            prefix=prefix[2:] if prefix.startswith("./") else prefix
        directory=args.get("directory")
        if directory == ".":
            directory=""
        elif directory and directory.startswith("./"):
            directory=directory[2:]
        poid_prefix=args.get("poid_prefix")
        rows=[]
        for source,rec in self._all_records(atlas):
            if source_filter!="all" and source!=source_filter:continue
            native=rec["native"]; project=rec["project_kc144"]; reference=rec["kc144_reference"]
            if prefix is not None and not native["path"].startswith(prefix):continue
            if args.get("git_type") is not None and native["git_type"]!=args["git_type"]:continue
            if args.get("project_gid") is not None and project["gid"]!=int(args["project_gid"]):continue
            if args.get("project_row") is not None and project["row"]!=int(args["project_row"]):continue
            if args.get("project_col") is not None and project["col"]!=int(args["project_col"]):continue
            if args.get("reference_gid") is not None and reference["gid"]!=int(args["reference_gid"]):continue
            parent=str(PurePosixPath(native["path"]).parent)
            if parent==".":parent=""
            if directory is not None and parent!=directory:continue
            mcp=rec.get("mcp")
            if args.get("mcp_kind") is not None and (not mcp or mcp.get("kind")!=args["mcp_kind"]):continue
            if poid_prefix is not None and not rec["poid"].startswith(poid_prefix):continue
            rows.append((source,rec))
        rows.sort(key=lambda x:(x[0],x[1]["native"]["path"],x[1]["native"]["git_type"],x[1]["poid"]))
        total=len(rows);offset=int(args.get("offset",0));limit=min(PROJECT_ATLAS_MAX_PAGE,int(args.get("limit",50)))
        page=rows[offset:offset+limit]
        next_offset=offset+len(page)
        if next_offset>=total:next_offset=None
        return {
            "status":"PASS",
            "surface_version":PROJECT_ATLAS_SURFACE_VERSION,
            "head":atlas["git"]["repository"]["head"],
            "total":total,
            "offset":offset,
            "limit":limit,
            "next_offset":next_offset,
            "items":[self._summary_record(source,rec) for source,rec in page],
            "filters":{k:v for k,v in args.items() if k not in {"expected_head","offset","limit"} and v is not None},
            "laws":list(PROJECT_ATLAS_LAWS),
        }

    def route(self, args: dict):
        atlas,hold,_=self._snapshot(args.get("expected_head"))
        if hold:return hold
        src=self._resolve_in_atlas(atlas,args["src"])
        if src.get("status")!="RESOLVED":
            return self._hold(
                "HOLD_ROUTE_SOURCE",
                head=atlas["git"]["repository"]["head"],
                source_resolution=src,
            )
        dst=self._resolve_in_atlas(atlas,args["dst"])
        if dst.get("status")!="RESOLVED":
            return self._hold(
                "HOLD_ROUTE_DESTINATION",
                head=atlas["git"]["repository"]["head"],
                destination_resolution=dst,
            )
        route=route_records(src["full_record"],dst["full_record"],wrap=bool(args.get("wrap",False)))
        return {
            "status":"ROUTED",
            "surface_version":PROJECT_ATLAS_SURFACE_VERSION,
            "head":atlas["git"]["repository"]["head"],
            "src":src["record"],
            "dst":dst["record"],
            "route":route,
            "laws":list(PROJECT_ATLAS_LAWS),
        }

    @staticmethod
    def _ensure_non_metering():
        # dispatch meters most tools into learned runtime usage. Project Atlas is
        # a read-only observation surface, so register these calls as non-self-
        # metering before dispatch performs post-call accounting.
        import sys
        mod=sys.modules.get("athena_mcp.dispatch")
        if mod is not None and hasattr(mod,"NON_SELF_METERING"):
            mod.NON_SELF_METERING.update(PROJECT_ATLAS_TOOL_NAMES)

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
        result=self.summary({})
        result["resource"]=PROJECT_ATLAS_RESOURCE["uri"]
        result["resource_role"]="bounded exact-head Project Atlas summary; use tools for resolve/list/route"
        return result

    def benchmark(self):
        return {
            "project_atlas_surface":PROJECT_ATLAS_SURFACE_VERSION,
            "project_atlas_max_page":PROJECT_ATLAS_MAX_PAGE,
            "project_atlas_cached_head":self._cache_head,
            "project_atlas_cached_surface_signature":self._cache_surface_signature,
            "project_atlas_query_tools":4,
            "project_atlas_resource":PROJECT_ATLAS_RESOURCE["uri"],
            "project_atlas_boundary":"READ_ONLY; cache frontier=Git HEAD x live MCP surface signature; PROJECT_QUERY != PERSISTENT_STATE_MUTATION; PROJECT_ROUTE != SEMANTIC_EQUIVALENCE",
        }
