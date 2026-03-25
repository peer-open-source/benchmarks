#
# Tip loaded cantilever beam - Poisson effect
#
import os
from argparse import ArgumentParser

import veux
from xara import  Section
from xara.benchmarks import Prism

import numpy as np
from pandas import DataFrame as df
import matplotlib.pyplot as plt
from xara.post import NodalAverage, FiberStress
from xsection.analysis import SaintVenantSectionAnalysis
from thesis import MultiFigure

from post import PlotFiberStrain
from venant import SaintVenant

def analyze(model, P, T):
    nn = len(model.getNodeTags())
    n = 1
    model.pattern("Plain", 1, "Linear", load={nn: [0,0,P, T,0,0]})
    model.integrator("LoadControl", 1/n)
    model.system("BandGen")
    model.analysis("Static")
    model.test("Residual", 1e-10, 5, 1)

    assert model.analyze(n) == 0


def run_strain(options, Figures=None):
    if Figures is None:
        Figures = {}

    element = options.element
    case = options.shape_name
    try:
        case = int(case)
    except:
        pass

    NIP = 5
    P   = 1
    T   = 1
    ne = int(os.getenv("ne", 1))



    shape = options.shape
    material = shape.material


    sv = SaintVenantSectionAnalysis(shape)



    Figures["strain"] = veux.ShapeArtist(shape)



    trace = sv.create_trace(form=options.trace)
    L = shape.d*options.length
    soln = SaintVenant(shape, length=L, sv=sv, material=material, V=[0.0, P], T=-T)



    plot = PlotFiberStrain()

    u_iesan = np.array(soln.u(L, trace=trace))
    prism = Prism(shape=shape,
                    length=L,
                    boundary=((1,1,1,  1,1,1),
                              (0,0,0,  0,0,0)),
                    material=material,
                    element=element,
                    section=Section("MixedFiber", shape, material, mixed_type=options.trace),#_create_section(trace),
                    shear=1,
                    vertical=3,
                    integration={"points": NIP, "type": "Lobatto"},
                    divisions=ne,
                    order=1 if "exact" not in element.lower() else 2
            )


    model = prism.create_model(options={"iter": (1, 1e-12)})

    analyze(model, P, T)

    SampleX = model.eleResponse(1, "integrationPoints")[0]
    SampleFibers = [3, 50, 100]#, 1000]
    for ifib in SampleFibers:
        fiber = shape.model._fibers[ifib]
        r = fiber.coord
        print(ifib, r)
        for ie, ke in enumerate(["11", "12", "13"]):
            cmd = f"eleResponse 1 section 1 fiber {r[0]} {r[1]} strain"
            eref = soln.strain(SampleX, fiber=fiber)
            model.eval(f"set e [{cmd}]")
            try:
                model.eval(f"verify error [lindex $e {ie}] {eref[ie]:.12f} 2.1e-4 {ke}")
            except:
                pass

    # print(f"M = {soln.moment(L)}")
    ifib = 100
    fiber = shape.model._fibers[ifib]
    r = fiber.coord
    
    print(model.state.element(1).section(NIP).strain())
    print(f"{r = }")
    for ie in [0, 1, 2]:
        plot.draw(model, tuple(r.tolist()), ie)
        X = np.linspace(0, L, 100)
        plot._ax.plot(X/L, 
                    [soln.strain(x, fiber=fiber)[ie] for x in X],
                    color=plot._color,
                    #marker=".",
                    linestyle='--', 
                    linewidth=1.2, 
                    label=f"{ie}"
        )

    end = len(model.getNodeTags())
    uz  = model.state.u(end, 3)

    # print(f"Uz = {uz:.8f}, Uz theory = {u_iesan[2]:.8f} ({u_euler:.6f} + {u_shear:.6f})")
    # print("FEA: ", model.state.u(end))
    # print("Trace: ", trace.solve(soln.p).position(L))
    # print(".      ", trace.solve(soln.p).rotation(L))


    elem_stress = FiberStress(model, 
                              shape, 
                              section=1, 
                              stress="sxz", 
                              element=1)
    Figures["strain"].draw_surfaces(
        field=elem_stress,
        # scale=1/max(elem_stress(n) for n in range(len(shape.model.nodes)))
    )
    plot.finalize()
    plt.show()

    return Figures

    # soln.render(trace=trace)
    if True:
        artist = veux.create_artist(shape.model, ndf=1)
        artist.draw_surfaces()
        for ifib in SampleFibers:
            r = sum(shape.model.nodes[shape.model.elems[ifib].nodes])/3
            artist.canvas.plot_nodes(
                [[r[0], r[1], 0]],
                size=5,
            )
        veux.serve(artist)

    if False:
        artist = veux.create_artist(shape.model, ndf=1)
    #       artist.draw_surfaces()
        artist.draw_outlines()
        artist.draw_surfaces(
            field=elem_stress,
            state=elem_stress,
            scale=1/max(elem_stress(n) for n in range(len(shape.model.nodes)))
        )
        veux.serve(artist)


    artist = veux.create_artist(shape.model, ndf=1)
#       artist.draw_surfaces()
    artist.draw_outlines()
    ncn = 3 # number of cell nodes
    stress = NodalAverage(shape.model, lambda n: [
        [soln.strain(SampleX, fiber=shape.model._fibers[n])[2]]
    ]*ncn)
    # artist.draw_surfaces(
    #     state=elem_stress,
    #     scale=1/max(stress(n) for n in range(len(shape.model.nodes)))
    # )
    artist.draw_surfaces(
        field=stress,
        state=stress,
        scale=1/max(stress(n) for n in range(len(shape.model.nodes)))
    )
    veux.serve(artist)

       #a = veux.create_artist(model)
       #a.draw_sections()
       #veux.serve(a)



if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-e", "--element", default="ForceFrame",    help="Element type")
    parser.add_argument("-s", "--shape",   type=str,   default="2",  help="Shape case")
    parser.add_argument("-n", "--number",  type=int,   default=1,    help="Number of elements")
    parser.add_argument("-v", "--poisson", type=float, default=-0.5, help="Poisson ratio")
    parser.add_argument("-r", "--rotate",  default=False,  help="Rotate", action="store_true")
    parser.add_argument("-t", "--trace",   default="energetic", help="Trace type")
    options = parser.parse_args()

    run_strain(options)
