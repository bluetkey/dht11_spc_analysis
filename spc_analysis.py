import numpy as np
import csv
import numpy as np
import matplotlib.pyplot as plt

# load data from CSV
readings = []
with open("sensor_data.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        readings.append((int(row["index"]), float(row["temperature"]), float(row["humidity"])))

print(f"Loaded {len(readings)} readings")

# paste the plot_data() function here, then call it:
plot_data(readings)

def plot_data(readings, warmup_subgroups=15):
    indices      = [r[0] for r in readings]
    temperatures = [r[1] for r in readings]
    humidities   = [r[2] for r in readings]

    def subgroup_stats(data, n=5):
        groups = [data[i:i+n] for i in range(0, len(data) - len(data) % n, n)]
        means  = [np.mean(g) for g in groups]
        ranges = [max(g) - min(g) for g in groups]
        return means, ranges

    #define constants
    n  = 5
    A2 = 0.577
    D3 = 0.0
    D4 = 2.114

    t_means, t_ranges = subgroup_stats(temperatures, n)
    h_means, h_ranges = subgroup_stats(humidities, n)
    sg_indices = list(range(1, len(t_means) + 1))

    # Exclude the warmup subgroups to calculate the limits with the stable readings
    t_means_stable  = t_means[warmup_subgroups:]
    t_ranges_stable = t_ranges[warmup_subgroups:]
    h_means_stable  = h_means[warmup_subgroups:]
    h_ranges_stable = h_ranges[warmup_subgroups:]

    #X-double-bar and R-bar for temp and hum
    tx_bar   = np.mean(t_means_stable);  tr_bar   = np.mean(t_ranges_stable)
    hx_bar  = np.mean(h_means_stable);  hr_bar  = np.mean(h_ranges_stable)

    #UCL and LCL for temp and hum
    t_ucl_x = tx_bar  + A2 * tr_bar;     t_lcl_x = tx_bar  - A2 * tr_bar
    t_ucl_r = D4 * tr_bar;              t_lcl_r = D3 * tr_bar
    h_ucl_x = hx_bar + A2 * hr_bar;    h_lcl_x = hx_bar - A2 * hr_bar
    h_ucl_r = D4 * hr_bar;             h_lcl_r = D3 * hr_bar

    fig, axes = plt.subplots(4, 1, figsize=(14, 16))
    fig.suptitle("DHT11 Sensor — SPC Analysis (Warm-up Excluded)", fontsize=14, fontweight="bold")

    #grey out the warm-up region on any axis
    def add_warmup_shade(ax):
        ax.axvspan(1, warmup_subgroups + 0.5, color="grey", alpha=0.15, label=f"Warm-up (excl. from limits)")

    #mark out-of-control points with a black X
    def mark_ooc(ax, indices, values, ucl, lcl):
        for i, v in zip(indices, values):
            if v > ucl or v < lcl:
                ax.plot(i, v, marker="x", color="black", markersize=10, zorder=5)

    # Temperature X-bar chart 
    ax1 = axes[0]
    ax1.plot(sg_indices, t_means, marker="o", color="tomato", linewidth=1.5, markersize=4, label="Subgroup Mean")
    ax1.axhline(tx_bar,   color="green", linewidth=1.5, linestyle="--", label=f"X̄ = {tx_bar:.2f}")
    ax1.axhline(t_ucl_x, color="red",   linewidth=1.2, linestyle=":",  label=f"UCL = {t_ucl_x:.2f}")
    ax1.axhline(t_lcl_x, color="red",   linewidth=1.2, linestyle=":",  label=f"LCL = {t_lcl_x:.2f}")
    add_warmup_shade(ax1)
    mark_ooc(ax1, sg_indices[warmup_subgroups:], t_means[warmup_subgroups:], t_ucl_x, t_lcl_x)
    ax1.set_title("Temperature — X̄ Chart")
    ax1.set_ylabel("°C")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Temperature R chart
    ax2 = axes[1]
    ax2.plot(sg_indices, t_ranges, marker="o", color="orange", linewidth=1.5, markersize=4, label="Subgroup Range")
    ax2.axhline(tr_bar,   color="green", linewidth=1.5, linestyle="--", label=f"R̄ = {tr_bar:.2f}")
    ax2.axhline(t_ucl_r, color="red",   linewidth=1.2, linestyle=":",  label=f"UCL = {t_ucl_r:.2f}")
    ax2.axhline(t_lcl_r, color="red",   linewidth=1.2, linestyle=":",  label=f"LCL = {t_lcl_r:.2f}")
    add_warmup_shade(ax2)
    mark_ooc(ax2, sg_indices[warmup_subgroups:], t_ranges[warmup_subgroups:], t_ucl_r, t_lcl_r)
    ax2.set_title("Temperature — R Chart")
    ax2.set_ylabel("Range (°C)")
    ax2.set_xlabel("Subgroup #")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    # Humidity X-bar chart 
    ax3 = axes[2]
    ax3.plot(sg_indices, h_means, marker="o", color="steelblue", linewidth=1.5, markersize=4, label="Subgroup Mean")
    ax3.axhline(hx_bar,  color="green", linewidth=1.5, linestyle="--", label=f"X̄ = {hx_bar:.2f}")
    ax3.axhline(h_ucl_x, color="red",   linewidth=1.2, linestyle=":",  label=f"UCL = {h_ucl_x:.2f}")
    ax3.axhline(h_lcl_x, color="red",   linewidth=1.2, linestyle=":",  label=f"LCL = {h_lcl_x:.2f}")
    add_warmup_shade(ax3)
    mark_ooc(ax3, sg_indices[warmup_subgroups:], h_means[warmup_subgroups:], h_ucl_x, h_lcl_x)
    ax3.set_title("Humidity — X̄ Chart")
    ax3.set_ylabel("%")
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    # Humidity R chart 
    ax4 = axes[3]
    ax4.plot(sg_indices, h_ranges, marker="o", color="mediumpurple", linewidth=1.5, markersize=4, label="Subgroup Range")
    ax4.axhline(hr_bar,  color="green", linewidth=1.5, linestyle="--", label=f"R̄ = {hr_bar:.2f}")
    ax4.axhline(h_ucl_r, color="red",   linewidth=1.2, linestyle=":",  label=f"UCL = {h_ucl_r:.2f}")
    ax4.axhline(h_lcl_r, color="red",   linewidth=1.2, linestyle=":",  label=f"LCL = {h_lcl_r:.2f}")
    add_warmup_shade(ax4)
    mark_ooc(ax4, sg_indices[warmup_subgroups:], h_ranges[warmup_subgroups:], h_ucl_r, h_lcl_r)
    ax4.set_title("Humidity — R Chart")
    ax4.set_ylabel("Range (%)")
    ax4.set_xlabel("Subgroup #")
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("spc_charts.png", dpi=150)
    plt.show()
    print("SPC charts saved to 'spc_charts.png'")

# run it
plot_data(readings, warmup_subgroups=15)