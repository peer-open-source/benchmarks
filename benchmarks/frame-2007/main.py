#
# Sep 27, 2025
#
import os
import veux
from veux.motion import Motion
from xara.benchmarks import Prism
import xara.units.iks as units
from xara.helpers import find_node
from xsection.library import from_aisc
import numpy as np
import matplotlib.pyplot as plt

verbose = True 
if verbose:
    tqdm = lambda x: x
else:
    from tqdm import tqdm

def section(model, tag, shape, material):
    model.section("ShearFiber", tag, GJ=0)
    m1 = {k: v for k, v in material[0].items() if k != "type"}
    m2 = {k: v for k, v in material[1].items() if k != "type"}
    model.material(material[0]["type"], 1, **m1)
    model.material(material[1]["type"], 2, **m2)

    for fiber in shape.create_fibers(warp=True, shear=True):
        if abs(fiber["z"]) > (shape.d/2-shape.tf):
            # Flange
            model.fiber(**fiber, material=1, section=tag)
        else:
            # Web
            model.fiber(**fiber, material=2, section=tag)


def analyze(model, nn, motion=None):
    # Loading
    step = 80

    model.pattern("Plain", 1, "Linear", load={nn: (0,0,1,0,0,0)})
    model.system("BandGeneral")
    # model.algorithm("NewtonLineSearch", 0.8)
    model.analysis("Static")
    model.test("Energy", 1e-17, 40, 2)

    history = [
        0.55, -0.5, 
        1.08, -1, 1, -1,
        1.6, -1.6, 1.6, -1.6,
        2.15, -2.1, 2.1, -2.1,
        2.6, -2.6, 2.6, -2.6,
        3.2, -3.2, 3.22
    ]
    u = [0]
    V = [0]
    sign = -1
    try:
        for point in history:
            sign *= -1

            model.integrator("DisplacementControl", nn, 3, 
                            point/step/5)
                            #  *(3, point/step/40, 5*point/step))
            print(point)

            while model.state.u(nn,3) * sign < abs(point):
                if model.analyze(1) != 0:
                    print(f"Failed at time = {model.state.time} with {point = }")
                    return u, V
                if motion:
                    motion.draw_sections(position=model.state.u, rotation=model.nodeRotation)
                    motion.advance(len(u)/step)
                u.append(model.state.u(nn,3))
                V.append(model.state.time)
    except KeyboardInterrupt:
        pass

    return u, V


if __name__ == "__main__":
    size = 40
    shape = from_aisc("W18x40", units=units, mesh_scale=1/size)
    print(shape.summary())

    flange = {
        "E":  28.0e3*units.ksi,
        "Fy": 35.0*units.ksi,
        "Fu": 58.5*units.ksi,
    }
    web = {
        "E":  28.3e3*units.ksi,
        "Fy": 39.5*units.ksi,
        "Fu": 60.1*units.ksi,
    }
    nu = 0.3
    # G  = E/(2*(1+nu))
    material = "GeneralizedJ2" # "J2BeamFiber" # "J2" # "J2Simplified" #

    L = 28*units.inch
    element = os.environ.get("Element", "ForceFrame")
    transform = os.environ.get("Transform", "Corotational02")

    #
    fig, ax = plt.subplots()
    ax.axhline(0, color='k', lw=0.5)
    ax.axvline(0, color='k', lw=0.5)
    ax.set_xlabel("Displacement (in)")
    ax.set_ylabel("Load (kips)")
    ax.grid(True)
    ax.plot(*np.loadtxt("Hjelmstad4.csv", delimiter=",").T, 'k--', label="Experiment")


    for shear in [1]:
        prism = Prism(shape=shape,
                      length=L,
                      boundary=((1,1,1,  1,1,1),
                                (0,1,0,  1,1,1)),
                    #   material={
                    #       "name": "GeneralizedJ2", # "J2BeamFiber", # "J2Simplified", #
                    #       "E": E,
                    #       "G": G,
                    #       "Fy": Fy,
                    #       "Fs": Fu,
                    #       "Hiso": 0.00020*E,
                    #       "Hkin": 0.004*E,
                    #       "Hsat": 0.005*Fy/(Fu-Fy)*E
                    #   },
                      material=[
                          # Flange
                          {  
                            "type": material, 
                            "E": flange["E"],
                            "nu": nu, 
                            "Fy": 0.85*flange["Fy"],
                            "Fs": flange["Fu"]-0.15*flange["Fy"],
                            "Hiso": 0.00020*flange["E"], 
                            "Hkin": 0.004*flange["E"], 
                            "Hsat": 0.01*flange["Fy"]/(flange["Fu"]-flange["Fy"])*flange["E"]
                          },
                          # Web
                          {
                            "type": material, 
                            "E": web["E"], 
                            "nu": nu, 
                            "Fy": 0.85*web["Fy"], 
                            "Fs": web["Fu"] - 0.15*web["Fy"], 
                            "Hiso": 0.00020*web["E"], 
                            "Hkin": 0.004*web["E"], 
                            "Hsat": 0.01*web["Fy"]/(web["Fu"]-web["Fy"])*web["E"]
                          }
                      ],
                      element=element,
                      section=section, #os.environ.get("Section", "ShearFiber"),
                      shear=1,
                      shear_warp=shear,
                      transform=os.getenv("Transform", transform),
                      divisions=2,
                      order=4 if "Exact" in element else 1
                )

        model = prism.create_model()
        artist = veux.create_artist(model, vertical=3, model_config={
            "frame_shape": shape
        })
        motion = Motion(artist)

        u,V = analyze(model, find_node(model, x=L), motion=motion)


        ax.plot(u,V, label=f"{element} size={size}")
        fig.legend()
        fig.savefig(f"img/{element}-{transform}-{material}-size{size}-shear{shear}.png", dpi=300)
        # motion.add_to(artist.canvas)
        # veux.serve(artist)
        plt.show()



        from post import FiberStress
    
        artist = veux.create_artist(shape.model)
        artist.draw_surfaces(
            field=FiberStress(model, shape, section=1, stress="sxx", element=1)
        )
        veux.serve(artist)


    # a = veux.create_artist(model)
    # a.draw_sections()
    # veux.serve(a)
