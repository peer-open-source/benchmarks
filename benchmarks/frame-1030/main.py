#
# The axial force N is applied to the shear center of the free end.
#
import os
import numpy as np
import xara
import veux
import xsection.library as xs
from xara.benchmarks import Prism
from xara.helpers import find_node
import thesis as plt




def analyze(model, shape, L, N, post=None, offset=None):

    end = find_node(model, x=L)
    model.pattern("Plain", 2, "Linear")
    if offset is not None:
        sc = -offset
        element = len(model.getEleTags())
        model.eleLoad("Frame",
                    "Point",
                    basis="local",
                    offset=[1,sc[0],sc[1]],
                    force=[N,0,0],
                    pattern=2,
                    elements=element
        )
    else:
        model.load(end, (N,0,0,  0,0,0), pattern=2)

    steps = 100
    model.integrator("LoadControl", 1/steps)
    model.system('Umfpack')
    model.test("Energy", 1e-20, 20, 0)
    model.analysis("Static")
    u = []
    v = []
    w = []
    for _ in range(steps):
        if model.analyze(1) != 0:
            print(f"Failed at time = {model.getTime()} with {N = }")
            break
        u.append([-model.nodeDisp(end,1), -N*model.getTime()])
        v.append([-model.nodeDisp(end,2), -N*model.getTime()])
        w.append([-model.nodeDisp(end,3), -N*model.getTime()])
    return u, v, w


if __name__ == "__main__":
    os.environ["Wagner"] = "1"
    version = "Battini"
    element = os.environ.get("Element", "ExactFrame")
    transform = os.environ.get("Transform", "Corotational02")
    Shear = int(os.getenv("Shear", 1))
    Warp = int(os.getenv("Warp", 0))

    if version == "Battini":
        L = 1.4e3
        N = -70
        material = xara.Material(**{
            # "name": "ElasticIsotropic", 
            "E":  193.05,
            "nu": 0.3
        })
        shape = xs.Angle(b=47.75,
                         d=72.75,
                         t=6.5,
                         material=material,
                         mesh_type="T6",
                         mesher="gmsh",
                         mesh_scale=1/5)
        # offset = None #shape.centroid
        offset = shape.centroid
        # shape = shape.translate(-shape.centroid)
        shape = shape.rotate(-0.4209)
        # shape = shape.translate(-offset)
        veux.serve(veux.draw_shape(shape, origin=True))
    else:
        import xara.units.mks as units
        # The geometric and material properties of the cantilever are: 
        # L = 1,400 mm, a = 76 mm, b = 51 mm, t = 6.5 mm, 
        # Young’s modulus E = 
        L = 1.4*units.m
        N = -60e3*units.N
        material = xara.Material(**{
            "name": "ElasticIsotropic", 
            "E":  193.05e3*units.MPa,
            # "G":  33.445e3*units.MPa,
            "nu": 0.3
        })
        shape = xs.Angle(b=51*units.mm,
                         d=76*units.mm,
                         t=6.4*units.mm,
                         mesh_scale=1/400)
        print(f"{shape.centroid = }, {shape._principal_rotation() = }")
        print(shape.summary())
        sc = shape.centroid
        shape = shape.translate(-shape.centroid)
    # veux.serve(veux.render(shape.model))

    section = xara.Section("MixedFiber", shape, 
                           mixed_type="U02" if not Warp else "NT")

    prism = Prism(shape=shape,
            length=L,
            boundary=((1,1,1,  1,1,1, 1),
                      (0,0,0,  0,0,0, 0)),
            material=material,
            element=element,
            section=section, #"ShearFiber",
            transform=transform,
            shear=Shear,
            vertical=3,
            # shear_warp=0,
            warp = [0] if Warp else None,
            divisions=10,
            order=3 if "Exact" in element else 1 # 3
    )
    model = prism.create_model()
    u, v, w = analyze(model, shape, L, N=N, offset=offset)

    fig, ax = plt.subplots()
    ax.plot(*zip(*u), label="$u_x$")
    ax.plot(*zip(*v), label="$u_y$")
    ax.plot(*zip(*w), label="$u_z$")
    # ax.set_xlim([0, None])
    ax.grid("on")
    ax.set_ylabel("Displacement")
    ax.set_ylim([0, None])
    ax.axhline(0, color='black', linestyle='-', linewidth=1)
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    plt.legend(ax)
    fig.savefig("img/1030-soln.png")
    plt.show()



    artist = veux.create_artist(model, vertical=3,
                                model_config={
                                    "frame_shape": shape,
                                })
    artist.draw_sections()
    artist.draw_sections(position=model.nodeDisp,
                         rotation=model.nodeRotation)
    
    veux.serve(artist)
