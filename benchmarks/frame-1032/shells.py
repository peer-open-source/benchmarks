# OpenSees -- Open System for Earthquake Engineering Simulation
#         Pacific Earthquake Engineering Research Center
#
import os
import veux
import xara
from xara.helpers import find_nodes, find_node

import numpy as np
import matplotlib.pyplot as plt

Verbose = False
if Verbose:
    Progress = lambda *args, **kwds: None
else:
    from tqdm import tqdm as Progress


def create_model(L, d, b, tw, tf, linear=True):
    # create ModelBuilder (with three-dimensions and 6 DOF/node)
    model = xara.Model(ndm=3, ndf=6)
    element = "ASDShellQ4" #"ShellNLDKGQ" #,  #"ShellMITC4"  #
    if linear:
        flags = () 
    else:
        flags = ("-corotational", )#"-drillingNL")

    E = 2.1e4

    # Define sections
    # ------------------
    #                            tag E   nu    h    rho
    model.section("ElasticShell", 1, E, 0.30, tw, 1.27)
    model.section("ElasticShell", 2, E, 0.30, tf, 1.27)

    # Define geometry
    # ---------------
    # these should both be even
    if linear:
        nx = 50 #240
        ny = 2 #8
    else:
        nx = 240 # 200
        ny = 8 # 4

    # Flanges
    model.surface((nx, ny),
                  element=element, args=(2, *flags),
                  points={
                      1: [ 0,  0, d/2],
                      2: [ L,  0, d/2],
                      3: [ L,  b, d/2],
                      4: [ 0,  b, d/2],
                  })

    model.surface((nx, ny),
                  element=element, args=(2, *flags),
                  points={
                      1: [ 0,  0, -d/2],
                      2: [ L,  0, -d/2],
                      3: [ L,  b, -d/2],
                      4: [ 0,  b, -d/2],
                  })

    # Web
    model.surface((nx, ny),
                  element=element, args=(1, *flags),
                  points={
                      1: [ 0,  0,  d/2],
                      2: [ L,  0,  d/2],
                      3: [ L,  0, -d/2],
                      4: [ 0,  0, -d/2],
                  })

    return model

if __name__ == "__main__":
    linear=False
    fig, ax = plt.subplots()
    if "Case" in os.environ:
        Cases = [int(os.environ["Case"])]
    else:
        Cases = [1,2,5]


    Pult = 20.0
    dP   = Pult/200
    dPmx = Pult/100
    dPmn = Pult/800
    siter = 300
    for case in Cases:
        print(f"Case {case}")
        model = create_model(L=900, b=10, d=30, tw=1, tf=1.6, linear=linear)
        artist = veux.create_artist(model, vertical=3)
    #   artist.draw_surfaces()
        artist.draw_outlines()

        if case == 1:
            for node in find_nodes(model, x=0):
                model.fix(node, (1,1,1, 1,1,1))
        elif case == 2:
            dP = Pult/100
            dPmx = Pult/50
            dPmn = Pult/400
            siter = 100
            for node in find_nodes(model, x=0, y=0):
                model.fix(node, (1,1,1, 1,1,1))
        elif case == 3:
            model.fix(find_node(model, x=0,y=0.,z= 15), (1,1,1, 1,1,1))
            model.fix(find_node(model, x=0,y=10,z= 15), (1,1,1, 1,1,1))
            model.fix(find_node(model, x=0,y=0.,z=-15), (1,1,1, 1,1,1))
            model.fix(find_node(model, x=0,y=10,z=-15), (1,1,1, 1,1,1))
        elif case == 4:
            dP   = Pult/200
            dPmx = Pult/100
            dPmn = Pult/400
            siter = 50
            model.fix(find_node(model, x=0,y=0.,z= 15), (1,1,1, 1,1,1))
            model.fix(find_node(model, x=0,y=0.,z=-15), (1,1,1, 1,1,1))
        # elif case == 5:
        #     for node in find_nodes(model, x=0, y=0):
        #         model.fix(node, (1,1,1, 1,1,1))


        tip = find_node(model, x=900,y=0,z=15)
        model.pattern("Plain", 1, "Linear", loads={
            tip: (0,0,-1, 0,0,0)
        })

        #
        # Perform the analysis
        #
        u = []
        ux = []
        uy = []
        P = []
        model.numberer("AMD")
        model.system('mumps')
        model.test("Energy", 1e-16, 600, 2 if Verbose else 0)
        model.integrator("LoadControl", 
                            dP, # 50
                            min_step=dPmn,
                            max_step=dPmx, # 10
                            iter=siter # 50
        )
        # model.algorithm("Broyden") #"NewtonLineSearch", 0.7)
        model.analysis("Static")

        pbar = Progress(total=Pult)
        try:
            while (time := model.getTime()) < Pult:
                if model.analyze(1) != 0:
                    break
                if pbar is not None:
                    pbar.update(model.getTime() - time)
                    pbar.set_postfix(iter=model.numIter())
                ux.append(model.nodeDisp(tip, 1))
                uy.append(model.nodeDisp(tip, 2))
                u.append(-model.nodeDisp(tip, 3))
                P.append( model.getTime())
        except KeyboardInterrupt:
            pass

        ax.plot(u, P, label=f"Case {case}")

        # np.savetxt(f"out/shell-1032-case{case}-pu.txt",
        #             np.column_stack((P, u, ux, uy)),
        #             header="P u3 ux uy"
        # )
    ax.grid(True)
    ax.legend()

    plt.show()
    artist.draw_surfaces(state=model.nodeDisp)
    veux.serve(artist)


