#
# Sep 27, 2025
#
# Hjelmstad's shear link #4
#

import os
import sys
from argparse import ArgumentParser
from pathlib import Path
import numpy as np
import veux
from xara import Material
from xara.post import PlotConvergenceRate
from xara.benchmarks import Prism
import xara.units.iks as units
from xara.helpers import find_node
from xsection.library import from_aisc, WideFlange, Rectangle
from xsection.analysis import SaintVenantSectionAnalysis
from xsection._benchmarks import load_shape
import thesis as plt
import thesis

verbose = False

from model import create_section, analyze
from post import PlotResponse
from xara.post import FiberStress, NodalAverage, PlotConvergenceRate

parser = ArgumentParser()
parser.add_argument("--shape", type=str, default="W03", help="Shape name (W03, H09, RX, H05, etc.)")
parser.add_argument("--save", action="store_true", default=False, help="Whether to save data and figures")

if __name__ == "__main__":
    args = parser.parse_args()
    Save = args.save
    shape_name = args.shape #"Tube" #"Rectangle" #"W03"

    Cases = [
        dict(element="ForceFrame", shear=0, trace=None,        tag=1, label=r"Reference~\ref{ref:AxialFiber}"),
        dict(element="ForceFrame", shear=1, trace=None,        tag=2, label=r"Compatible \eqref{eq:linear-gl-strain-pi}"),
        dict(element="ForceFrame", shear=1, trace="MS",        tag=3, label=r"Reference~\ref{ref:NDFiber}"),
        dict(element="ForceFrame", shear=1, trace="energetic", tag=4, label=r"Enhanced \ref{sec:trace-energy}"),
        dict(element="ForceFrame", shear=1, trace="geometric", tag=5, label=r"Enhanced \ref{sec:trace-cowper}"),
        # dict(element="ExactFrame", shear=1, trace="energetic", tag=6),
        # dict(element="ExactFrame", shear=1, trace="energetic", order=3, tag=7),
    ]


    Fy = 35.0*units.ksi
    E = 30e3*units.ksi
    G = 12e3*units.ksi

    material = Material(
        type="NonlinearJ2", #"J2BeamThread", # # "J2BeamFiber" #   "J2" # "GeneralizedJ2" # "J2Simplified" #
        E =  E,
        G =  G,
        Fy = Fy,
        Hiso = 0.002*E,
        Hkin = 0.002*E
    )

    print(f"poisson = {E/(2*G)-1.0}")

    size = 1
    if shape_name == "W03": # Hjelmstad's original link
        shape = from_aisc("W18x40",
                        units=units,
                        mesh_scale=1/size,
                        material=material,
                        fillet=True,
                        mesh_type="T3",
                        mesher="gmsh")
        L = 28*units.inch
    elif shape_name == "RX":
        shape = Rectangle(
            d=18,
            b=4,
            material=material,
            mesh_scale=1/10,
            mesh_type="T3",
            mesher="gmsh"
        )
        material.type = "J2BeamThread"
        L = 28*units.inch
    elif False:
        shape = WideFlange(
            tw=1.10*units.inch,
            d = 33.86*units.inch,
            b = 23.62*units.inch,
            tf=1.77*units.inch,
            material=material,
        )
        L = 66*units.inch
    else:
        shape = load_shape(shape_name, material=material, 
                           mesh_scale=1/3,
                           mesh_type="T3", mesher="gmsh")
        L = 28*units.inch

    sv = SaintVenantSectionAnalysis(shape)
    print(sv.summary(format="texsection"))


    transform = os.environ.get("Transform", "Linear")

    ##
    plot_1 = PlotResponse()


    ShellColors = iter(["k", "r", "b", "g", "m"])
    for file in Path("out").glob(f"shell-2007-case?-{shape_name}.txt"):
        case = file.stem.split("-")[-2][4:]
        ps, uz, vs, uy = np.loadtxt(file, unpack=True)
        stride = 200
        plot_1.ax.plot(uz[::stride], ps[::stride], "o", 
                label=f"Shells", 
                color=next(ShellColors),
                markersize=4,
                fillstyle="none",
                # linestyle="-"
        )

    _,plot_stress = thesis.subplots(1,3, aspect=0.5)
    plot_stress[0].figure.subplots_adjust(wspace=0.8)

    ##
    for case in Cases:
        i = case["tag"]
        element = case["element"]
        shear   = case["shear"]
        trace   = case["trace"]
        order   = case.get("order", 1)
        case_label = case.get("label", f"Case {i}")


        print(f"Running {element} shear={shear} trace={trace}")
        prism = Prism(shape=shape,
                    length=L,
                    boundary=((1,1,1,  1,1,1),
                              (1,1,0,  0,1,1)),
                    material=material,
                    element=element,
                    section=create_section(shape, trace, shear),
                    shear=shear,
                    transform=transform,
                    integration={
                        "points": 3, "type": "Legendre"
                    },
                    divisions=1,
                    order=order
                )

        model = prism.create_model(
            echo_file=open(f"out/C{i}_{shape_name}.tcl", "w+")
        )
        model.print(json=f"out/C{i}_{shape_name}.json")


        plot_cr = PlotConvergenceRate(x_mode="time", skip=True)
        # plot_cr.ax.figure.suptitle(f"Case {i}: {element} shear={shear} trace={trace}")

        plot_1.reset(model, find_node(model, x=L), 3,
                    label=f"({i}) {'Shear' if shear else 'Euler'}, {'Warping ('+str(trace)+')' if trace else ''}" + f" {element}")


        analyze(model, find_node(model, x=L),
                trace=trace,
                shear=shear,
                verbose=verbose,
                plots=[plot_1, plot_cr]
        )

        plot_1.draw()
        plot_1.save_data(f"out/C{i}_{shape_name}_data.txt")
        plot_cr.draw()
        plot_cr.finalize()

        if False: #shear:
            artist = veux.ShapeArtist(shape, 
                                      title=case_label)
            artist.draw_surfaces(
                field=FiberStress(model, shape, section=1, stress="svm", element=1),
                cbar_label="Von Mises Stress (ksi)",
            )
            artist.save(f"img/C{i}_{shape_name}_stress.pgf", backend="pgf")
        if i in {2, 4, 5}:
            artist = veux.ShapeArtist(shape, 
                                      ax=plot_stress[[2,4,5].index(i)],
                                      title=case_label)
            artist.draw_surfaces(
                field=FiberStress(model, shape, section=1, stress="svm", element=1),
                cbar_label="Von Mises Stress (ksi)",
            )
            # artist.save(f"img/C{i}_{shape_name}_stress.pgf", backend="pgf")

    # plt.tight_layout()

    plot_1.finish()
    plot_stress[0].figure.savefig(f"img/{shape_name}_stress.pgf", backend="pgf")
    # plot_stress[0].figure.tight_layout()
    # plot_1.ax.figure.savefig(f"img/{element}-size{size}.png", dpi=600)
    plt.show()


    # artist = veux.create_artist(shape.model, ndf=1)
    # artist.draw_surfaces()
    # artist.draw_surfaces(
    #     field=FiberStress(model, shape, section=1, stress="svm", element=1),
    #     state=FiberStress(model, shape, section=1, stress="svm", element=1),
    #     scale=1/Fy
    # )
    # veux.serve(artist)
