#
# The axial force N is applied to the shear center of the free end.
#
import os
import veux
import xara
import numpy as np
import xsection.library as xs
from xara.benchmarks import Prism
from xara.helpers import find_node
import matplotlib.pyplot as plt
try:
    plt.style.use("veux-web")
except:
    pass



def analyze(model, shape, sc, L, N):
    model.pattern("Plain", 2, "Linear")
    element = len(model.getEleTags())
    # print(f"{offset = }, {element = }")
    model.eleLoad("Frame",
                  "Point",
                  basis="local",
                  offset=[1,sc[0],sc[1]],
                  force=[N,0,0],
                  pattern=2,
                  elements=element
    )
    steps = 100
    model.integrator("LoadControl", 1/steps)
    model.system('Umfpack')
    model.test("Energy", 1e-20, 20, 2)
    model.analysis("Static")
    u = []
    v = []
    w = []
    for _ in range(steps):
        if model.analyze(1) != 0:
            print(f"Failed at time = {model.getTime()} with {N = }")
            break
        u.append([-model.nodeDisp(find_node(model, x=L),1), -N*model.getTime()])
        v.append([-model.nodeDisp(find_node(model, x=L),2), -N*model.getTime()])
        w.append([-model.nodeDisp(find_node(model, x=L),3), -N*model.getTime()])
    return u, v, w


if __name__ == "__main__":
    os.environ["Wagner"] = "1"
    version = "Battini"

    if version == "Battini":
        L = 1.4e3
        N = -70
        shape = xs.Angle(b=47.75,
                         d=72.75,
                         t=6.5,
                         mesh_scale=1/20)
        # shape = shape.rotate(-0.4209)
        sc = shape.centroid
        shape = shape.translate(-sc)
        # veux.serve(veux.render(shape.model))
        material = {
            "name": "ElasticIsotropic", 
            "E":  193.05,
            "nu": 0.3
        }
    else:
        import xara.units.mks as units
        # The geometric and material properties of the cantilever are: 
        # L = 1,400 mm, a = 76 mm, b = 51 mm, t = 6.5 mm, 
        # Young’s modulus E = 
        L = 1.4*units.m
        N = -60e3*units.N
        shape = xs.Angle(b=51*units.mm,
                        d=76*units.mm,
                        t=6.4*units.mm,
                        mesh_scale=1/400)
        print(f"{shape.centroid = }, {shape._principal_rotation() = }")
        print(shape.summary())
        sc = shape.centroid
        shape = shape.translate(-shape.centroid)
    # veux.serve(veux.render(shape.model))
        material = {
            "name": "ElasticIsotropic", 
            "E":  193.05e3*units.MPa,
            # "G":  33.445e3*units.MPa,
            "nu": 0.3
        }

    prism = Prism(shape=shape,
            length=L,
            boundary=((1,1,1,  1,1,1),
                      (0,0,0,  0,0,0)),
            material=material,
            element="ExactFrame",
            section="ShearFiber",
            transform="Corotational02",
            shear=1,
            vertical=3,
            # shear_warp=0,
            divisions=4,
            order=3
    )
    model = prism.create_model()
    u, v, w = analyze(model, shape, -sc, L, N=N)

    fig, ax = plt.subplots()
    ax.plot(*zip(*u), label="$u_x$")
    ax.plot(*zip(*v), label="$u_y$")
    ax.plot(*zip(*w), label="$u_z$")
    plt.legend()
    fig.savefig("img/1030-soln.png")
    plt.show()
