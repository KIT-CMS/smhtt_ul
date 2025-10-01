# plotting confidence intervals

from matplotlib import pyplot as plt
import numpy as np
import os
import mplhep as hep

hep.style.use("CMS")


##############################
# CL values for equal events
##############################
# tt
# Expected  2.5%: r < 7.2188
# Expected 16.0%: r < 9.7617
# Expected 50.0%: r < 14.0000
# Expected 84.0%: r < 20.3059
# Expected 97.5%: r < 28.3948
tt_cl_equal_events = [7.2188, 9.7617, 14.0000, 20.3059, 28.3948]

# mt
# Expected  2.5%: r < 10.8655
# Expected 16.0%: r < 14.8769
# Expected 50.0%: r < 21.5625
# Expected 84.0%: r < 31.6185
# Expected 97.5%: r < 44.6150
mt_cl_equal_events = [10.8655, 14.8769, 21.5625, 31.6185, 44.6150]

# et
# Expected  2.5%: r < 17.4624
# Expected 16.0%: r < 23.8411
# Expected 50.0%: r < 34.1250
# Expected 84.0%: r < 49.7677
# Expected 97.5%: r < 69.8073
et_cl_equal_events = [17.4624, 23.8411, 34.1250, 49.7677, 69.8073]

# all together
# Expected  2.5%: r < 5.5038
# Expected 16.0%: r < 7.4523
# Expected 50.0%: r < 10.5938
# Expected 84.0%: r < 15.1965
# Expected 97.5%: r < 20.9798
all_cl_equal_events = [5.5038, 7.4523, 10.5938, 15.1965, 20.9798]


##############################
# CL values for equal weights
##############################


##############################
# CL values for custom events
##############################


##############################
# CL values for custom weights
##############################


def build_interval_dict(training_type: str):
    raw = {}

    if training_type == "equal_events":
        raw = {
            "et": et_cl_equal_events,
            "mt": mt_cl_equal_events,
            "tt": tt_cl_equal_events,
            "all": all_cl_equal_events,
        }

    # Placeholder für zukünftige Varianten
    # elif training_type == "equal_weights":
    #     raw = { ... }

    if not raw:
        raise ValueError(f"Unknown training_type: {training_type}")

    out = {}
    for k, v in raw.items():
        p2, p16, p50, p84, p97 = v
        out[k] = {
            "cl": v,
            "median": p50,
            "err68_low": p50 - p16,
            "err68_high": p84 - p50,
            "err95_low": p50 - p2,
            "err95_high": p97 - p50,
        }
    return out


def plot_intervals(outdir: str = "plots", filename: str = "cl_intervals", training_type: str = "equal_events"):
	data = build_interval_dict(training_type)
	order = ["all", "et", "mt", "tt"]  # Reihenfolge von unten nach oben

	y_positions = np.arange(len(order))

	# Farben
	color_95 = "#b6e3a1"  # hellgrün
	color_68 = "#228B22"  # dunkelgrün

	fig, ax = plt.subplots(figsize=(11, 7))

	bar_width = 0.4

	# 95% Bänder (hellgrün)
	for y, label in zip(y_positions, order):
		d = data[label]
		left = d["median"] - d["err95_low"]
		right = d["median"] + d["err95_high"]
		ax.fill_betweenx([y - bar_width, y + bar_width], left, right, color=color_95, zorder=1)

	# 68% Bänder (dunkelgrün)
	for y, label in zip(y_positions, order):
		d = data[label]
		left = d["median"] - d["err68_low"]
		right = d["median"] + d["err68_high"]
		ax.fill_betweenx([y - bar_width, y + bar_width], left, right, color=color_68, zorder=2)

	# Median Marker
	# Zeichne Median als gestrichelte vertikale Linie über das 95%-Band
	for y, label in zip(y_positions, order):
		d = data[label]
		m = d["median"]
		ax.plot([m, m], [y - bar_width, y + bar_width], color="black", linestyle="--", linewidth=1.4, zorder=4)

	# Referenzlinie r=1 nur falls im Bereich sinnvoll
	xmin = 0.0
	xmax = max(d["median"] + d["err95_high"] for d in data.values()) * 1.05
	if xmax < 1.0:
		xmax = 1.2
	# if 0.0 <= 1.0 <= xmax:
	#     ax.axvline(1.0, color="red", linestyle="--", linewidth=1, label="r=1")

	ax.set_yticks(y_positions)
	ax.set_yticklabels(order)
	# Keine sichtbaren Tick-Markierungen zwischen den Labels
	ax.tick_params(axis="y", which="both", length=0)
	# Sicherstellen, dass keine Minor-Ticks erscheinen
	from matplotlib.ticker import NullLocator
	ax.yaxis.set_minor_locator(NullLocator())
	ax.set_xlabel(r"$95\%$ CL upper limit on $\sigma(pp \to HH)\,/\,\sigma_{\mathrm{theory}}$")
	ax.set_ylim(-0.6, len(order) - 0.4)
	ax.set_xlim(xmin, xmax)
	ax.grid(axis="x", alpha=0.3, linestyle=":")
	ax.set_title(f"CLs - only statistical uncertainties")

	# Legende
	from matplotlib.patches import Patch
	from matplotlib.lines import Line2D

	legend_elements = [
		Patch(facecolor=color_68, label="68% expected"),
		Patch(facecolor=color_95, label="95% expected"),
		Line2D([0, 1], [0, 1], color="black", linestyle="--", label="Median expected"),
	]
	ax.legend(handles=legend_elements, loc="upper right")

	os.makedirs(outdir, exist_ok=True)
	pdf_path = os.path.join(outdir, f"{filename}.pdf")
	png_path = os.path.join(outdir, f"{filename}.png")
	fig.tight_layout()
	fig.savefig(pdf_path)
	fig.savefig(png_path, dpi=150)
	print(f"[INFO] Saved plot to {pdf_path} and {png_path}")


if __name__ == "__main__":
	output_dir = "plots/confidence_intervals"
	filename = "cl_equal_events"
	plot_intervals(outdir=output_dir, filename=filename)


