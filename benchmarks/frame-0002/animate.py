#
# May 30 2025
#
import os

import veux
from xara.benchmarks import Prism
from veux.motion import Motion
import xara.units.iks as units
from xsection.library import from_aisc, Rectangle
import numpy as np


def analyze(model, P, nstep):
    nn = len(model.getNodeTags())

    model.pattern("Plain", 1, "Linear", load={nn: [0,P,0, 0,0,-P*100]})
    model.integrator("LoadControl", 1)
    model.analysis("Static")#, pattern=1, integrator=1)
    model.test("Residual", 1e-8, 3)

    speed = 4
    motion = Motion(artist)
    for i in range(nstep):
        if model.analyze(1) != 0:
            print(f"Failed at time = {model.getTime()}")
            break

        motion.advance(time=model.getTime()/speed)
        motion.draw_sections(rotation=model.nodeRotation,
                             position=model.nodeDisp)


    return motion


if __name__ == "__main__":
#   shape = Rectangle(d=10, b=6, mesh_scale=1/100) #
    shape = from_aisc("W14x48", units=units, mesh_scale=1/100)

    E  = 29e3*units.ksi
    G  = 11.2e3*units.ksi # * 4/5

    A  = shape.cnn()[0,0]
    GA = A*G
    EI = E*shape.cmm()[1,1]

    L = shape.d*15


    for shear in [0,]:
        prism = Prism(shape=shape,
                      length=L,
                      boundary=((1,1,1,  1,1,1), 
                                (0,0,0,  0,0,0)),
                      material={"name": "ElasticIsotropic", "E": E, "G": G},
                      element=os.environ.get("Element", "ForceFrame"),
                      section=os.environ.get("Section", "ShearFiber"),
                      shear=shear,
                      divisions=4
                )
        model = prism.create_model()
        artist = veux.create_artist(model, model_config=dict(extrude_outline=shape))

        P = 10
        motion = analyze(model, P, 60)
        motion.add_to(artist.canvas)
        veux.serve(artist)

        end = len(model.getNodeTags())
        uz = model.nodeDisp(end, 3)
        u_euler = P*L**3/(3*EI)
        u_shear = P*L/GA * shear

        print(f"Uz = {uz:.6f}, Uz theory = {u_euler+u_shear:.6f} ({u_euler:.6f} + {u_shear:.6f})")


    # a = veux.create_artist(model)
    # a.draw_sections()
    # veux.serve(a)
