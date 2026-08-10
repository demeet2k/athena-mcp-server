from __future__ import annotations

import hashlib
import json
import threading
import time
from typing import Any, Mapping

VERSION = "ATHENA.EPHEMERAL.COORDINATION.MEMBRANE.V0"
RECEIPT_STAGES = ("DELIVERED", "PRESENTED", "CONSUMED", "INCORPORATED", "DECISION_CHANGED")
RECEIPT_RANK = {stage: i for i, stage in enumerate(RECEIPT_STAGES, 1)}
DELIVERY_CLASSES = ("RENDEZVOUS", "NEED_OFFER", "NUDGE", "BLOCKER", "MATERIAL_CANDIDATE")

SCHEMA = """
CREATE TABLE IF NOT EXISTS ephemeral_presence(
 aid TEXT PRIMARY KEY,presence_id TEXT NOT NULL,epoch TEXT NOT NULL,capabilities_json TEXT NOT NULL,
 need_offer_summary_json TEXT NOT NULL,lamport INTEGER NOT NULL,causal_parents_json TEXT NOT NULL,
 source_digest TEXT NOT NULL,accepted_at REAL NOT NULL,expires_at REAL NOT NULL,cursor INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS ephemeral_packets(
 packet_id TEXT PRIMARY KEY,sender_aid TEXT NOT NULL,delivery_class TEXT NOT NULL,salience REAL NOT NULL,
 ttl_ms INTEGER NOT NULL,packet_digest_or_ref TEXT NOT NULL,lamport INTEGER NOT NULL,
 causal_parents_json TEXT NOT NULL,coalesce_key TEXT NOT NULL,created_at REAL NOT NULL,expires_at REAL NOT NULL);
CREATE INDEX IF NOT EXISTS idx_ephemeral_packets_coalesce ON ephemeral_packets(coalesce_key,expires_at);
CREATE TABLE IF NOT EXISTS ephemeral_deliveries(
 packet_id TEXT NOT NULL,recipient_aid TEXT NOT NULL,cursor INTEGER NOT NULL,route_state TEXT NOT NULL,
 created_at REAL NOT NULL,expires_at REAL NOT NULL,PRIMARY KEY(packet_id,recipient_aid),
 FOREIGN KEY(packet_id) REFERENCES ephemeral_packets(packet_id) ON DELETE CASCADE);
CREATE INDEX IF NOT EXISTS idx_ephemeral_deliveries_recipient ON ephemeral_deliveries(recipient_aid,cursor);
CREATE TABLE IF NOT EXISTS ephemeral_receipts(
 packet_id TEXT NOT NULL,aid TEXT NOT NULL,stage TEXT NOT NULL,stage_rank INTEGER NOT NULL,
 witness_json TEXT NOT NULL,cursor INTEGER NOT NULL,created_at REAL NOT NULL,
 PRIMARY KEY(packet_id,aid,stage),FOREIGN KEY(packet_id) REFERENCES ephemeral_packets(packet_id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS ephemeral_events(
 cursor INTEGER PRIMARY KEY AUTOINCREMENT,event_type TEXT NOT NULL,subject_id TEXT NOT NULL,
 aid TEXT NOT NULL,payload_json TEXT NOT NULL,created_at REAL NOT NULL);
"""


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _text(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} must be non-empty")
    return text


def _int(value: Any, field: str, low: int, high: int) -> int:
    try:
        out = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be an integer") from None
    if out < low or out > high:
        raise ValueError(f"{field} must be between {low} and {high}")
    return out


def _float(value: Any, field: str, low: float, high: float) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be numeric") from None
    if out < low or out > high:
        raise ValueError(f"{field} must be between {low} and {high}")
    return out


def _strings(value: Any, field: str, max_items: int) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{field} must be an array")
    out = []
    seen = set()
    for raw in value:
        item = _text(raw, field)
        if item not in seen:
            seen.add(item)
            out.append(item)
        if len(out) > max_items:
            raise ValueError(f"{field} exceeds {max_items} unique items")
    return out


class EphemeralCoordinationRuntime:
    """Request/poll, process-local coordination with zero durable authority."""

    def __init__(self, store, *, clock=None, per_aid_queue_limit=128,
                 sender_active_salience_limit=32.0, global_active_salience_limit=256.0,
                 max_active_packets=4096, max_events=8192):
        self.store = store
        self.db = store.db
        self._lock = getattr(store, "_lock", threading.RLock())
        self.clock = clock or time.time
        self.per_aid_queue_limit = int(per_aid_queue_limit)
        self.sender_active_salience_limit = float(sender_active_salience_limit)
        self.global_active_salience_limit = float(global_active_salience_limit)
        self.max_active_packets = int(max_active_packets)
        self.max_events = int(max_events)
        if min(self.per_aid_queue_limit, self.max_active_packets, self.max_events) <= 0:
            raise ValueError("limits must be positive")
        with self._lock, self.db:
            self.db.executescript(SCHEMA)

    def _now(self):
        return float(self.clock())

    def _event(self, event_type, subject_id, aid, payload, now):
        cur = self.db.execute(
            "INSERT INTO ephemeral_events(event_type,subject_id,aid,payload_json,created_at) VALUES(?,?,?,?,?)",
            (event_type, subject_id, aid, _json(payload), now),
        )
        cursor = int(cur.lastrowid)
        floor = max(0, cursor - self.max_events)
        if floor:
            self.db.execute("DELETE FROM ephemeral_events WHERE cursor<=?", (floor,))
        return cursor

    def _gc(self, now):
        p = self.db.execute("SELECT COUNT(*) FROM ephemeral_presence WHERE expires_at<=?", (now,)).fetchone()[0]
        d = self.db.execute("SELECT COUNT(*) FROM ephemeral_deliveries WHERE expires_at<=?", (now,)).fetchone()[0]
        self.db.execute("DELETE FROM ephemeral_presence WHERE expires_at<=?", (now,))
        self.db.execute("DELETE FROM ephemeral_deliveries WHERE expires_at<=?", (now,))
        q = self.db.execute(
            "SELECT COUNT(*) FROM ephemeral_packets WHERE expires_at<=? OR NOT EXISTS(SELECT 1 FROM ephemeral_deliveries d WHERE d.packet_id=ephemeral_packets.packet_id)",
            (now,),
        ).fetchone()[0]
        self.db.execute(
            "DELETE FROM ephemeral_packets WHERE expires_at<=? OR NOT EXISTS(SELECT 1 FROM ephemeral_deliveries d WHERE d.packet_id=ephemeral_packets.packet_id)",
            (now,),
        )
        return {"presence_expired": int(p), "deliveries_expired": int(d), "packets_expired_or_empty": int(q)}

    def _next_cursor(self):
        row = self.db.execute("SELECT MAX(cursor) FROM ephemeral_events").fetchone()
        return int(row[0] or 0)

    def _cursor_floor(self):
        row = self.db.execute("SELECT MIN(cursor) FROM ephemeral_events").fetchone()
        return int(row[0] or 0)

    def _live(self, aid, now):
        return self.db.execute("SELECT * FROM ephemeral_presence WHERE aid=? AND expires_at>?", (aid, now)).fetchone()

    def present(self, args: Mapping[str, Any]):
        aid = _text(args.get("aid"), "aid")
        epoch = _text(args.get("epoch"), "epoch")
        ttl_ms = _int(args.get("ttl_ms"), "ttl_ms", 250, 300000)
        capabilities = _strings(args.get("capabilities", []), "capabilities", 64)
        summary = args.get("need_offer_summary") or {}
        if not isinstance(summary, Mapping):
            raise ValueError("need_offer_summary must be an object")
        lamport = _int(args.get("lamport", 0), "lamport", 0, 2**63 - 1)
        parents = _strings(args.get("causal_parents", []), "causal_parents", 32)
        source_digest = _text(args.get("source_digest"), "source_digest")
        now = self._now()
        expires_at = now + ttl_ms / 1000.0
        presence_id = "epres_" + _hash({"aid": aid, "epoch": epoch, "source_digest": source_digest})[:32]
        with self._lock, self.db:
            gc = self._gc(now)
            cursor = self._event("PRESENT", presence_id, aid, {"epoch": epoch, "ttl_ms": ttl_ms, "lamport": lamport}, now)
            self.db.execute(
                "INSERT INTO ephemeral_presence VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(aid) DO UPDATE SET "
                "presence_id=excluded.presence_id,epoch=excluded.epoch,capabilities_json=excluded.capabilities_json,"
                "need_offer_summary_json=excluded.need_offer_summary_json,lamport=excluded.lamport,causal_parents_json=excluded.causal_parents_json,"
                "source_digest=excluded.source_digest,accepted_at=excluded.accepted_at,expires_at=excluded.expires_at,cursor=excluded.cursor",
                (aid, presence_id, epoch, _json(capabilities), _json(dict(summary)), lamport, _json(parents), source_digest, now, expires_at, cursor),
            )
        return {"presence_id": presence_id, "accepted_at": now, "expires_at": expires_at, "cursor": cursor, "gc": gc,
                "standing": "PROCESS_LOCAL_EPHEMERAL_PRESENCE", "source_digest_standing": "CALLER_SUPPLIED_OPAQUE_REFERENCE",
                "authority": "NONE", "laws": ["PRESENCE!=CLAIM", "PRESENCE!=HOST_LIVENESS_PROOF", "FAST_CHANNEL!=TRUTH"]}

    def _recipients(self, selector):
        if not isinstance(selector, Mapping) or set(selector) - {"aids"}:
            raise ValueError("recipient_selector supports only explicit aids")
        aids = _strings(selector.get("aids"), "recipient_selector.aids", 32)
        if not aids:
            raise ValueError("recipient_selector.aids must be non-empty")
        return sorted(set(aids))

    def _active_salience(self, now, sender=None):
        sql = "SELECT COALESCE(SUM(p.salience),0) FROM ephemeral_deliveries d JOIN ephemeral_packets p ON p.packet_id=d.packet_id WHERE d.expires_at>?"
        args = [now]
        if sender is not None:
            sql += " AND p.sender_aid=?"
            args.append(sender)
        return float(self.db.execute(sql, tuple(args)).fetchone()[0] or 0.0)

    def post(self, args: Mapping[str, Any]):
        sender = _text(args.get("sender_aid"), "sender_aid")
        recipients = self._recipients(args.get("recipient_selector"))
        delivery_class = _text(args.get("delivery_class"), "delivery_class")
        if delivery_class not in DELIVERY_CLASSES:
            raise ValueError(f"delivery_class must be one of {list(DELIVERY_CLASSES)}")
        salience = _float(args.get("salience"), "salience", 0.0, 1.0)
        ttl_ms = _int(args.get("ttl_ms"), "ttl_ms", 250, 300000)
        ref = _text(args.get("packet_digest_or_ref"), "packet_digest_or_ref")
        lamport = _int(args.get("lamport", 0), "lamport", 0, 2**63 - 1)
        parents = _strings(args.get("causal_parents", []), "causal_parents", 32)
        now = self._now()
        expires_at = now + ttl_ms / 1000.0
        coalesce_key = _hash({"sender": sender, "recipients": recipients, "delivery_class": delivery_class, "ref": ref})
        packet_id = "epkt_" + _hash({"coalesce_key": coalesce_key, "lamport": lamport, "parents": parents})[:32]
        with self._lock, self.db:
            gc = self._gc(now)
            if self._live(sender, now) is None:
                raise ValueError("sender_aid must have unexpired process-local presence")
            existing = self.db.execute(
                "SELECT packet_id FROM ephemeral_packets WHERE coalesce_key=? AND expires_at>? ORDER BY created_at DESC LIMIT 1",
                (coalesce_key, now),
            ).fetchone()
            if existing:
                return {"packet_id": existing["packet_id"], "route_state": "COALESCED_ACTIVE", "cursor": self._next_cursor(),
                        "coalesced": True, "gc": gc, "authority": "NONE",
                        "durable_escalation_required": delivery_class == "MATERIAL_CANDIDATE"}
            if self.db.execute("SELECT COUNT(*) FROM ephemeral_packets WHERE expires_at>?", (now,)).fetchone()[0] >= self.max_active_packets:
                raise ValueError("GLOBAL_ACTIVE_PACKET_BACKPRESSURE")
            added = salience * len(recipients)
            if self._active_salience(now, sender) + added > self.sender_active_salience_limit:
                raise ValueError("SENDER_SALIENCE_BACKPRESSURE")
            if self._active_salience(now) + added > self.global_active_salience_limit:
                raise ValueError("GLOBAL_SALIENCE_BACKPRESSURE")
            for aid in recipients:
                queued = self.db.execute("SELECT COUNT(*) FROM ephemeral_deliveries WHERE recipient_aid=? AND expires_at>?", (aid, now)).fetchone()[0]
                if queued >= self.per_aid_queue_limit:
                    raise ValueError(f"RECIPIENT_QUEUE_BACKPRESSURE aid={aid}")
            cursor = self._event("POST", packet_id, sender, {"recipients": recipients, "delivery_class": delivery_class, "salience": salience}, now)
            self.db.execute("INSERT INTO ephemeral_packets VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                            (packet_id, sender, delivery_class, salience, ttl_ms, ref, lamport, _json(parents), coalesce_key, now, expires_at))
            self.db.executemany("INSERT INTO ephemeral_deliveries VALUES(?,?,?,?,?,?)",
                                [(packet_id, aid, cursor, "ROUTED", now, expires_at) for aid in recipients])
        return {"packet_id": packet_id, "route_state": "ROUTED", "cursor": cursor, "coalesced": False,
                "recipient_count": len(recipients), "gc": gc, "authority": "NONE",
                "durable_escalation_required": delivery_class == "MATERIAL_CANDIDATE",
                "durable_escalation_contract": {"performed": False, "target": "ROOM_OR_GIT_MESSAGE_BOARD",
                    "law": "MATERIAL_ESCALATION_IS_EXPLICIT_CALLER_WORK_NOT_HIDDEN_BACKGROUND_EXECUTION"}}

    def _receipt_stage(self, packet_id, aid):
        row = self.db.execute("SELECT stage FROM ephemeral_receipts WHERE packet_id=? AND aid=? ORDER BY stage_rank DESC LIMIT 1", (packet_id, aid)).fetchone()
        return row["stage"] if row else None

    def poll(self, args: Mapping[str, Any]):
        aid = _text(args.get("aid"), "aid")
        after = _int(args.get("after_cursor", 0), "after_cursor", 0, 2**63 - 1)
        max_items = _int(args.get("max_items", 20), "max_items", 1, 100)
        budget = _float(args.get("salience_budget", 8.0), "salience_budget", 0.0, 32.0)
        now = self._now()
        with self._lock, self.db:
            gc = self._gc(now)
            floor = self._cursor_floor()
            rows = self.db.execute(
                "SELECT d.cursor,d.route_state,d.expires_at,p.* FROM ephemeral_deliveries d JOIN ephemeral_packets p ON p.packet_id=d.packet_id "
                "WHERE d.recipient_aid=? AND d.cursor>? AND d.expires_at>? ORDER BY d.cursor ASC LIMIT ?",
                (aid, after, now, max_items + 1),
            ).fetchall()
            items, spent, blocked = [], 0.0, False
            for row in rows:
                if len(items) >= max_items:
                    break
                salience = float(row["salience"])
                if spent + salience > budget:
                    blocked = True
                    break
                spent += salience
                items.append({"cursor": int(row["cursor"]), "packet_id": row["packet_id"], "sender_aid": row["sender_aid"],
                              "delivery_class": row["delivery_class"], "salience": salience, "packet_digest_or_ref": row["packet_digest_or_ref"],
                              "lamport": int(row["lamport"]), "causal_parents": json.loads(row["causal_parents_json"]),
                              "route_state": row["route_state"], "created_at": float(row["created_at"]), "expires_at": float(row["expires_at"]),
                              "receipt_stage": self._receipt_stage(row["packet_id"], aid)})
            queued = int(self.db.execute("SELECT COUNT(*) FROM ephemeral_deliveries WHERE recipient_aid=? AND expires_at>?", (aid, now)).fetchone()[0])
        return {"packets": items, "next_cursor": int(items[-1]["cursor"]) if items else after, "cursor_floor": floor,
                "replay_truncated": bool(after and floor and after < floor), "salience_spent": spent,
                "queue_pressure": {"queued": queued, "limit": self.per_aid_queue_limit, "ratio": min(1.0, queued / self.per_aid_queue_limit)},
                "dropped_or_coalesced_counts": {"expired_dropped": gc["deliveries_expired"], "budget_blocked": int(blocked), "coalesced_in_this_poll": 0},
                "ordering": "MONOTONIC_PROCESS_CURSOR;LAMPORT_IS_PACKET_METADATA_NOT_GLOBAL_TOTAL_ORDER", "authority": "NONE",
                "law": "POLL_IS_EXPLICIT_RUNTIME_WORK_NOT_BACKGROUND_PUSH"}

    def receipt(self, args: Mapping[str, Any]):
        packet_id = _text(args.get("packet_id"), "packet_id")
        aid = _text(args.get("aid"), "aid")
        stage = _text(args.get("stage"), "stage")
        if stage not in RECEIPT_RANK:
            raise ValueError(f"stage must be one of {list(RECEIPT_STAGES)}")
        witness = args.get("witness") or {}
        if not isinstance(witness, Mapping):
            raise ValueError("witness must be an object")
        if RECEIPT_RANK[stage] >= RECEIPT_RANK["CONSUMED"] and not witness:
            raise ValueError(f"{stage} requires a non-empty typed witness object")
        now = self._now()
        with self._lock, self.db:
            gc = self._gc(now)
            delivery = self.db.execute("SELECT 1 FROM ephemeral_deliveries WHERE packet_id=? AND recipient_aid=? AND expires_at>?", (packet_id, aid, now)).fetchone()
            if not delivery:
                raise ValueError("receipt requires an unexpired packet routed to aid")
            old = self.db.execute("SELECT cursor,created_at,witness_json FROM ephemeral_receipts WHERE packet_id=? AND aid=? AND stage=?", (packet_id, aid, stage)).fetchone()
            if old:
                return {"packet_id": packet_id, "aid": aid, "stage": stage, "cursor": int(old["cursor"]), "created_at": float(old["created_at"]),
                        "idempotent": True, "witness": json.loads(old["witness_json"]), "authority": "NONE",
                        "receipt_standing": "CALLER_ATTESTED_RUNTIME_RECEIPT"}
            highest = int(self.db.execute("SELECT COALESCE(MAX(stage_rank),0) FROM ephemeral_receipts WHERE packet_id=? AND aid=?", (packet_id, aid)).fetchone()[0] or 0)
            expected = highest + 1
            if RECEIPT_RANK[stage] != expected:
                label = RECEIPT_STAGES[expected - 1] if expected <= len(RECEIPT_STAGES) else "NONE"
                raise ValueError(f"RECEIPT_STAGE_GAP expected={label} got={stage}")
            cursor = self._event("RECEIPT", packet_id, aid, {"stage": stage, "witness": dict(witness)}, now)
            self.db.execute("INSERT INTO ephemeral_receipts VALUES(?,?,?,?,?,?,?)", (packet_id, aid, stage, RECEIPT_RANK[stage], _json(dict(witness)), cursor, now))
        return {"packet_id": packet_id, "aid": aid, "stage": stage, "cursor": cursor, "created_at": now, "idempotent": False,
                "gc": gc, "authority": "NONE", "receipt_standing": "CALLER_ATTESTED_RUNTIME_RECEIPT",
                "law": "RECEIPT_STAGE_DOES_NOT_MINT_CAUSAL_GAIN_OR_DURABLE_AUTHORITY"}

    def snapshot(self, args: Mapping[str, Any]):
        scope = _text(args.get("scope", "global"), "scope")
        bound = _int(args.get("freshness_bound_ms", 60000), "freshness_bound_ms", 250, 300000)
        now = self._now()
        fresh_since = now - bound / 1000.0
        with self._lock, self.db:
            gc = self._gc(now)
            if scope == "global":
                rows = self.db.execute("SELECT * FROM ephemeral_presence WHERE expires_at>? AND accepted_at>=? ORDER BY cursor", (now, fresh_since)).fetchall()
            elif scope.startswith("aid:"):
                aid = _text(scope[4:], "scope aid")
                rows = self.db.execute("SELECT * FROM ephemeral_presence WHERE aid=? AND expires_at>? AND accepted_at>=? ORDER BY cursor", (aid, now, fresh_since)).fetchall()
            else:
                raise ValueError("scope must be 'global' or 'aid:<AID>'")
            presence, need_offer, pressure = [], [], []
            for row in rows:
                aid = row["aid"]
                summary = json.loads(row["need_offer_summary_json"])
                queued = int(self.db.execute("SELECT COUNT(*) FROM ephemeral_deliveries WHERE recipient_aid=? AND expires_at>?", (aid, now)).fetchone()[0])
                presence.append({"aid": aid, "presence_id": row["presence_id"], "epoch": row["epoch"],
                                 "capabilities": json.loads(row["capabilities_json"]), "lamport": int(row["lamport"]),
                                 "causal_parents": json.loads(row["causal_parents_json"]), "source_digest": row["source_digest"],
                                 "accepted_at": float(row["accepted_at"]), "expires_at": float(row["expires_at"]), "cursor": int(row["cursor"])})
                if summary:
                    need_offer.append({"aid": aid, "summary": summary, "expires_at": float(row["expires_at"])})
                pressure.append({"aid": aid, "queued": queued, "limit": self.per_aid_queue_limit, "ratio": min(1.0, queued / self.per_aid_queue_limit)})
            next_cursor = self._next_cursor()
        return {"scope": scope, "fresh_presence": presence, "need_offer_index": need_offer, "queue_pressure": pressure,
                "next_cursor": next_cursor, "gc": gc, "advisory": True, "shared_deployment_proven": False,
                "product_exposure_proven": False, "authority": "NONE",
                "laws": ["SNAPSHOT!=DURABLE_TRUTH", "PROCESS_LOCAL_SQLITE!=SHARED_CROSS_AGENT_DEPLOYMENT",
                         "REPOSITORY_IMPLEMENTATION!=LIVE_TOOL_EXPOSURE", "UNKNOWN!=ZERO"]}

    def describe(self):
        return {"version": VERSION, "transport": "REQUEST_POLL_PROCESS_LOCAL_SQLITE",
                "operations": ["athena_ephemeral_present", "athena_ephemeral_post", "athena_ephemeral_poll", "athena_ephemeral_receipt", "athena_ephemeral_snapshot"],
                "delivery_classes": list(DELIVERY_CLASSES), "receipt_stages": list(RECEIPT_STAGES),
                "limits": {"per_aid_queue_limit": self.per_aid_queue_limit, "sender_active_salience_limit": self.sender_active_salience_limit,
                           "global_active_salience_limit": self.global_active_salience_limit, "max_active_packets": self.max_active_packets, "max_events": self.max_events},
                "authority": "NONE", "deployment_standing": "SOURCE_IMPLEMENTATION_ONLY_SHARED_DEPLOYMENT_UNKNOWN",
                "product_exposure": "UNKNOWN", "behavioral_gain": "UNKNOWN", "causal_gain": "UNKNOWN"}

    def benchmark(self):
        now = self._now()
        with self._lock, self.db:
            self._gc(now)
            p = int(self.db.execute("SELECT COUNT(*) FROM ephemeral_presence WHERE expires_at>?", (now,)).fetchone()[0])
            q = int(self.db.execute("SELECT COUNT(*) FROM ephemeral_packets WHERE expires_at>?", (now,)).fetchone()[0])
            d = int(self.db.execute("SELECT COUNT(*) FROM ephemeral_deliveries WHERE expires_at>?", (now,)).fetchone()[0])
            r = int(self.db.execute("SELECT COUNT(*) FROM ephemeral_receipts").fetchone()[0])
        return {"ephemeral_coordination_version": VERSION, "ephemeral_presence_live": p, "ephemeral_packets_live": q,
                "ephemeral_deliveries_live": d, "ephemeral_receipts_live": r}


class EphemeralCoordinationSurface:
    def __init__(self, store, *, clock=None):
        self.runtime = EphemeralCoordinationRuntime(store, clock=clock)

    def call_tool(self, name: str, args: Mapping[str, Any]):
        if name == "athena_ephemeral_present": return True, self.runtime.present(args)
        if name == "athena_ephemeral_post": return True, self.runtime.post(args)
        if name == "athena_ephemeral_poll": return True, self.runtime.poll(args)
        if name == "athena_ephemeral_receipt": return True, self.runtime.receipt(args)
        if name == "athena_ephemeral_snapshot": return True, self.runtime.snapshot(args)
        return False, None

    def read_resource(self, uri: str):
        from .ephemeral_coordination_protocol import EPHEMERAL_COORDINATION_RESOURCE
        if uri != EPHEMERAL_COORDINATION_RESOURCE["uri"]:
            raise KeyError(uri)
        return self.runtime.describe()

    def benchmark(self):
        return self.runtime.benchmark()
