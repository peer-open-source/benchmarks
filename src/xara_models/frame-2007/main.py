#
# Sep 27, 2025
#
# Hjelmstad's shear link #4
#

import os
import sys
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



if __name__ == "__main__":
    from xara.post import FiberStress, NodalAverage
    shape_name = "W03" #"Tube" #"Rectangle" #"W03"

    if len(sys.argv) > 1:
        shape_name = sys.argv[1]

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

    Cases = [
        dict(element="ForceFrame", shear=0, trace=None, tag=1),
        dict(element="ForceFrame", shear=1, trace=None, tag=2),
        dict(element="ForceFrame", shear=1, trace="MS", tag=3),
        dict(element="ForceFrame", shear=1, trace="energetic", tag=4),
        dict(element="ForceFrame", shear=1, trace="geometric", tag=5),
        dict(element="ExactFrame", shear=1, trace="energetic", tag=6),
        dict(element="ExactFrame", shear=1, trace="energetic", order=3, tag=7),
    ]

    ##
    for case in Cases:
        i = case["tag"]
        element = case["element"]
        shear   = case["shear"]
        trace   = case["trace"]
        order   = case.get("order", 1)


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


        # plot_cr = PlotConvergenceRate(x_mode="time",ci=95)
        # plot_cr.ax.figure.suptitle(f"Case {i}: {element} shear={shear} trace={trace}")

        plot_1.reset(model, find_node(model, x=L), 3,
                    label=f"({i}) {'Shear' if shear else 'Euler'}, {'Warping ('+str(trace)+')' if trace else ''}" + f" {element}")


        analyze(model, find_node(model, x=L),
                trace=trace,
                shear=shear,
                verbose=verbose,
                plots=[plot_1]#, plot_cr]
        )

        plot_1.draw()
        plot_1.save_data(f"out/C{i}_{shape_name}_data.txt")
        # plot_cr.draw()
        # plot_cr.finalize()

        if shear:
            artist = veux.ShapeArtist(shape, 
                                      title=f"Case {i}",)
            artist.draw_surfaces(
                field=FiberStress(model, shape, section=1, stress="svm", element=1),
                cbar_label="Von Mises Stress (ksi)",
            )
            artist.save(f"img/C{i}_{shape_name}_stress.pgf", backend="pgf")


    # plt.tight_layout()

    plot_1.finish()
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
