from __future__ import annotations

from typing import Any, Mapping

AUTHORITY_TOOL_NAMES = {
    "athena_claim_register",
    "athena_claim_state",
    "athena_claim_list",
    "athena_claim_promote",
    "athena_claim_challenge",
    "athena_claim_resolve_canonical_challenge",
}


def call_authority_tool(ledger, name: str, args: Mapping[str, Any]):
    args = dict(args or {})
    if name == "athena_claim_register":
        return ledger.register(args["claim_id"], args["source_ref"], args.get("actor", "agent"))
    if name == "athena_claim_state":
        state = ledger.state(args["claim_id"])
        return state if state is not None else {"found": False, "claim_id": args["claim_id"]}
    if name == "athena_claim_list":
        return ledger.list(args.get("y"), args.get("status"), args.get("limit", 100))
    if name == "athena_claim_promote":
        return ledger.promote(
            args["claim_id"],
            args["target_y"],
            evidence=args.get("evidence"),
            test=args.get("test"),
            canonical_authority=args.get("canonical_authority"),
            actor=args.get("actor", "agent"),
        )
    if name == "athena_claim_challenge":
        return ledger.challenge(
            args["claim_id"],
            args["witness"],
            args["reason"],
            args.get("actor", "agent"),
        )
    if name == "athena_claim_resolve_canonical_challenge":
        return ledger.resolve_canonical_challenge(
            args["claim_id"],
            args["decision"],
            args["authority"],
            args.get("actor", "agent"),
        )
    raise KeyError(name)


def authority_resource_value(ledger):
    return {
        "law": {
            "states": ["?", "+", "!", "#"],
            "promotion": "non-skippable ?->+->!->#",
            "support_gate": "verified support|derive|reproduce ref",
            "execution_gate": "procedure+observation+result+witness",
            "canonical_gate": "authorized=true + ref",
            "challenge": "verified witness+reason",
            "canonical_challenge": "# remains canonical but blocks automatic routing until UPHOLD|DEMOTE authorized resolution",
            "separation": "authority != confidence != truth != branch reward",
        },
        "claims": ledger.list(limit=500),
        "benchmark": ledger.benchmark(),
    }
