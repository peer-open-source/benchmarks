#
# Sep 27, 2025
#
# Hjelmstad's shear link #4
#

import os
import time
import veux
from xara import Material
from xara.benchmarks import Prism
import xara.units.iks as units
from xara.helpers import find_node
from xsection.library import from_aisc, WideFlange
import matplotlib.pyplot as plt
# plt.style.use("typewriter")

verbose = False

from model import create_section, analyze
from post import PlotResponse



if __name__ == "__main__":
    from xara.post import FiberStress, NodalAverage
    link_name = "Hjelmstad"

    Fy = 35.0*units.ksi
    E = 30e3*units.ksi
    G = 12e3*units.ksi

    material = Material(
        type="NonlinearJ2", # "J2BeamFiber" #   "J2" # "GeneralizedJ2" # "J2Simplified" #
        E =  E,
        G =  G,
        Fy = Fy,
        Hiso = 0.002*E,
        Hkin = 0.002*E
    )

    print(f"poisson = {E/(2*G)-1.0}")

    size = 1
    if link_name == "Hjelmstad":
        shape = from_aisc("W18x40",
                        units=units,
                        mesh_scale=1/size,
                        material=material,
                        fillet=True,
                        mesh_type="T3",
                        mesher="gmsh")
        L = 28*units.inch
    else:
        shape = WideFlange(
            tw=1.10*units.inch,
            d = 33.86*units.inch,
            b = 23.62*units.inch,
            tf=1.77*units.inch,
            material=material,
        )
        L = 66*units.inch

    print(shape.summary(shear=False))


    transform = os.environ.get("Transform", "Linear")

    ##
    plot_1 = PlotResponse()

    Cases = [
        dict(element="ForceFrame", shear=1, trace="MS"),
        dict(element="ForceFrame", shear=0, trace=None),
        dict(element="ExactFrame", shear=1, trace="energetic"),
        # dict(element="ExactFrame", shear=1, trace="energetic", order=3),
        dict(element="ForceFrame", shear=1, trace="energetic"),
        # dict(element="ForceFrame", shear=1, trace="geometric"),
        dict(element="ForceFrame", shear=1, trace=None),
    ]

    ##
    i = 1
    for case in Cases:
        element = case["element"]
        shear   = case["shear"]
        trace   = case["trace"]
        order   = case.get("order", 1)

        # Create section
        # section = Section(
        #     type="ShearFiber" if shear else "AxialFiber",
        #     shape=shape,
        #     warp=trace,
        #     material=material,
        # )

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
                        "points": 5, "type": "Legendre"
                    },
                    divisions=1, # 1
                    order=order
                )

        model = prism.create_model(
            echo_file=open(f"out/{i}.tcl", "w+")
        )
        model.print(json=f"out/{i}.json")

        plot_1.reset(model, find_node(model, x=L), 3,
                    label=f"({i}) {'Shear' if shear else 'Euler'}, {'Warping ('+str(trace)+')' if trace else ''}" + f" {element}")


        analyze(model, find_node(model, x=L),
                trace=trace,
                shear=shear,
                verbose=verbose,
                plots=[plot_1]#+[PlotPlasticSpread(model, elements=[
                #         ElementFiberYieldMap(model, shape, Fy=Fy, element=1, remember=False),
                #         ElementFiberYieldMap(model, shape, Fy=Fy, element=2, remember=False)
                #     ] if False else []) #shear else [])
                # ]
        )

        plot_1.draw()
        i += 1

    plt.tight_layout()

    plot_1.finish()
    plot_1.ax.figure.savefig(f"img/{element}-size{size}.png", dpi=600)
    plt.show()


    artist = veux.create_artist(shape.model, ndf=1)
    artist.draw_surfaces()
    # artist.draw_outlines(state = lambda _: 1)
    artist.draw_surfaces(
        field=FiberStress(model, shape, section=1, stress="svm", element=1),
        state=FiberStress(model, shape, section=1, stress="svm", element=1),
        scale=1/Fy
    )
    veux.serve(artist)
