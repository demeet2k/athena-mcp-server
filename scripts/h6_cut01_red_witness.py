"""Static source-surface witness for ATHENA H6 CUT-01.

This is not treatment and does not assert that the six RED obligations are absent at runtime.
It only verifies that the frozen inventory branch remains bound to the expected constitutional base and that treatment files are not being introduced by this witness cartridge itself.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "spec/H6_EXECUTION_CUT01_RED_V1.json").read_text(encoding="utf-8"))
assert contract["artifact"] == "ATHENA.H6.EXECUTION.CUT01.RED.V1"
assert contract["treatment_code"] is False
assert contract["gids"] == [1, 2, 3, 4, 5, 6]
assert set(contract["stations"]) == {"H01", "H02", "H03", "H04", "H05", "H06"}
print(json.dumps({"status":"H6_CUT01_RED_CONTRACT_FROZEN","artifact":contract["artifact"],"runtime_base":contract["runtime_base"],"treatment_code":False}, sort_keys=True))
