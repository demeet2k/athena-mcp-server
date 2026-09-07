import copy
import json
import os
import tempfile
import unittest

from athena_mcp.mythos_kernel import (
    MythosVM, atlas, benchmark, bridge, compare_modules, encode_index, isomorphism_classes, lint_steps,
    service_matrix, signature_of, unify, validate_module, validate_modules,
)
from athena_mcp.mythos_modules import MODULE_INDEX, MODULES
from athena_mcp.mythos_protocol import FAMILIES, MYTHOS_RESOURCES, MYTHOS_TOOL_NAMES, MYTHOS_TOOLS, RITE_OPCODES, SERVICES
from athena_mcp.mythos_surface import ATHENA_ORGAN_MAP, MythosSurface

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(ROOT, "spec", "MYTHOS_OS_V1.json")


class Schema(unittest.TestCase):
    def test_registry_validates(self):
        self.assertEqual(validate_modules(MODULES), [])

    def test_every_module_has_twelve_graded_slots_and_sources(self):
        for m in MODULES:
            self.assertEqual(set(m["services"]), set(SERVICES), m["id"])
            self.assertTrue(m["sources"], m["id"])
            self.assertIn(m["family"], FAMILIES)

    def test_validator_catches_defects(self):
        base = copy.deepcopy(MODULE_INDEX["babylon"])
        bad = copy.deepcopy(base); bad["services"]["RITE"]["protocols"][0]["steps"].append("DANCE")
        self.assertTrue(any("opcode" in e for e in validate_module(bad)))
        bad = copy.deepcopy(base); bad["services"]["BOOT"]["stages"][0]["stage"] = "GENESIS"
        self.assertTrue(any("stage" in e for e in validate_module(bad)))
        bad = copy.deepcopy(base); bad["standing"] = "MODERN_RECONSTRUCTION"
        for s in SERVICES:
            bad["services"][s].pop("src", None)
        self.assertTrue(any("🟢 requires" in e for e in validate_module(bad)))
        bad = copy.deepcopy(base); bad["services"]["ORACLE"] = {"grade": "⊥", "absent": True, "devices": []}
        self.assertTrue(any("absent slot carries content" in e for e in validate_module(bad)))
        bad = copy.deepcopy(base); bad["services"]["RING"]["rings"][1]["level"] = 0
        self.assertTrue(any("unique" in e for e in validate_module(bad)))
        bad = copy.deepcopy(base); bad["services"]["PROC"]["agents"][0]["parent"] = "Nobody"
        self.assertTrue(any("is not an agent" in e for e in validate_module(bad)))

    def test_families_and_athena_present(self):
        fams = {m["family"] for m in MODULES}
        self.assertIn("NEAR_EAST", fams)
        self.assertIn("ENGINEERED", fams)
        self.assertIn("athena", MODULE_INDEX)
        self.assertIn("babylon", MODULE_INDEX)


class VM(unittest.TestCase):
    def test_every_module_runs_every_op(self):
        for m in MODULES:
            out = MythosVM(m).run_all()
            for op in ("boot", "memmap", "spawn", "tick", "invoke", "divine", "raise", "judge"):
                self.assertIn("status", out[op], (m["id"], op))
                self.assertEqual(out[op]["execution_authority"], "NONE", (m["id"], op))
            self.assertEqual(set(out["signature"]), set(SERVICES))

    def test_boot_fault_position(self):
        b = MythosVM(MODULE_INDEX["babylon"]).boot()
        self.assertEqual(b["status"], "BOOTED")
        self.assertEqual(b["fault_position"], "PRE_POPULATION")
        a = MythosVM(MODULE_INDEX["athena"]).boot()
        self.assertEqual(a["fault_position"], "POST_POPULATION")

    def test_ring_gate_and_high_stakes_hold(self):
        vm = MythosVM(MODULE_INDEX["babylon"])
        self.assertEqual(vm.invoke(None, caller_ring=3)["status"], "HOLD_RING")
        self.assertEqual(vm.invoke(None, caller_ring=0)["status"], "SIMULATED_RITE")
        self.assertEqual(vm.invoke(None, caller_ring=0, use_case="MEDICAL")["status"], "HOLD_SAFETY_CRITICAL_USE")
        self.assertEqual(vm.invoke("nope", caller_ring=0)["status"], "HOLD_UNKNOWN_RITE")

    def test_oracle_is_seeded_deterministic_and_gated(self):
        vm = MythosVM(MODULE_INDEX["babylon"])
        self.assertEqual(vm.divine(None)["status"], "HOLD_SAMPLE_REQUIRED")
        self.assertEqual(vm.divine(None, seed="a"), vm.divine(None, seed="a"))
        d = vm.divine(None, seed="a")
        self.assertEqual(d["status"], "SYMBOLIC_ONLY")
        self.assertLess(d["R_sampler"]["index"], d["sample_space"])
        self.assertEqual(vm.divine(None, seed="a", use_case="FINANCIAL")["status"], "HOLD_SAFETY_CRITICAL_USE")
        self.assertEqual(vm.divine(None, sample=5)["R_sampler"]["index"], 5 % d["sample_space"])

    def test_fault_handlers_and_reboot_link(self):
        r = MythosVM(MODULE_INDEX["babylon"]).raise_fault("the noise of humankind")
        self.assertEqual(r["outcome"], "REBOOT")
        self.assertTrue(r["reboot_event"])
        self.assertEqual(r["trace"][0], "RAISE:COSMIC:the noise of humankind")

    def test_ledger_models_map_scores(self):
        j = MythosVM(MODULE_INDEX["athena"]).judge(1.0)
        self.assertEqual(j["destination"], "# canonical")
        j = MythosVM(MODULE_INDEX["athena"]).judge(-1.0)
        self.assertEqual(j["destination"], "? registered")
        j = MythosVM(MODULE_INDEX["babylon"]).judge(0.3)
        self.assertEqual(j["model"], "NONE")

    def test_clock_tick_counts_rollovers_and_festivals(self):
        t = MythosVM(MODULE_INDEX["babylon"]).tick(19 * 355)
        year = next(p for p in t["periods"] if p["name"].startswith("year"))
        self.assertEqual(year["rollovers"], 19)
        self.assertEqual(t["intercalation"]["intercalations_due"], 7)
        akitu = next(f for f in t["festivals"] if f["name"].startswith("Akītu (New Year)"))
        self.assertEqual(akitu["fired"], 20)

    def test_lint_rules(self):
        self.assertTrue(lint_steps(["PURIFY", "BOUND", "INVOKE", "OFFER", "RECEIVE", "CLOSE"])["well_formed"])
        bad = lint_steps(["INVOKE", "BOUND", "CLOSE", "OFFER"])
        self.assertFalse(bad["well_formed"])
        self.assertIn("BOUND after INVOKE", bad["violations"])
        self.assertIn("OFFER after CLOSE", bad["violations"])
        self.assertIn("INVOKE without CLOSE/RELEASE", lint_steps(["INVOKE"])["violations"])
        for op in RITE_OPCODES:
            self.assertTrue(op.isupper())

    def test_encode_index(self):
        self.assertEqual(encode_index(5, 64, "BINARY")["digits"], "000101")
        self.assertEqual(encode_index(5, 64, "BINARY")["width"], 6)
        self.assertEqual(encode_index(7, 16, "QUATERNARY")["digits"], "13")
        self.assertEqual(encode_index(3, 4, "TERNARY")["radix"], 3)


class Unification(unittest.TestCase):
    def test_signature_has_twelve_tokens(self):
        for m in MODULES:
            sig = signature_of(m)
            self.assertEqual(list(sig), list(SERVICES))

    def test_matrix_and_classes(self):
        mat = service_matrix(MODULES)
        self.assertEqual(mat["module_count"], len(MODULES))
        for s in SERVICES:
            classes = isomorphism_classes(MODULES, s)
            self.assertEqual(sum(c["size"] for c in classes), len(MODULES))

    def test_bridge_is_lossy_never_identity(self):
        for m in MODULES:
            if m["id"] == "athena":
                continue
            br = bridge(MODULE_INDEX["athena"], m)
            self.assertIn(br["strata"]["status"], {"BRIDGE_ALLOWED_WITH_LOSS", "HOLD_STANDING_ESCALATION"})
            self.assertFalse(br["identity_equivalence"])
            self.assertFalse(br["strata"]["identity_equivalence"])
            self.assertFalse(br["strata"]["semantic_equivalence"])

    def test_unify_and_compare(self):
        u = unify(MODULES, "BOOT", "babylon", "athena")
        self.assertIn("bridge", u)
        c = compare_modules(MODULE_INDEX["babylon"], MODULE_INDEX["athena"])
        self.assertEqual(c["of"], 12)
        self.assertFalse(c["identity_equivalence"])
        self.assertLessEqual(c["isomorphic_services"], 12)

    def test_atlas_is_144_cells_with_kc144_law(self):
        a = atlas(MODULES)
        self.assertEqual(a["count"], 144)
        for c in a["cells"]:
            self.assertEqual(c["gid"], 12 * (c["row"] - 1) + c["col"])
        occupied = sum(1 for c in a["cells"] if c["module_count"])
        self.assertGreaterEqual(occupied, 24)

    def test_benchmark_gates(self):
        b = benchmark(MODULES)
        self.assertTrue(b["schema_pass"])
        self.assertEqual(b["gates_passed"], b["gate_count"])
        self.assertTrue(b["lint_rejects_malformed"])
        self.assertTrue(b["lint_accepts_wellformed"])


class Surface(unittest.TestCase):
    def setUp(self):
        self.s = MythosSurface()

    def test_tools_and_resources_declared(self):
        self.assertEqual(len(MYTHOS_TOOLS), 6)
        self.assertEqual(len(MYTHOS_RESOURCES), 3)
        for t in MYTHOS_TOOLS:
            self.assertTrue(t["name"].startswith("athena_mythos_"))
            self.assertFalse(t["inputSchema"]["additionalProperties"])

    def test_catalog_module_run(self):
        handled, cat = self.s.call_tool("athena_mythos_catalog", {})
        self.assertTrue(handled)
        self.assertEqual(cat["module_count"], len(MODULES))
        handled, mod = self.s.call_tool("athena_mythos_module", {"module_id": "babylon", "service": "ORACLE"})
        self.assertEqual(mod["slot"]["devices"][0]["encoding"], "BINARY")
        handled, run = self.s.call_tool("athena_mythos_run", {"module_id": "babylon", "op": "boot"})
        self.assertEqual(run["status"], "BOOTED")
        handled, hold = self.s.call_tool("athena_mythos_run", {"module_id": "zzz", "op": "boot"})
        self.assertEqual(hold["status"], "HOLD_UNKNOWN_MODULE")
        handled, athena = self.s.call_tool("athena_mythos_athena", {"op": "signature"})
        self.assertEqual(athena["self_module"], "athena")
        self.assertEqual(set(athena["organ_map"]), set(SERVICES))
        self.assertIn("ATHENA_SELF_MODULE != ATHENA_AUTHORITY", athena["law"])
        self.assertIs(self.s.call_tool("athena_other", {})[0], False)

    def test_resources_read(self):
        main = self.s.read_resource("athena://mythos/os/v1")
        self.assertEqual(main["module_count"], len(MODULES))
        self.assertEqual(main["schema"]["violations"], 0)
        self.assertEqual(self.s.read_resource("athena://mythos/os/v1/atlas")["count"], 144)
        self.assertEqual(self.s.read_resource("athena://mythos/os/v1/matrix")["module_count"], len(MODULES))
        with self.assertRaises(KeyError):
            self.s.read_resource("athena://nope")


class Rpc(unittest.TestCase):
    def setUp(self):
        from athena_mcp.server import Server
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.server = Server(self.tmp.name)
        self.seq = 0

    def tearDown(self):
        self.server.store.close()
        self.tmp.close()

    def rpc(self, method, params=None):
        self.seq += 1
        m = {"jsonrpc": "2.0", "id": self.seq, "method": method}
        if params is not None:
            m["params"] = params
        return self.server.handle(m)

    def test_tools_listed_and_callable(self):
        names = {t["name"] for t in self.rpc("tools/list")["result"]["tools"]}
        self.assertTrue(MYTHOS_TOOL_NAMES <= names)
        from athena_mcp.aor_development_surface import AOR_DEVELOPMENT_TOOL_NAMES
        self.assertTrue(MYTHOS_TOOL_NAMES <= AOR_DEVELOPMENT_TOOL_NAMES)
        r = self.rpc("tools/call", {"name": "athena_mythos_run", "arguments": {"module_id": "athena", "op": "all"}})
        self.assertFalse(r["result"]["isError"], r)
        self.assertEqual(r["result"]["structuredContent"]["boot"]["status"], "BOOTED")
        r = self.rpc("tools/call", {"name": "athena_mythos_unify", "arguments": {"service": "LEDGER", "left": "babylon", "right": "athena"}})
        self.assertFalse(r["result"]["isError"], r)
        self.assertIn(r["result"]["structuredContent"]["bridge"]["strata"]["status"], {"BRIDGE_ALLOWED_WITH_LOSS", "HOLD_STANDING_ESCALATION"})
        r = self.rpc("tools/call", {"name": "athena_mythos_run", "arguments": {"module_id": "athena", "op": "teleport"}})
        self.assertTrue(r["result"]["isError"])

    def test_resources_listed_and_read(self):
        uris = {r["uri"] for r in self.rpc("resources/list")["result"]["resources"]}
        for res in MYTHOS_RESOURCES:
            self.assertIn(res["uri"], uris)
        v = json.loads(self.rpc("resources/read", {"uri": "athena://mythos/os/v1"})["result"]["contents"][0]["text"])
        self.assertEqual(v["benchmark"]["schema_pass"], True)
        self.assertEqual(set(v["athena_organ_map"]), set(ATHENA_ORGAN_MAP))


class SpecSync(unittest.TestCase):
    def test_spec_json_in_sync(self):
        from scripts.mythos_report import check_json
        self.assertTrue(os.path.exists(SPEC), "run `python -m scripts.mythos_report` to export the spec")
        self.assertTrue(check_json(), "run `python -m scripts.mythos_report` to re-export spec/MYTHOS_OS_V1.json")


if __name__ == "__main__":
    unittest.main()
