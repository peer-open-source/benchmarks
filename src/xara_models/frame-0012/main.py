# xm run frame-0012/main  --save
import veux
import os
from xsection.analysis import SaintVenantSectionAnalysis

from run_strain import run_strain
from run_trace import run_trace
import thesis as plt

os.environ["XARA_FIBER_THREADS"] = "1"

if __name__ == "__main__":
    from options import parse_options
    options = parse_options()
    Figures = {}

    shape = options.shape
    sv = SaintVenantSectionAnalysis(shape)
    print(sv.summary())


    Figures["shape"] = veux.ShapeArtist(shape)
    Figures["shape"].draw_surfaces()
    Figures["shape"].draw_exterior()
    Figures["shape"].draw_origin(fontsize=16, label="$O$")

    run_strain(options, Figures=Figures)

    run_trace(options)


    if options.save:
        for name, fig in Figures.items():
            fig.save(f"img/{options.shape_name}_{name}.pdf", dpi=600)#, backend="pgf")

        with open(f"out/{options.shape_name}.tex", "w") as f:
            f.write(sv.summary(format="texsection"))

    plt.show()