# Simply supported angle under torsion and flexure
import os
import sys
import veux
import xara
import numpy as np
import xsection.library as xs
from xara.benchmarks import Prism
from xara.helpers import find_node
import xara.units.ips as units
import matplotlib.pyplot as plt


def read_engel(exclude=None):
    import json 
    with open("engel/engel.json") as f:
        data = json.load(f)

    if exclude is None:
        exclude = set()
    return {
        dset["name"]: {
            "T": [item["value"][1] for item in dset["data"]],
            "theta": [item["value"][0] for item in dset["data"]],
        }
        for dset in data["datasetColl"] if dset["name"] not in exclude
    }


def create_model(element, section, shape, material, mixed_type=None):
    print(f"Element = {element}, Section = {section}")
    model = xara.Model(ndm=3, ndf=6)

    L = 36.8*units.inch


    model.node(1, 0,0,0)
    model.node(2, L/2,0,0)
    model.node(3, L,0,0)
    model.fix(1, 1,1,1, 1,0,0)
    model.fix(3, 0,1,1, 0,0,0)

    E = material["E"]
    G = material["G"]
    model.material("ElasticIsotropic", 1, E=E, G=G)

    if section == "Fiber":
        G = E/(2*(1+nu))
        GJ = shape.elastic.J*G
        model.section("Fiber", 1, GJ=GJ)
        for fiber in shape.create_fibers():
            y = fiber["y"]
            z = fiber["z"]
            A = fiber["area"]
            model.fiber(y, z, A, material=1, section=1)

    elif section == "ShearFiber":
        model.section("ShearFiber", 1, mixed_type=mixed_type)
        for fiber in shape.create_fibers():
            model.fiber(**fiber, material=1, section=1)

    elif section == "Elastic":
        G = E/(2*(1+nu))
        model.section("ElasticFrame", 1,
                        E=E,
                        G=G,
                        A=shape.elastic.A,
                        Ay=shape.elastic.A,
                        Az=shape.elastic.A,
                        Iy=shape.elastic.Iy,
                        Iz=shape.elastic.Iz,
                        J =shape.elastic.J
                    )

    model.geomTransf("Corotational02", 1, (0,0,1))
    model.element(element, 1, (1,2), section=1, transform=1, shear=0)
    model.element(element, 2, (2,3), section=1, transform=1, shear=0)

    return model




def analyze(model, shape, sc, L, M, T):
    N = 0 # M/sc[1]
    print(f"{N = }, {M = }, {T = }")
    model.pattern("Plain", 1, "Linear", load={
        find_node(model, x=L)  : [-N,0,0, 0, M,0],
        find_node(model, x=0)  : [ N,0,0, 0,-M,0]
    })

    steps = 20 # 40
    model.integrator("LoadControl", 1/steps)
    model.system('Umfpack')
    model.test("Energy", 1e-20, 40, 2)
    model.analysis("Static")
    for _ in range(steps):
        if model.analyze(1) != 0:
            print(f"Failed at time = {model.getTime()} with {M = }")
            return []

    model.loadConst(time=0)

    model.pattern("Plain", 2, "Linear", load={
        find_node(model, x=L/2): [0,0,0, T,0,0],
    })
    # model.pattern("Plain", 2, "Linear")
    # offset = [1, 0,0] #*(-shape._analysis.shear_center()).tolist()]
    # element = find_node(model, x=L/2)-1
    # print(f"{offset = }, {element = }")
    # model.eleLoad("Frame",
    #               "Point",
    #               basis="local",
    #               offset=offset,
    #               couple=[T,0,0],
    #               pattern=2,
    #               elements=element
    # )


    # Analyze
    u = []
    for _ in range(steps):
        u.append([
            abs(T*model.getTime()),
            abs(model.nodeDisp(find_node(model, x=L/2),4)/(L/2))
        ])
        if model.analyze(1) != 0:
            print(f"Failed at time = {model.getTime()} with {M = }")
            break

    return u


if __name__ == "__main__":
    os.environ["Wagner"] = "1"
    L = 36.8*units.inch
    shape = xs.Angle(b=1*units.inch,
                     d=1*units.inch,
                     t=0.03*units.inch,
                     mesh_scale=1/300)

    print(f"{shape.centroid = }")
    # shape = shape.translate(-shape.centroid).rotate(3*np.pi/4)
    shape = shape.rotate(-3*np.pi/4)
    sc = shape.centroid
    # shape = shape.translate(-shape.centroid)
    # shape = shape.translate([0, np.sqrt(2)/2])
    # shape = shape.rotate(1*np.pi/4)
    # veux.serve(veux.render(shape.model))
    material = {
        "name": "ElasticIsotropic",
        "E":  10e3*units.ksi,
        "G":  3.75e3*units.ksi,
    }

    u = []
    fig, (ax, legend) = plt.subplots(ncols=2, gridspec_kw={'width_ratios': [5, 1.5]})
    legend.axis('off')

    ax.plot([0, 4*units.lbf*units.inch],
            [0, (4*units.lbf*units.inch)/(shape.elastic.J*material['G'])],
            'k-', label="Linear")


    # ax.plot(
    #     *(np.loadtxt("out/extracted_circles_estimated_coords.csv", delimiter=',',skiprows=1).T[3:]), "o", 
    #     label="Engel (1975)", markersize=4, markerfacecolor='none'
    # )
    styles = iter(["--", "-.", ":", (0, (3,1,1,1)), (0, (5,1)), (0, (3,1,1,1,1,1)), "-"])
    colors = iter(["r", "b", "g", "m", "c", "orange", "brown"])
    moments = [#-0.65, 
               #0, 
               9.1, 18.9, 28.6, 38.4,
               48.2
    ]
    for M in moments:
        # model = create_model("ForceFrame", "ShearFiber", 
        #                      shape, material, mixed_type="UT")
        prism = Prism(shape=shape,
                length=L,
                boundary=((1,1,1,  1,0,0), 
                          (0,1,1,  0,0,0)),
                material=material,
                element="ForceFrame",
                section="ShearFiber",
                transform="Corotational02",#"Linear",  # 
                # joint_offset={
                #     1: [0, 0, sc[1]],
                #     2: [0, 0, sc[1]],
                # },
                shear=1,
                vertical=3,
                # shear_warp=0,
                divisions=20,
                order=1
        )
        model = prism.create_model()
        u = analyze(model, shape, sc, L,
                    M=-M*units.lbf*units.inch,
                    T=-4.5*units.lbf*units.inch)

        ax.plot([ui[0] for ui in u], [ui[1] for ui in u],
                color=next(colors),
                linestyle=next(styles),
                label=f"$M={M}$ in-lbf")

    print(f"{sc = }, {shape.elastic.J = }")

    # Add Engel experiment data
    i = 0
    for name, data in read_engel().items():
        label = f"Experiment" if i==0 else None
        i += 1
        ax.plot(data["T"], data["theta"], "o", 
                label=label, markersize=5, 
                markerfacecolor='none',
                markeredgecolor='k')
    del i

    ax.set_xlabel(r"Torque $\bar{T}$ (in-lbf)")
    ax.set_ylabel(r"Average Twist $\bar{\vartheta}$ (rad/in)")
    ax.set_ylim([0, 0.03])
    ax.set_xlim([0, 4*units.lbf*units.inch])
    ax.grid("on")
    legend.legend(*ax.get_legend_handles_labels(), borderaxespad=0)
    plt.tight_layout()
    fig.savefig("img/frame-1041-solution.png", dpi=600)
    plt.show()
