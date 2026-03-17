import tempfile
import unittest
from pathlib import Path

from aqm.apps.planet9.qphi import QPHIConfig, run_qphi
from aqm.apps.planet9.tno_data import demo_extreme_tnos


class TestDeterminism(unittest.TestCase):
    def test_run_is_deterministic_under_seed(self) -> None:
        """Same (data, config, seed) should yield the same outputs."""
        tnos = demo_extreme_tnos(seed=9)

        with tempfile.TemporaryDirectory() as tmp:
            out1 = Path(tmp) / "run1"
            out2 = Path(tmp) / "run2"

            cfg_common = dict(
                seed=42,
                n_initial=4000,
                elite_keep=120,
                refine_rounds=1,
                offspring_per_elite=10,
                store_dir=None,
            )

            s1 = run_qphi(tnos, QPHIConfig(out_dir=str(out1), **cfg_common))
            s2 = run_qphi(tnos, QPHIConfig(out_dir=str(out2), **cfg_common))

            # Digests should match exactly.
            self.assertEqual(s1["cfg_digest"], s2["cfg_digest"])
            self.assertEqual(s1["tno_digest"], s2["tno_digest"])

            # Key numeric outputs should match closely.
            for k in [
                "best_log_score",
                "sky_center_ra_deg",
                "sky_center_dec_deg",
                "containment_radius_50_deg",
                "containment_radius_90_deg",
            ]:
                self.assertAlmostEqual(float(s1[k]), float(s2[k]), places=10)

            # Output files exist.
            for p in [
                out1 / "summary.json",
                out1 / "candidates.csv",
                out1 / "sky_samples.csv",
            ]:
                self.assertTrue(p.exists(), f"missing output file: {p}")


if __name__ == "__main__":
    unittest.main()
