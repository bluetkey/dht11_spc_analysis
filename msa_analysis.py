import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def run_msa(readings, warmup_subgroups=15, n=5):
    
    # Use only stable region 
    stable_start = warmup_subgroups * n
    stable_readings = readings[stable_start:]
    
    temperatures = [r[1] for r in stable_readings]
    humidities   = [r[2] for r in stable_readings]

    def msa_stats(data, name, unit):
        data = np.array(data)

        mean    = np.mean(data)
        std     = np.std(data, ddof=1)
        std_total = np.std(np.array([r[1] for r in readings] if name == "Temperature" else [r[2] for r in readings]), ddof=1)
        
        gauge_rr_pct = (std / std_total) * 100
        ndc          = 1.41 * (std_total / std) if std > 0 else float('inf')
        
        # Verdict 
        if gauge_rr_pct < 10:
            verdict = "EXCELLENT ✓"
            color   = "green"
        elif gauge_rr_pct < 30:
            verdict = "ACCEPTABLE ⚠"
            color   = "orange"
        else:
            verdict = "UNACCEPTABLE ✗"
            color   = "red"

        # Normality test (Shapiro-Wilk)
        shapiro_stat, shapiro_p = stats.shapiro(data[:50])  # max 50 samples for Shapiro

        # Cp / Cpk (assume ±2 unit spec limits around mean) 
        spec_range = 2.0
        usl = mean + spec_range
        lsl = mean - spec_range
        cp  = (usl - lsl) / (6 * std) if std > 0 else float('inf')
        cpk = min((usl - mean), (mean - lsl)) / (3 * std) if std > 0 else float('inf')

        print(f"\n{'='*50}")
        print(f"  MSA Results — {name}")
        print(f"{'='*50}")
        print(f"  Stable readings used : {len(data)}")
        print(f"  Mean                 : {mean:.2f} {unit}")
        print(f"  Std Dev (repeatability): {std:.4f} {unit}")
        print(f"  Total Std Dev        : {std_total:.4f} {unit}")
        print(f"  % Gauge R&R          : {gauge_rr_pct:.2f}%  → {verdict}")
        print(f"  NDC                  : {ndc:.1f}  (need ≥5 for good resolution)")
        print(f"  Normality (Shapiro-Wilk p): {shapiro_p:.4f} {'✓ Normal' if shapiro_p > 0.05 else '✗ Non-normal'}")
        print(f"  Cp                   : {cp:.2f}  (spec ±{spec_range}{unit})")
        print(f"  Cpk                  : {cpk:.2f}")
        print(f"{'='*50}")

        return {
            "name": name, "unit": unit, "mean": mean, "std": std,
            "gauge_rr_pct": gauge_rr_pct, "ndc": ndc,
            "cp": cp, "cpk": cpk, "verdict": verdict,
            "color": color, "data": data,
            "usl": usl, "lsl": lsl
        }

    t_msa = msa_stats(temperatures, "Temperature", "°C")
    h_msa = msa_stats(humidities,   "Humidity",    "%")

    # plots 
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle("Measurement System Analysis (MSA) — Stable Region Only", fontsize=13, fontweight="bold")

    for row, msa in enumerate([t_msa, h_msa]):
        data  = msa["data"]
        name  = msa["name"]
        unit  = msa["unit"]
        color = msa["color"]

        # 1. Run chart (individual measurements over time) 
        ax = axes[row][0]
        ax.plot(data, color="steelblue" if row else "tomato", linewidth=1, marker="o", markersize=2)
        ax.axhline(msa["mean"],          color="green", linestyle="--", linewidth=1.5, label=f"Mean = {msa['mean']:.2f}")
        ax.axhline(msa["mean"] + 3*msa["std"], color="red", linestyle=":", linewidth=1.2, label="±3σ")
        ax.axhline(msa["mean"] - 3*msa["std"], color="red", linestyle=":", linewidth=1.2)
        ax.set_title(f"{name} — Run Chart")
        ax.set_xlabel("Reading #")
        ax.set_ylabel(unit)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        # 2. Histogram with normal curve 
        ax = axes[row][1]
        ax.hist(data, bins=15, color="steelblue" if row else "tomato", edgecolor="white", density=True, alpha=0.7)
        x = np.linspace(data.min(), data.max(), 200)
        ax.plot(x, stats.norm.pdf(x, msa["mean"], msa["std"]), color="black", linewidth=2, label="Normal fit")
        ax.axvline(msa["usl"], color="red",   linestyle="--", linewidth=1.5, label=f"USL={msa['usl']:.1f}")
        ax.axvline(msa["lsl"], color="red",   linestyle="--", linewidth=1.5, label=f"LSL={msa['lsl']:.1f}")
        ax.set_title(f"{name} — Distribution")
        ax.set_xlabel(unit)
        ax.set_ylabel("Density")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        # 3. Gauge R&R summary bar 
        ax = axes[row][2]
        categories = ["% Gauge R&R", "% Part Variation"]
        values     = [msa["gauge_rr_pct"], 100 - msa["gauge_rr_pct"]]
        bar_colors = [color, "steelblue"]
        bars = ax.bar(categories, values, color=bar_colors, edgecolor="white", width=0.4)
        ax.axhline(10, color="green",  linestyle="--", linewidth=1, label="10% threshold (excellent)")
        ax.axhline(30, color="orange", linestyle="--", linewidth=1, label="30% threshold (acceptable)")
        ax.set_ylim(0, 110)
        ax.set_title(f"{name} — Gauge R&R Summary")
        ax.set_ylabel("%")
        ax.legend(fontsize=7)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f"{val:.1f}%", ha="center", fontsize=10, fontweight="bold")
        # verdict label
        ax.text(0.5, 0.92, msa["verdict"], transform=ax.transAxes,
                ha="center", fontsize=11, fontweight="bold", color=color)
        ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig("msa_analysis.png", dpi=150)
    plt.show()
    print("\nMSA charts saved to 'msa_analysis.png'")

    return t_msa, h_msa

#run it 
t_msa, h_msa = run_msa(readings, warmup_subgroups=15)
