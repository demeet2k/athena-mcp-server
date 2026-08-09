import importlib
import tempfile
import unittest

from athena_mcp.bootstrap import bootstrap
from athena_mcp.core import AthenaCore
from athena_mcp.crystal_runtime import CrystalRuntime
from athena_mcp.h6_root import H6RootRuntime
from athena_mcp.promotion import PromotionLedger
from athena_mcp.store import Store


GAP_ID = "IC10G01_ORDERED_GATE_CHAIN"
HEAD = "HEAD.IC10.RED"


class IC10GateChainRed(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.store = Store(self.tmp.name)
        self.core = AthenaCore(self.store)
        bootstrap(self.core)
        self.crystal = CrystalRuntime(self.core)
        self.h6 = H6RootRuntime(self.core, self.crystal)
        self.promotion = PromotionLedger(self.core)

    def tearDown(self):
        self.store.close()
        self.tmp.close()

    def test_promotion2_qualifies_runtime_contract_without_full_ic10_vector(self):
        ci = {"observed": True, "ref": "CI.IC10.RED", "head_sha": HEAD, "conclusion": "success"}
        smoke = {"observed": True, "ref": "SMOKE.IC10.RED", "head_sha": HEAD, "conclusion": "success"}
        trusted = {
            "observed": True,
            "verifier": "TEST.TRUSTED.HOST",
            "verification_ref": "VERIFY.IC10.RED",
            "head_sha": HEAD,
            "ci_ref": ci["ref"],
            "smoke_ref": smoke["ref"],
        }
        cert = self.promotion.evaluate(
            "Server",
            HEAD,
            {"surface_status": "PASS", "composition": {"status": "PASS"}},
            ci,
            smoke,
            local_git_status={"enabled": False},
            trusted_external_verification=trusted,
            persist=False,
        )

        # Parent fact: PROMOTION.2 is a real trusted exact-head runtime gate and
        # can become QUALIFIED, but its gate vocabulary is not the constitutional
        # IC10 I01..I10 chain.
        self.assertEqual(cert["status"], "QUALIFIED")
        self.assertTrue(cert["promotion_allowed"])
        self.assertNotIn("I03_TYPE_UNIT_CARRIER", cert["gates"])
        self.assertNotIn("I05_INVARIANT_PRESERVATION", cert["gates"])
        self.assertNotIn("I08_BRIDGE_GLUING_RETURN_DEFECT", cert["gates"])
        self.assertNotIn("I09_AUDIT_REPLAY_COMPLETENESS", cert["gates"])

        try:
            module = importlib.import_module("athena_mcp.ic10_runtime")
        except ModuleNotFoundError:
            self.fail(
                f"{GAP_ID}: PROMOTION.2 exists and qualifies its bounded runtime contract, "
                "but no constitutional athena_mcp.ic10_runtime.IC10Compiler maps I01-I09 "
                "obligations plus the existing I10 promotion receipt into one ordered decision"
            )
        cls = getattr(module, "IC10Compiler", None)
        if cls is None:
            self.fail(f"{GAP_ID}: athena_mcp.ic10_runtime exists but IC10Compiler is absent")


if __name__ == "__main__":
    unittest.main()
