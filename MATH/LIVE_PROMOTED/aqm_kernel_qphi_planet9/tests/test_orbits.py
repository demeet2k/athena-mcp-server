import unittest

import numpy as np

from aqm.apps.planet9.orbits import OrbitalElements, ecliptic_to_radec_deg, wrap_angle_deg


class TestOrbits(unittest.TestCase):
    def test_wrap_angle_deg(self) -> None:
        self.assertAlmostEqual(wrap_angle_deg(0.0), 0.0)
        self.assertAlmostEqual(wrap_angle_deg(360.0), 0.0)
        self.assertAlmostEqual(wrap_angle_deg(-10.0), 350.0)

    def test_simple_circular_orbit_points_to_ra0_dec0(self) -> None:
        e = OrbitalElements(a_au=100.0, e=0.0, i_deg=0.0, Omega_deg=0.0, omega_deg=0.0, M_deg=0.0)
        r = e.position_vector()
        self.assertTrue(np.allclose(r, np.array([100.0, 0.0, 0.0]), atol=1e-8))
        ra, dec = ecliptic_to_radec_deg(r)
        self.assertAlmostEqual(float(ra), 0.0, places=8)
        self.assertAlmostEqual(float(dec), 0.0, places=8)


if __name__ == "__main__":
    unittest.main()
