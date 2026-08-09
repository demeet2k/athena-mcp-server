from __future__ import annotations

import os
import re
from pathlib import Path

from .git_backend import GitBackend, GitStateError

HEX40=re.compile(r"^[0-9a-fA-F]{40}$")


def _normalize_repo(raw: str) -> str:
    value=str(raw or "").strip()
    value=re.sub(r"^git@([^:]+):",r"\1/",value)
    value=re.sub(r"^[a-z]+://","",value,flags=re.I).rstrip("/")
    if value.endswith(".git"):value=value[:-4]
    # Accept GitHub owner/name shorthand but canonicalize it to the same repo key
    # emitted by HTTPS/SSH origin URLs. Other hosts should be supplied explicitly.
    if re.fullmatch(r"[^./:]+/[^/]+",value):value=f"github.com/{value}"
    return value


def _source_checkout_root() -> Path | None:
    # In a source checkout athena_mcp/ sits directly below the repository root.
    # Never walk arbitrarily upward from site-packages: a venv may itself live
    # under some unrelated application repository.
    candidate=Path(__file__).resolve().parent.parent
    return candidate if (candidate/".git").exists() else None


def _root_frontier(root: Path, source: str) -> dict:
    try:
        backend=GitBackend(root);status=backend.status()
        try:remote=backend._git("remote","get-url","origin")
        except GitStateError:remote=""
        repo_key=_normalize_repo(remote) or f"local/{root.name}"
        return {
            "status":"RESOLVED","source":source,"mode":"GIT_CHECKOUT","attestation_level":"OBSERVED_LOCAL_GIT",
            "root":str(root),"repo_key":repo_key,"head":status["head"],"branch":status.get("branch"),"dirty":bool(status.get("dirty")),
        }
    except Exception as exc:
        return {
            "status":"HOLD_RUNTIME_PROVENANCE","source":source,"mode":"GIT_CHECKOUT","attestation_level":"NONE",
            "root":str(root),"reason":f"{type(exc).__name__}: {exc}",
        }


def runtime_frontier() -> dict:
    """Resolve runtime source provenance without borrowing the brain Git head.

    Priority:
      1. ATHENA_RUNTIME_GIT_ROOT exact checkout.
      2. package source checkout (athena_mcp/ directly under .git root).
      3. explicit ATHENA_RUNTIME_REPOSITORY + ATHENA_RUNTIME_GIT_HEAD host attestation.
      4. HOLD: package/version identity alone is not an exact Git frontier.
    """
    configured_root=str(os.getenv("ATHENA_RUNTIME_GIT_ROOT") or "").strip()
    if configured_root:
        root=Path(configured_root).expanduser().resolve()
        if not (root/".git").exists():
            return {
                "status":"HOLD_RUNTIME_PROVENANCE","source":"ATHENA_RUNTIME_GIT_ROOT","mode":"GIT_CHECKOUT","attestation_level":"NONE",
                "root":str(root),"reason":"ATHENA_RUNTIME_GIT_ROOT is not an exact Git checkout",
            }
        return _root_frontier(root,"ATHENA_RUNTIME_GIT_ROOT")

    source_root=_source_checkout_root()
    if source_root is not None:return _root_frontier(source_root,"PACKAGE_SOURCE_CHECKOUT")

    repo=str(os.getenv("ATHENA_RUNTIME_REPOSITORY") or "").strip();head=str(os.getenv("ATHENA_RUNTIME_GIT_HEAD") or "").strip()
    if repo or head:
        if not repo or not HEX40.fullmatch(head):
            return {
                "status":"HOLD_RUNTIME_PROVENANCE","source":"ENV_ATTESTATION","mode":"HEAD_ATTESTATION","attestation_level":"NONE",
                "repo_key":_normalize_repo(repo) if repo else None,"head":head or None,
                "reason":"ATHENA_RUNTIME_REPOSITORY and an exact 40-hex ATHENA_RUNTIME_GIT_HEAD are both required",
            }
        return {
            "status":"RESOLVED","source":"ENV_ATTESTATION","mode":"HEAD_ATTESTATION","attestation_level":"HOST_CONFIGURED_UNVERIFIED",
            "root":None,"repo_key":_normalize_repo(repo),"head":head.lower(),"branch":None,"dirty":None,
            "boundary":"host configuration supplies exact identity coordinates but is not independent promotion verification",
        }

    return {
        "status":"HOLD_RUNTIME_PROVENANCE","source":"NONE","mode":"UNRESOLVED","attestation_level":"NONE",
        "repo_key":None,"head":None,
        "reason":"Installed runtime has no exact source checkout or explicit runtime repository/head attestation; package version is insufficient for exact MCP Git coordinates.",
    }


def same_runtime_frontier(left: dict, right: dict) -> bool:
    keys=("status","mode","repo_key","head","root","attestation_level")
    return all(left.get(k)==right.get(k) for k in keys)
