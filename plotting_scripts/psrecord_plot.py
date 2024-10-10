import matplotlib.pyplot as plt

file = open("performance_lcg102.log", "r")
lines = file.read().splitlines()
file.close()

log = dict()
log["times"] = list()
log["cpu"] = list()
log["mem_real"] = list()
log["mem_virt"] = list()

for idx, line in enumerate(lines):
    if idx == 0:
        continue
    rows = [col.strip() for col in line.split(' ') if col]
    log["times"].append(float(rows[0]))
    log["cpu"].append(float(rows[1]))
    log["mem_real"].append(float(rows[2]))
    log["mem_virt"].append(float(rows[3]))

with plt.rc_context({"backend": "Agg"}):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(log["times"], log["cpu"], "-", lw=1, color="r")

    ax.set_ylabel("CPU (%)", color="r")
    ax.set_xlabel("time (s)")
    ax.set_ylim(0.0, max(log["cpu"]) * 1.2)

    ax2 = ax.twinx()

    ax2.plot(log["times"], log["mem_real"], "-", lw=1, color="b")
    ax2.set_ylim(0.0, max(log["mem_real"]) * 1.2)

    ax2.set_ylabel("Real Memory (MB)", color="b")

    ax.grid()

    fig.savefig("performance_lcg102.png")