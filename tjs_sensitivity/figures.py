"""
Figure generator for the TJS κ-sensitivity simulation.

Reads:
    outputs/tables/sensitivity_full_grid.csv
    outputs/tables/sensitivity_main_pi_010.csv

Writes:
    outputs/figures/figure_main_kappa_outcomes.png
    outputs/figures/figure_supp_kappa_pi_grid.png

NON-VALIDATION DISCLAIMER
-------------------------
Figures depict simulated outcomes under stated modelling assumptions.
They do not depict κ values from any real institutional setting or
governance metric. See ``docs/non_validation_disclaimer.md``.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parent.parent
# WS-2.6 Phase 11 fix: paths under outputs/sensitivity/ per the WS-2.6 structural
# mapping (Walter Phase 3.3 ack). See simulation.py for full rationale.
TABLES_DIR = REPO_ROOT / "outputs" / "sensitivity" / "tables"
FIGURES_DIR = REPO_ROOT / "outputs" / "sensitivity" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

PNG_SAVE_KWARGS = {
    "dpi": 150,
    "metadata": {"Software": "Matplotlib"},
    "pil_kwargs": {"compress_level": 9, "optimize": False},
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with open(path) as f:
        return list(csv.DictReader(f))


def _to_float(rows: list[dict[str, str]], cols: list[str]) -> dict[str, list[float]]:
    out: dict[str, list[float]] = {c: [] for c in cols}
    for r in rows:
        for c in cols:
            out[c].append(float(r[c]))
    return out


def figure_main(main_csv: Path, out_path: Path) -> None:
    """Main-text figure: κ on x-axis, four outcomes on stacked panels (π=0.10)."""
    rows = _read_csv(main_csv)
    rows.sort(key=lambda r: float(r["target_kappa"]))
    cols = [
        "target_kappa",
        "unsafe_secondary_rate_mean",
        "unsafe_secondary_rate_mcse",
        "over_escalation_rate_mean",
        "over_escalation_rate_mcse",
        "net_primary_rate_mean",
        "net_primary_rate_mcse",
        "over_escalation_burden_hours_per_100_mean",
        "over_escalation_burden_hours_per_100_mcse",
    ]
    data = _to_float(rows, cols)
    k = data["target_kappa"]

    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    fig.suptitle(
        "Simulated governance outcomes vs target κ (π_Primary = 0.10)\n"
        "Sensitivity analysis under stated modelling assumptions; not empirical.",
        fontsize=10,
    )

    panels = [
        (
            axes[0, 0],
            "Unsafe-Secondary rate",
            data["unsafe_secondary_rate_mean"],
            data["unsafe_secondary_rate_mcse"],
            "P(adjudicated = Secondary | latent Primary)",
        ),
        (
            axes[0, 1],
            "Over-escalation rate",
            data["over_escalation_rate_mean"],
            data["over_escalation_rate_mcse"],
            "P(adjudicated = Primary | latent Secondary)",
        ),
        (
            axes[1, 0],
            "Net Primary rate",
            data["net_primary_rate_mean"],
            data["net_primary_rate_mcse"],
            "P(adjudicated = Primary)",
        ),
        (
            axes[1, 1],
            "Documentation burden",
            data["over_escalation_burden_hours_per_100_mean"],
            data["over_escalation_burden_hours_per_100_mcse"],
            "Extra hours / 100 thresholds",
        ),
    ]
    for ax, title, mean, mcse, ylabel in panels:
        ax.errorbar(
            k, mean, yerr=mcse, marker="o", linestyle="-", capsize=3
        )
        ax.set_title(title, fontsize=10)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.grid(True, alpha=0.3)
        # Mark κ = 0.40 (falsification) and κ = 0.60 (target) regimes
        ax.axvline(0.40, color="red", linestyle="--", alpha=0.4, linewidth=0.8)
        ax.axvline(0.60, color="green", linestyle="--", alpha=0.4, linewidth=0.8)

    for ax in axes[1, :]:
        ax.set_xlabel("Target κ (Negative Harm Test)", fontsize=9)

    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out_path, **PNG_SAVE_KWARGS)
    plt.close(fig)


def figure_supp(full_csv: Path, out_path: Path) -> None:
    """Supplement figure: unsafe-Secondary across full π × κ grid."""
    rows = _read_csv(full_csv)
    cols_needed = [
        "target_kappa",
        "base_rate_primary",
        "unsafe_secondary_rate_mean",
        "unsafe_secondary_rate_mcse",
    ]
    data = []
    for r in rows:
        data.append(
            {
                "kappa": float(r["target_kappa"]),
                "pi": float(r["base_rate_primary"]),
                "mean": float(r["unsafe_secondary_rate_mean"]),
                "mcse": float(r["unsafe_secondary_rate_mcse"]),
            }
        )

    pis = sorted({d["pi"] for d in data})
    fig, ax = plt.subplots(figsize=(9, 6))
    fig.suptitle(
        "Simulated unsafe-Secondary rate vs κ across base-rate scenarios\n"
        "Sensitivity analysis under stated modelling assumptions; not empirical.",
        fontsize=10,
    )
    for pi in pis:
        sub = sorted([d for d in data if d["pi"] == pi], key=lambda x: x["kappa"])
        ks = [d["kappa"] for d in sub]
        means = [d["mean"] for d in sub]
        mcses = [d["mcse"] for d in sub]
        ax.errorbar(
            ks, means, yerr=mcses, marker="o", linestyle="-",
            capsize=3, label=f"π = {pi:.2f}",
        )
    ax.axvline(0.40, color="red", linestyle="--", alpha=0.4, linewidth=0.8,
               label="κ = 0.40 (falsification)")
    ax.axvline(0.60, color="green", linestyle="--", alpha=0.4, linewidth=0.8,
               label="κ = 0.60 (illustrative target)")
    ax.set_xlabel("Target κ (Negative Harm Test)")
    ax.set_ylabel("P(adjudicated = Secondary | latent Primary)")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out_path, **PNG_SAVE_KWARGS)
    plt.close(fig)


def main() -> None:
    main_csv = TABLES_DIR / "sensitivity_main_pi_010.csv"
    full_csv = TABLES_DIR / "sensitivity_full_grid.csv"
    figure_main(main_csv, FIGURES_DIR / "figure_main_kappa_outcomes.png")
    figure_supp(full_csv, FIGURES_DIR / "figure_supp_kappa_pi_grid.png")
    print(f"[figures] wrote main and supplement figures to {FIGURES_DIR}")


if __name__ == "__main__":
    main()
