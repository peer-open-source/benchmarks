# xm run frame-0012/main  --save
import veux
from xsection.analysis import SaintVenantSectionAnalysis

from run_strain import run_strain
from run_trace import run_trace


if __name__ == "__main__":
    from options import parse_options
    options = parse_options()
    Figures = {}

    shape = options.shape
    sv = SaintVenantSectionAnalysis(shape)
    print(sv.summary())


    Figures["shape"] = veux.draw_shape(shape, origin=True)

    run_strain(options, Figures=Figures)

    run_trace(options)


    if options.save:
        for name, fig in Figures.items():
            fig.save(f"img/{options.shape_name}_{name}.pdf", dpi=600)#, backend="pgf")
