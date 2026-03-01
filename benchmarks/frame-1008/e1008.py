#
# Cantilever
#
import os
import time
import xara

# External libraries
import numpy as np
import matplotlib.pyplot as plt
from xara.post import PlotConvergenceRate


def create_cantilever(shape,
                      material,
                      L,
                      element,
                      transform="Corotational02",
                      shear=1,
                      ne=10):


    E = material["E"]
    G = material["G"]

    nen = 2
    nn = ne*(nen-1)+1

    model = xara.Model(ndm=3, ndf=6) #, echo_file=open(f"test-{element}-{transform}.tcl","w+"))

    sec = 1


    model.section("ElasticFrame", sec, **material, **shape)

    model.geomTransf(transform, 1, (0,0,1))

    for i,x in enumerate(np.linspace(0, L, nn)):
        model.node(i, (x,0,0))


    for i in range(ne):
        start = i * (nen - 1)
        nodes = tuple(range(start, start + nen))
        model.element(element, i+1, nodes, section=sec, transform=1, shear=shear)


    model.fix(0,     (1,1,1,  1,1,1))
    model.fix(nn-1,  (0,0,0,  0,0,0))
    return model


def analyze(model, Mmax, Fmax, nsteps=1, post=None):

    end = len(model.getNodeTags()) - 1
    #
    # Apply loading
    #
    model.pattern("Plain", 1, "Linear")
    model.load(end, (0,0,Fmax,  0,0,Mmax), pattern=1)

    model.system('Umfpack')
    model.integrator("LoadControl", 1/nsteps,
                    # iter=10,
                    # min_step=(1/nsteps)/100,
                    # max_step=(1/nsteps)/2
    )
    model.test("Residual", 1e-10, 55, 0) #50 #20
    model.algorithm("Newton")
    model.analysis("Static")

    ux = []
    uy = []
    P  = []
    ni = [5]
    L  = model.nodeCoord(end, 1)

    ux.append(  model.nodeDisp(end, 1)/L)
    uy.append(  model.nodeDisp(end, 2)/L)
    P.append(model.getTime())

    start = time.time()
    while model.getTime() < 1.0:
        if model.analyze(1) != 0:
            print(f"Failed at time = {model.getTime()}")
            break
        ni.append(model.numIter())
        ux.append(1+model.nodeDisp(end, 1)/L)
        uy.append(  model.nodeDisp(end, 2)/L)
        P.append(model.getTime())

        if post is not None:
            for p in post:
                p.update(model)

    t_end = time.time()

    print(sum(ni)/len(ni), np.array(model.nodeDisp(end))[:3]) # + model.nodeCoord(end))
    return ux, uy, P, ni



if __name__ == "__main__":
    length = 10.0

    material = dict(
        E = 1e4,
        G = 1e4
    )

    shape = dict(
        A   = 1,
        Ay  = 1,
        Az  = 1,
        Iy  = 1e-2,
        Iz  = 1e-2,
        J   = 1e-2
    )

    M0 = 20*np.pi # 2 pi EI /L

    analyze(create_cantilever(
                      shape,
                      material,
                      length,
                      ne=10,
                      shear=1,
                      element = "ExactFrame",
                      transform="Linear"),
              Mmax=M0/8, Fmax=1/16, nsteps=1)


    Transforms = [
        "Corotational",
        "Corotational02",
        "Corotational03",
        "Corotational04",
        "Corotational05"
    ]

    for transform in Transforms: #
        print(f"Transform: {transform}")
        model = create_cantilever(shape,
                                material,
                                length,
                                ne=10,
                                element = os.environ.get("Element", "ForceFrame"),
                                transform=transform)

        analyze(model, Mmax=M0/8, Fmax=1/16, nsteps=1)


    #
    #
    #
    print("\nLooping\n-------\n")
    markers = iter([":", "--", "-."]*2)
    colors  = iter(["#999393", "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"])
    fig, ax = plt.subplots(1,2, sharey=True)


    color = "#9E9E9E"

    post = [
        PlotConvergenceRate(ci=None, x_mode="time")
    ]

    post[-1].reset(label="ExactFrame")
    ux, uy, P,ni = analyze(create_cantilever(
                      shape,
                      material,
                      length,
                      ne=10,
                      shear=1,
                      element = "ExactFrame",
                      transform="Linear"),
              post=post,
              Mmax=5.0*M0, Fmax=25, nsteps=55)
    post[-1].draw()
    ax[0].plot(uy, P, "-", color=color, label="ExactFrame")
    ax[1].plot(ni, P, "-", color=color, label="ExactFrame")


    for transform in  Transforms: # "Linear",
        print(f"Transform: {transform}")
        model = create_cantilever(shape,
                                material,
                                length,
                                ne=10,
                                element = os.environ.get("Element", "ForceFrame"),
                                transform=transform)
        post[-1].reset(label=transform)
        ux, uy, P, ni = analyze(model, Mmax=5.0*M0, Fmax=25, nsteps=400, post=post)
        post[-1].draw()
        marker = next(markers)
        color  = next(colors)
        ax[0].plot(uy, P, marker, color=color, label=transform)
        ax[1].plot(ni, P, marker, color=color, label=transform)

    post[-1].finalize()
    ax[0].set_xlabel(r"Drift, $u_y/L$")
    ax[1].set_xlabel(r"Drift, $u_x/L$")
    ax[0].set_ylabel("Load, $P$")
    ax[0].set_xlim([None, 1.25])
    for axi in ax:
        axi.grid("on")
        # axi.set_xlim([None, 1.25])
        axi.set_ylim([0, None])
        axi.axvline(0, color='black', linestyle='-', linewidth=1)
        axi.axhline(0, color='black', linestyle='-', linewidth=1)
    axi.legend()

    # fig.savefig("img/frame-1008.png", dpi=600)
    plt.show()



