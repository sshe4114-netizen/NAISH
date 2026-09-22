from __future__ import annotations

from pathlib import Path

import numpy as np

HEADER = "monthly_cash_flow_sar,registration_age_months,defaulted\n"


def generate_dataset(output_path: Path, rows: int = 4000, seed: int = 113) -> None:
    rng = np.random.default_rng(seed)
    cash_flow = rng.uniform(-50_000, 250_000, size=rows)
    age_months = rng.integers(1, 241, size=rows)

    cash_scaled = cash_flow / 50_000
    age_scaled = age_months / 24
    logit = 1.7 - 0.85 * cash_scaled - 0.38 * age_scaled
    probability = 1.0 / (1.0 + np.exp(-logit))
    defaulted = rng.binomial(1, probability)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        file.write(HEADER)
        for cash, age, target in zip(cash_flow, age_months, defaulted, strict=True):
            file.write(f"{cash:.2f},{int(age)},{int(target)}\n")


if __name__ == "__main__":
    generate_dataset(Path("data/nasih_training.csv"))
