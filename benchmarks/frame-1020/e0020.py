#
# Cantilever beam subjected to follower end load.
#
import sys
import veux
import numpy as np
from veux.motion import Motion
import xara
from xara.post import PlotConvergenceRate

import matplotlib.pyplot as plt
try:
    plt.style.use("typewriter")
except:
    pass

def create_cantilever(ne, element):
    model = xara.Model(ndm=3, ndf=6)

    L  = 100

    nen = 2
    nmn = ne*(nen-1)+1
    sec = 1
    A = 1.61538e8
    I = 3.5e7
    model.section("ElasticFrame", sec,
                    E=1,
                    G=1,
                    A=A,
                    Ay=A,
                    Az=A,
                    Iy=I*100,
                    Iz=I,
                    J =I
    )

    model.geomTransf("Corotational02", 1, (0,0,1))

    for i,x in enumerate(np.linspace(0, L, nmn)):
        model.node(i, (x,0,0))

    for i in range(ne):
        start = i * (nen - 1)
        nodes = list(range(start, start + nen))
        model.element(element, i+1, nodes,
                      section=sec, transform=1, shear=1)

    model.fix(0,  (1,1,1,  1,1,1))
    for i in range(nmn):
        model.nodeRotation(i)

    return model


def analyze(element, post=None):
    ne = 10

    model = create_cantilever(ne, element=element)
    artist = veux.create_artist(model, model_config=dict(extrude_outline="square"))
    artist.draw_nodes(size=10)
    artist.draw_sections()
    motion = Motion(artist)

    #
    # Apply vertical load
    #
    speed  = 1/3000 # animation frames
    Pmax   = 150e3 # N
    model.pattern("Plain", 1, "Linear")


    model.eleLoad("Frame", "Dirac",
                  force = [0, 1, 0],
                  basis = "director",
                  offset=[1.0,0,0],
                  pattern=1,
                  elements=[ne]
    )

    model.system('Umfpack')
    model.integrator("LoadControl", Pmax/500)
    model.test("NormDispIncr", 1e-12, 10, 2)
#   model.test('NormUnbalance',1e-6,100,1)
    model.algorithm("Newton")
    model.analysis("Static")

    u = []
    v = []
    w = []
    P = []
    while model.state.time < Pmax:
        if model.analyze(1) != 0:
            print(f"Failed at time = {100*model.getTime()/Pmax}% with v = {v[-1]}")
            break
        motion.advance(time=model.getTime()*speed)
        motion.draw_sections(rotation=model.nodeRotation,
                             position=model.nodeDisp)
        u.append(-model.nodeDisp(ne, 1))
        v.append( model.nodeDisp(ne, 2))
        w.append( model.nodeDisp(ne, 3))
        P.append( model.getTime())

        if post is not None:
            for p in post:
                p.update(model)


    post[-1].draw()
    post[-1].finalize()
    if True:
        fig, ax = plt.subplots()
        ax.set_xlabel("Load, $P$")
        ax.set_ylabel(r"Displacement")
        ax.axvline(0, color='black', linestyle='-', linewidth=1)
        ax.axhline(0, color='black', linestyle='-', linewidth=1)
        ax.plot(P, u, label="$u$")
        ax.plot(P, v, label="$v$")
        ax.plot(P, w, label="$w$")
        ax.set_xlim([0, None])
        ax.legend()
        # ax.savefig(f"img/1020-{element[:5]}-displacement.png")
        plt.show()

    motion.add_to(artist.canvas)
    if len(sys.argv) > 1:
        artist.save(sys.argv[1])
    else:
        veux.serve(artist)

    return {
        "motion": motion,
        "convergence": post[-1],
    }


if __name__ == "__main__":
    import os

    analyze(element = os.environ.get("Element", "ExactFrame"),
            post=[PlotConvergenceRate(ci=None, x_mode="step")]
    )

