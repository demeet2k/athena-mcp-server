import torch
import torch.nn as nn

from qpgemm import QPGEMMConfig, QPGEMMEngine, QPLinear, optimize_vision_model


def test_engine_dense_vs_lowrank():
    torch.manual_seed(0)
    W = torch.randn(128, 128)
    cfg = QPGEMMConfig(energy_threshold=0.99, min_gain=0.30)
    engine = QPGEMMEngine(cfg)
    out = engine.analyze(W)
    assert out["strategy"] in ("dense", "lowrank")
    assert "stats" in out


def test_qplinear_shapes_and_forward():
    torch.manual_seed(0)
    lin = nn.Linear(64, 32, bias=True)
    x = torch.randn(10, 64)
    # Full rank should reconstruct close to exact (within numerical tolerance)
    qpl = QPLinear(lin, rank=min(lin.weight.shape), allow_bias=True)
    y0 = lin(x)
    y1 = qpl(x)
    rel = (y1 - y0).norm() / (y0.norm() + 1e-12)
    assert rel.item() < 1e-4


def test_optimize_replaces_linear():
    class Toy(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc1 = nn.Linear(64, 64)
            self.fc2 = nn.Linear(64, 64)

        def forward(self, x):
            return self.fc2(torch.relu(self.fc1(x)))

    m = Toy().eval()
    cfg = QPGEMMConfig(energy_threshold=0.90, min_gain=0.0)  # force lowrank more often
    m2 = optimize_vision_model(m, config=cfg, inplace=False)
    # At least one layer should be converted with such lenient settings.
    assert any(isinstance(mod, QPLinear) for mod in m2.modules())
