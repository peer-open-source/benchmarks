#
# Aug 27 2025
#
import os

import veux
import xara
from xara.benchmarks import Prism
import xara.units.iks as units
from xsection.library import from_aisc, Rectangle
import numpy as np


def analyze(model, P):
    nn = len(model.getNodeTags())

    model.pattern("Plain", 1, "Linear", load={nn: [0,0,1, 0,0,0]})
    model.integrator("LoadControl", P)
    model.analysis("Static")
    model.test("Residual", 1e-10, 3)

    assert model.analyze(1) == 0



if __name__ == "__main__":
#   shape = Rectangle(d=14, b=10, mesh_scale=1/100) #
    shape = from_aisc("W14x48", units=units, mesh_scale=1/100)

    E  = 29e3*units.ksi
    G  = 11.2e3*units.ksi # * 4/5

    A  = shape.cnn()[0,0]
    Az = A*shape._analysis.shear_factor_romano()[0][1]

    print(f"{G*Az = }")
    GA = Az*G
    EI = E*shape.cmm()[1,1]
    print(f"{EI = }")

    L = shape.d*4
    for shear in [1]:
        prism = Prism(shape=shape,
                      length=L,
                      boundary=((1,1,1,  1,1,1), 
                                (0,0,0,  0,0,0)),
                      material={"name": "ElasticIsotropic", "E": E, "G": G},
                      element=os.environ.get("Element", "ForceFrame"),
                      section=os.environ.get("Section", "ShearFiber"),
                      shear=shear,
                      vertical=3,
                      shear_warp=shear,
                      divisions=1,
                      order=1
                )
        model = prism.create_model()
        model.print(json="model.json")

        P = 10
        analyze(model, P)

        end = len(model.getNodeTags())
        uz = model.nodeDisp(end, 3)
        u_euler = P*L**3/(3*EI)
        u_shear = P*L/GA * shear

        print(f"Uz = {uz:.6f}, Uz theory = {u_euler+u_shear:.6f} ({u_euler:.6f} + {u_shear:.6f})")

        model.eval(f"verify value [nodeDisp {end} 3] {u_euler+u_shear:.12f} 1e-6")

    # a = veux.create_artist(model)
    # a.draw_sections()
    # veux.serve(a)
