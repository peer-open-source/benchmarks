#
# Sep 3, 2025
#
import os

import veux
import xara
from xara.benchmarks import Prism
import xara.units.iks as units
from xsection.library import from_aisc
import numpy as np


def analyze(model, P,H):
    nn = len(model.getNodeTags())
    nsteps = 10
    model.pattern("Plain", 1, "Linear", load={nn: [P,0,H, 0,0,0]})
    model.integrator("LoadControl", 1/nsteps)
    model.analysis("Static")
    model.test("Energy", 1e-12, 10)

    assert model.analyze(nsteps) == 0



if __name__ == "__main__":
#   shape = Rectangle(d=14, b=10, mesh_scale=1/100) #
    shape = from_aisc("W14x48", units=units, mesh_scale=1/100)
    # shape = from_aisc("W18x40", units=units, mesh_scale=1/100)

    E  = 29e3*units.ksi
    G  = 11.2e3*units.ksi * 1000

    A  = shape.cnn()[0,0]
    GA = A*G
    EI = E*shape.cmm()[1,1]

    L = shape.d*10
    element = os.environ.get("Element", "ForceFrame")
    for shear in [1]:
        prism = Prism(shape=shape,
                      length=L,
                      boundary=((1,1,1,  1,1,1),
                                (0,1,0,  1,1,1)),
                      material={"name": "ElasticIsotropic", "E": E, "G": G},
                      element=element,
                      section=os.environ.get("Section", "ShearFiber"),
                      shear=shear,
                      transform=os.getenv("Transform", "Corotational02"),
                      divisions=1,
                      order=2 if "Exact" in element else 1
                )
        model = prism.create_model()

        P = -10
        H = 100
        analyze(model, P,H)

        end = len(model.getNodeTags())
        uz = model.nodeDisp(end, 3)
        Peuler = -np.pi**2*EI/L**2
        print(f"Peuler = {Peuler:.3f}")
        lam = (np.pi/2)*np.sqrt(P/Peuler)
        u_euler = H*L**3/(12*EI)
        u_delta = u_euler*(3*(np.tan(lam)-lam)/lam**3)

        print(f"u/L = {uz/L:.6f}, u/L theory = {u_delta/L:.6f}, (Linear = {u_euler/L:.6f})")

        # model.eval(f"verify value [nodeDisp {end} 3] {u_euler+u_shear:.12f} 1e-6")

    # a = veux.create_artist(model)
    # a.draw_sections()
    # veux.serve(a)
