# OpenSees -- Open System for Earthquake Engineering Simulation
#         Pacific Earthquake Engineering Research Center
#
import os
import time
import veux
import xara
from xara.helpers import find_nodes, find_node
import xara.units.iks as units
from xsection.library import from_aisc

import numpy as np
import matplotlib.pyplot as plt

Verbose = True
if Verbose:
    Progress = lambda *args, **kwds: None
else:
    from tqdm import tqdm as Progress


def create_model(L, d, b, tw, tf, linear=True):
    # create ModelBuilder (with three-dimensions and 6 DOF/node)
    model = xara.Model(ndm=3, ndf=6)
    order = 1
    element = "ShellMITC4"  #"ASDShellQ4" #"ShellMITC9"# "ShellNLDKGQ" #,  #
    if linear:
        flags = () 
    else:
        flags = () #("-corotational", )#"-drillingNL")

    E = 30e3*units.ksi

    # Define sections
    # ------------------
    if linear:
        #                            tag E      nu    h    rho
        model.section("ElasticShell", 1, E, poisson, tw, 1.27)
        model.section("ElasticShell", 2, E, poisson, tf, 1.27)
    else:
        nip = 5
        model.material("NonlinearJ2", 1, E=E, 
                       nu=poisson, 
                       Fy=35.0*units.ksi, 
                       Hiso=0.002*E, 
                       Hkin=0.002*E)
        model.section("LayeredShell", 1, nip,
                      1, tw/nip,
                      1, tw/nip,
                      1, tw/nip,
                      1, tw/nip,
                      1, tw/nip)
        model.section("LayeredShell", 2, nip,
                      1, tf/nip,
                      1, tf/nip,
                      1, tf/nip,
                      1, tf/nip,
                      1, tf/nip)
    # Define geometry
    # ---------------
    # these should both be even

    if linear:
        nx = 20 #240
        ny = 2 #8
        nz = 4
    else:
        nx = 30 # 200
        ny = 4 # 4
        nz = 8


    # Flanges
    model.surface((nx, ny),
                  order=order,
                  element=element, 
                  args=("-section", 2, *flags),
                  points={
                      1: [ 0, -b/2, d/2],
                      2: [ L, -b/2, d/2],
                      3: [ L,  b/2, d/2],
                      4: [ 0,  b/2, d/2],
                  })

    model.surface((nx, ny),
                  order=order,
                  element=element, 
                  args=("-section", 2, *flags),
                  points={
                      1: [ 0, -b/2, -d/2],
                      2: [ L, -b/2, -d/2],
                      3: [ L,  b/2, -d/2],
                      4: [ 0,  b/2, -d/2],
                  })

    # Web
    model.surface((nx, nz),
                  order=order,
                  element=element, 
                  args=("-section", 1, *flags),
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
        Cases = [2,3]

    poisson = 0.25


    nstep = 800
    Uult = 0.5
    dU   = Uult/nstep
    dPmx = dU
    dPmn = dU/100
    siter = 2

    L = 28*units.inch
    shape = from_aisc("W18x40",
                      units=units,
                      mesh_scale=1/2,
                      poisson=poisson,
                      fillet=True,
                      mesh_type="T6",
                      mesher="gmsh")

    for case in Cases:
        print(f"Case {case}")
        model = create_model(
            L=L, 
            b=shape.bf,
            d=shape.d, 
            tw=shape.tw, 
            tf=shape.tf, 
            linear=linear)
        artist = veux.create_artist(model, vertical=3)
    #   artist.draw_surfaces()
        artist.draw_outlines()

        if case == 1:
            for node in find_nodes(model, x=0):
                model.fix(node, (1,1,1, 1,1,1))
            for node in find_nodes(model, x=L):
                model.fix(node, (1,1,0, 1,1,1))
        elif case == 2:
            for node in find_nodes(model, x=0, y=0):
                model.fix(node, (1,1,1, 1,1,1))
            for node in find_nodes(model, x=L, y=0):
                model.fix(node, (1,1,0, 1,1,1))
        elif case == 3:
            model.fix(find_node(model, x=0,y=0.,z= shape.d/2), (1,1,1, 1,1,1))
            # model.fix(find_node(model, x=0,y=shape.b/2,z= shape.d/2), (1,1,1, 1,1,1))
            model.fix(find_node(model, x=0,y=0.,z=-shape.d/2), (1,1,1, 1,1,1))
            # model.fix(find_node(model, x=0,y=10,z=-shape.d/2), (1,1,1, 1,1,1))

            model.fix(find_node(model, x=L,y=0.,z= shape.d/2), (1,1,0, 1,1,1))
            # model.fix(find_node(model, x=L,y=10,z= shape.d/2), (1,1,0, 1,1,1))
            model.fix(find_node(model, x=L,y=0.,z=-shape.d/2), (1,1,0, 1,1,1))
            # model.fix(find_node(model, x=L,y=10,z=-shape.d/2), (1,1,0, 1,1,1))
        elif case == 4:
            dU   = Uult/200
            dPmx = Uult/100
            dPmn = Uult/400
            siter = 50
            model.fix(find_node(model, x=0,y=0.,z= shape.d/2), (1,1,1, 1,1,1))
            model.fix(find_node(model, x=0,y=0.,z=-shape.d/2), (1,1,1, 1,1,1))


        tip = find_node(model, x=L,y=0,z=shape.d/2)

        #
        # Perform the analysis
        #
        u = []
        ux = []
        uy = []
        P = []
        model.numberer("AMD")
        model.system('mumps')
        model.constraints("Transformation")
        model.test("Energy", 1e-18, 20, 2)

        model.timeSeries("Path", 1,
                         values=[0,  Uult, -Uult, 0.0],
                         time=  [0,   1,       4,   5])

        # model.integrator("LoadControl", 
        #                 dP, # 50
        #                 min_step=dPmn,
        #                 max_step=dPmx, # 10
        #                 iter=siter # 50
        # )
        model.pattern("Plain", 1, 1)
        for node in find_nodes(model, x=L):
            model.sp(node, 3, 1.0, pattern=1)
        model.integrator("LoadControl", dU, 
                        # min_step=dPmn,
                        # max_step=dPmx,
                        # iter=siter
        )
        model.analysis("Static")

        pbar = Progress(total=nstep*5)
        try:

            tstart = time.time()
            # for i in range(nstep*5):
            while model.state.time < 5.0:
                if model.analyze(1) != 0:
                    break
                if pbar is not None:
                    pbar.update(i)
                    pbar.set_postfix(iter=model.numIter())
                ux.append(model.nodeDisp(tip, 1))
                uy.append(model.nodeDisp(tip, 2))
                u.append(model.nodeDisp(tip, 3))
                model.reactions()
                P.append( sum(model.nodeReaction(node, 3) for node in find_nodes(model, x=L)))

            tend = time.time()
            print(f"Case {case} took {tend - tstart} seconds")
        except KeyboardInterrupt:
            pass

        ax.plot(u, P, label=f"Case {case}")

        np.savetxt(f"out/shell-2007-case{case}-pu.txt",
                    np.column_stack((P, u, ux, uy)),
                    header="P u3 ux uy"
        )
    # ax.grid(True)
    # ax.legend()

    # plt.show()
    # artist.draw_surfaces(state=model.nodeDisp)
    # veux.serve(artist)


