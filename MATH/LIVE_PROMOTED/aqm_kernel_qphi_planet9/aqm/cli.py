from __future__ import annotations

import argparse
import os
import json
from typing import Any, Dict

from .addressing import TileAddress
from .kernel import Tile
from .store import MerkleStore
from .ledger import Ledger
from .certs import CertificateBundle
from .manifest import ExtractionManifest

def _demo(store_dir: str) -> None:
    store = MerkleStore(store_dir)

    # Example: Chapter 01, Square Lens, Facet 1 (Objects & Types)
    addr1 = TileAddress.for_chapter(1, "S", 1)
    ledger1 = Ledger()
    ledger1.append("CreateTile", {"address": addr1.to_ascii()})
    cert1 = CertificateBundle()
    cert1.add_obligation("Totality", "Evaluation returns a typed outcome (Value/Jet/Branch/Liminal/Fail).")

    tile1 = Tile(
        kind="Tile",
        address=addr1,
        seed={"title": "Ch01 S.1 Objects & Types"},
        payload={
            "seed_contract": "tile = seed + obligations + replay",
            "typed_outcomes": ["ValueState","Jet","BranchState","LiminalState","FailType"],
        },
        cert=cert1.summary(),
        ledger=ledger1.anchor(),
        escalation_policy={
            "when_ambiguous": ["increase_jet_order", "shrink_neighborhood", "refine_realization"],
            "when_forbidden": "emit FailType with budget infeasibility",
        },
    )

    h1 = store.put(tile1)

    # Example: Chapter 01, Fractal Lens, Facet 1 (Tile object model)
    addr2 = TileAddress.for_chapter(1, "R", 1)
    ledger2 = Ledger()
    ledger2.append("CreateTile", {"address": addr2.to_ascii()})
    cert2 = CertificateBundle()
    cert2.add_obligation("ReplayDeterminism", "Seed + deps deterministically reconstruct payload + cert + ledger anchors.")

    tile2 = Tile(
        kind="Tile",
        address=addr2,
        seed={"title": "Ch01 R.1 Tile object model"},
        payload={
            "kernel_object": {
                "Seed": "minimal reconstruction parameters",
                "Meta": "policy/regime/context IDs",
                "PayloadRef": "content-addressed payload pointer",
                "CertRef": "certificate bundle pointer",
                "LedgerAnchor": "ledger subtree pointer",
            },
            "dependencies": [],
        },
        cert=cert2.summary(),
        ledger=ledger2.anchor(),
        escalation_policy={"default": "deterministic; no silent conventions"},
    )

    h2 = store.put(tile2)

    # Chapter manifest
    man = ExtractionManifest(manifest_id="Ch01-demo", chapter=1, deps=[])
    man.add_tile(addr1.to_ascii(), h1, tags={"lens": "S", "facet": 1})
    man.add_tile(addr2.to_ascii(), h2, tags={"lens": "R", "facet": 1})
    man_hash = store.put(Tile(kind="Tile", address=TileAddress.for_chapter(1,"R",4),
                              seed={"title":"Ch01 manifest wrapper"},
                              payload={"manifest": man.to_canonical_dict(), "manifest_hash": man.hash()},
                              cert=None, ledger=None))
    # Verify closure and hashes
    closure = store.closure(man_hash)
    ok = all(store.verify_hash(h) for h in closure)

    print(json.dumps({
        "store_dir": store_dir,
        "tile_hashes": {"tile1": h1, "tile2": h2},
        "manifest_hash": man.hash(),
        "manifest_wrapper_hash": man_hash,
        "closure": closure,
        "closure_ok": ok,
    }, indent=2))

def main() -> None:
    ap = argparse.ArgumentParser(prog="aqm")
    sub = ap.add_subparsers(dest="cmd", required=True)

    demo = sub.add_parser("demo", help="build + store a tiny demo tile set")
    demo.add_argument("--store", default="./.aqm_store_demo", help="directory for the merkle store")

    args = ap.parse_args()
    if args.cmd == "demo":
        _demo(args.store)

if __name__ == "__main__":
    main()
