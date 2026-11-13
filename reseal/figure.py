"""The report's main figure: what each verifier refused, in three setups.

Sprint work (13 Nov 2026 onward).

    python -m reseal.figure            # writes results/fig_main.png
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .report import load

INTERIOR = ("first", "middle", "penultimate")
ROWS = [  # label, attack ids, positions (None = all)
    ("Edit, swap, insert, replay\nor backdate a record", ("A1", "A2", "A5", "A6", "A7", "A8"), None),
    ("Delete a record that is\nnot the last", ("A3",), INTERIOR),
    ("Delete the last record", ("A3",), ("final",)),
    ("Cut off the last 1 or 10\nrecords", ("A4",), None),
    ("Change any one stored field\n(fields refused)", ("A9",), None),
    ("Strip signature or\nintegrity fields", ("A10",), None),
    ("Rebuild the log without\nthe keys", ("A11",), None),
    ("Operator rebuilds the log\nwith the real keys", ("A12",), None),
    ("Operator shows a forked\nhistory", ("A13",), None),
    ("Control: the action was\nnever recorded", ("A14",), None),
]
TOOLS = [("halo-record", "halo-\nrecord"), ("witnesskit", "Witness\nKit"), ("signet", "Signet"),
         ("agent-receipts", "Agent\nReceipts"), ("tool-e", "Tool E"), ("plain-jsonl", "plain\nlog")]
PANELS = [("default", "A. Default setup"), ("strong", "B. Strongest documented setup"),
          ("checkpoint", "C. Default + outside checkpoint"),
          ("checkpoint-stale", "D. Default + stale checkpoint (90%)")]


def cell(rows_by, tool, setup, ids, positions):
    """(refused, shown) for one cell; for A9 the unit is a stored field."""
    sel = [r for i in ids for r in rows_by[(tool, setup, i)]
           if r["applicable"] and (positions is None or r["position"] in positions)]
    if not sel:
        return None
    if ids == ("A9",):
        fields = defaultdict(list)
        for r in sel:
            fields[r["variant"]].append(r["detected"])
        return sum(all(v) for v in fields.values()), len(fields)
    return sum(r["detected"] for r in sel), len(sel)


def collect(main="results/main", layer="results/layer"):
    rows_by = defaultdict(list)
    for run in (main, layer):
        rows, _ = load(run)
        for r in rows:
            if r["kind"] in ("attack", "coverage"):
                rows_by[(r["tool"], r["setup"], r["id"])].append(r)
    grid = {}
    for setup, _ in PANELS:
        for tool, _ in TOOLS:
            for k, (_label, ids, pos) in enumerate(ROWS):
                grid[(setup, tool, k)] = cell(rows_by, tool, setup, ids, pos)
    return grid


def draw(grid, path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    ramp = LinearSegmentedColormap.from_list("blue", ["#ffffff", "#cde2fb", "#6da7ec", "#256abf", "#0d366b"])
    ink, muted = "#1f1f1c", "#6b6a66"
    fig, axes = plt.subplots(2, 2, figsize=(7.5, 6.5), sharey=True)
    for ax, (setup, title) in zip(axes.flat, PANELS):
        data = [[(lambda c: float("nan") if c is None else c[0] / c[1])(grid[(setup, t, k)])
                 for t, _ in TOOLS] for k in range(len(ROWS))]
        ax.imshow(data, cmap=ramp, vmin=0, vmax=1, aspect="auto")
        for k in range(len(ROWS)):
            for j, (t, _) in enumerate(TOOLS):
                c = grid[(setup, t, k)]
                if c is None:
                    ax.text(j, k, "n/a", ha="center", va="center", fontsize=7.5, color=muted)
                    continue
                d, n = c
                text = "all" if d == n else ("none" if d == 0 else f"{d}/{n}")
                ax.text(j, k, text, ha="center", va="center", fontsize=8 if len(text) < 6 else 7,
                        color="#ffffff" if d / n > 0.6 else ink,
                        fontweight="bold" if d == n else "normal")
        ax.set_xticks(range(len(TOOLS)))
        ax.set_xticklabels([lab for _, lab in TOOLS], fontsize=7.4, color=ink, linespacing=0.95)
        ax.xaxis.tick_top()
        ax.set_title(title, fontsize=8.6, color=ink, pad=28, loc="left", fontweight="bold")
        ax.set_xticks([x - 0.5 for x in range(1, len(TOOLS))], minor=True)
        ax.set_yticks([y - 0.5 for y in range(1, len(ROWS))], minor=True)
        ax.grid(which="minor", color="#ffffff", linewidth=1.6)
        ax.tick_params(which="both", length=0)
        ax.axvline(len(TOOLS) - 1.5, color=muted, linewidth=0.8)  # the baseline sits apart
        for sp in ax.spines.values():
            sp.set_visible(False)
    for ax in axes[:, 0]:
        ax.set_yticks(range(len(ROWS)))
        ax.set_yticklabels([lab for lab, _, _ in ROWS], fontsize=7.6, color=ink, linespacing=0.95)
    fig.text(0.005, 0.008, "all = every tampered log refused; none = every one accepted; a fraction = refused / shown.\n"
             "'plain log' is an unprotected baseline, not a tool under test; it has no documented stronger setup.",
             fontsize=7.2, color=muted, linespacing=1.3)
    fig.tight_layout(rect=(0, 0.045, 1, 1), w_pad=0.8, h_pad=1.4)
    fig.savefig(path, dpi=240, facecolor="#ffffff")
    plt.close(fig)
    return path


def main():
    out = Path("results/fig_main.png")
    print("wrote", draw(collect(), out))


if __name__ == "__main__":
    main()
