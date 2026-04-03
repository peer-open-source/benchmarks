#
# Sep 27, 2025
#
# Hjelmstad's shear link #4
#
import sys
import thesis as plt
import thesis
from post import PlotResponse2
from pathlib import Path
import numpy as np

if __name__ == "__main__":
    shape_name = "W03"
    if len(sys.argv) > 1:
        shape_name = sys.argv[1]

    ##
    axs = thesis.MultiFigure((1,2), aspect=0.45)
    plot_1 = PlotResponse2(ax=axs[0], axs=axs)
    plot_2 = PlotResponse2(ax=axs[1], axs=axs)
    plot_3 = PlotResponse2()

    axs[0].set_xlabel("Displacement (in)")
    axs[1].set_xlabel("Displacement (in)")
    axs[0].set_ylabel("Load (kips)")
    plot_3.ax.set_xlabel("Displacement (in)")
    plot_3.ax.set_ylabel("Load (kips)")

    for ax in [axs[0], axs[1], plot_3.ax]:
        ShellColors = iter(["k", "r", "b", "g", "m"])
        for file in Path("out").glob(f"shell-2007-case1-{shape_name}.txt"):
            case = file.stem.split("-")[-2][4:]
            ps, uz, vs, uy = np.loadtxt(file, unpack=True)
            stride = 200
            ax.plot(uz[::stride], ps[::stride], "o", 
                    label=f"Shells", 
                    color=next(ShellColors),
                    markersize=4,
                    fillstyle="none",
                    # linestyle="-"
            )

    Cases = [
        dict(element="ForceFrame", shear=0, trace=None, tag=1),
        dict(element="ForceFrame", shear=1, trace=None, tag=2),
        dict(element="ForceFrame", shear=1, trace="MS", tag=3),
        dict(element="ForceFrame", shear=1, trace="energetic", tag=4),
        dict(element="ForceFrame", shear=1, trace="geometric", tag=5),
    ] + ([
        dict(element="ExactFrame", shear=1, trace="energetic", tag=6),
        dict(element="ExactFrame", shear=1, trace="energetic", order=3, tag=7),
    ] if shape_name == "W03" else [])

    Sections = {
        "MS": r"\cite{scott2004response}",
        "energetic": r"\cref{sec:trace-energy}",
        "geometric": r"\cref{sec:trace-cowper}",
        None: "None"
    }

    ##
    
    for case in Cases:
        i = case["tag"]
        element = case["element"]
        shear   = case["shear"]
        trace   = case["trace"]
        order   = case.get("order", 1)
        print(f"{i} & ",
              f"{element} & ",
              f"{'Yes' if shear else 'No'} & ",
              f"{Sections[trace]} & ",
              f"{order if element == 'ExactFrame' else 5} ",
              "\\\\")

        if i in {1,2,3}:
            plot_1.reset(label=f"Case {i}")
            plot_1.load_data(f"out/C{i}_{shape_name}_data.txt")
            plot_1.draw()
        if i in {4, 5, 6, 7}:
            plot_2.reset(label=f"Case {i}")
            plot_2.load_data(f"out/C{i}_{shape_name}_data.txt")
            plot_2.draw()

        if i in {2, 4, 5}:
            label = {
                2: r"Compatible \eqref{eq:linear-gl-strain-pi}",
                4: r"Enhanced \ref{sec:trace-energy}",
                5: r"Enhanced \ref{sec:trace-cowper}"
            }[i]
            style = {
                2: {"color": "r", "linestyle": "--"},
                4: {"color": "b", "linestyle": "-."},
                5: {"color": "g", "linestyle": ":"}
            }[i]
            plot_3.reset(label=label)
            plot_3.load_data(f"out/C{i}_{shape_name}_data.txt")
            plot_3.draw(style=style)

    # plt.tight_layout()
    thesis.space_ticks(axs[0], 'y', round=5)
    thesis.space_ticks(axs[1], 'y', round=5)
    thesis.format_ticks(plot_3.ax)
    thesis.legend(plot_3.ax)
    axs.finish()
    # axs.figure.savefig(f"img/{shape_name}_u.pgf", backend="pgf")
    plot_3.ax.figure.savefig(f"img/{shape_name}_u.pgf", backend="pgf")
    plt.show()
