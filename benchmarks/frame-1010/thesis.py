#
# Hockling problem, as desribed by Perez and Filippou (2024).
#
# https://onlinelibrary.wiley.com/doi/10.1002/nme.7506
#
import os
from xara.benchmarks import Prism
import xara
from shps.rotor import exp
import numpy as np
import veux
import matplotlib.pyplot as plt


if __name__ == "__main__":

    ne = 20
    E  = 71_240
    G  = 27_190
    I  = 0.0833
    A  = 10.0
    J  = 2.16

    fig, ax = plt.subplots()
    ax.grid("on")
    ax.axvline(0, color='k', lw=0.5)
    ax.axhline(0, color='k', lw=0.5)

    for element in ["ExactFrame", "ForceFrame"]:
        prism = Prism(
            length = 240.,
            element = element,
            material = dict(
                E   = E,
                G   = G,
            ),
            shape   = dict(
                A   = A,
                J   = J,
                Iy  = I,
                Iz  = I,
                Ay  = A,
                Az  = A),
            boundary = ((1,1,1, 1,1,1),
                        (0,1,1, 0,1,1)),
            transform = "Corotational02",
            divisions = ne,
            rotation = exp([0,  0.0, 0.005])
        )

        model = prism.create_model()


        #
        # Analysis
        #
        scale = 5 #0.0
        steps = 65
        Tref  = 2*E*I/prism.length
    #   model.test("EnergyIncr", 1e-9, 55, 1)
        model.test("NormDispIncr", 1e-9, 45, 1)
    #   model.test("RelativeNormDispIncr", 1e-6, 50, 1)

        f = [0, 0, 0] + list(map(float, [Tref, 0, 0]))
        model.pattern("Plain", 1, "Linear", load={
            ne+1: f
        })

        model.integrator("MinUnbalDispNorm", 1, 5,  1/steps/1000, 1)
    #   model.integrator("MinUnbalDispNorm", 1/30, 5,  1/steps/1000, 1/20, det=True)
    #   model.integrator("LoadControl", 1/steps, 5, 1/steps/100, 1.5/steps) #scale/steps)
    #   model.integrator("ArcLength", 1/64, det=True, exp=0.5)
        model.system("Umfpack")
        model.analysis("Static")

        artist = veux.create_artist(model)
        artist.draw_axes()
        artist.draw_outlines()

        u = []
        lam = []
        time = []

        for i in range(400):
            u.append(model.nodeDisp(ne+1, 4)/np.pi)
            time.append(model.getTime())
            lam.append(model.getLoadFactor(1))

            if model.analyze(1) != 0:
                break
                raise RuntimeError(f"Failed at step {i}")

    #       artist.draw_outlines(state=model.nodeDisp)

        ax.plot(u, lam,  '.')
        ax.plot(u, time, '.')
    fig.savefig("img/1030-Hockling-loadpath.png")

    # fig, ax = plt.subplots()
    # ax.plot(lam, u, '-')
    plt.show()

#   veux.serve(artist)


