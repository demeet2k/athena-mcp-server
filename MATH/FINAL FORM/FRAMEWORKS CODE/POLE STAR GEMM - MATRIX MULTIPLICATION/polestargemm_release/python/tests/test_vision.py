import torch
import torch.nn as nn

from polestargemm.vision import PoleStarVisionConfig, optimize_model, validate_relative_error


class Toy(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(256, 512)
        self.act = nn.ReLU()
        self.fc2 = nn.Linear(512, 128)

    def forward(self, x):
        return self.fc2(self.act(self.fc1(x)))


def test_optimize_model_runs():
    torch.manual_seed(0)
    model = Toy().eval()
    x = torch.randn(8, 256)

    cfg = PoleStarVisionConfig(energy_threshold=0.95, min_gain=0.1, rank_multiple=1)
    model_opt, report = optimize_model(model, config=cfg, verbose=False)

    # Should produce an output of same shape
    y0 = model(x)
    y1 = model_opt(x)
    assert y0.shape == y1.shape

    err = validate_relative_error(model, model_opt, x, samples=3, device="cpu")
    assert err["mean_relative_error"] < 0.5  # loose: random weights can be not low-rank
