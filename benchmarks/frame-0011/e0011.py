# Test of the warping DOF
# Linear 7-DOF analysis of a cantilever subjected to a torque
#
import os
import sys

import veux
from veux.motion import Motion
from xsection.library import WideFlange, HollowRectangle, Channel, Rectangle, Circle

import opensees.openseespy as ops
import pandas as pd

# External libraries
import numpy as np
import matplotlib.pyplot as plt
try:
    plt.style.use("veux-web")
except:
    pass


class Shaft:
    def __init__(self, case, L, shape, material):

        J = shape._analysis.torsion_constant()
        GJ = material["G"]*J
        E = material["E"]
        Cv  = shape.cvv()[0,0]
        Cw  = shape.cww()[0,0]

        eta = 1 + J/Cv
        lam = np.sqrt(GJ/(eta*E*Cw))

        self.GJ = GJ
        self.eta = eta
        self.lam = lam

        if case == "b":
            self.C1 = -np.tanh(lam*L)
            self.C2 = -self.C1
            self.C3 = -1
        elif case == "c":
            self.C1 = (1- np.cosh(lam*L))/np.sinh(lam*L)
            self.C2 = -self.C1
            self.C3 = -1

    def angle(self, x, T):
        return T/(self.GJ*self.lam*self.eta)*(
            self.C1 \
                + self.C2*np.cosh(self.lam*x) \
                    + self.C3*np.sinh(self.lam*x) \
                        + x*self.lam*self.eta
        )
        # return self.C1 \
        #     +  self.C2*np.cosh(self.lam*x) \
        #     +  self.C3*np.sinh(self.lam*x) \
        #     +  T/(self.GJ)*x


def create_cantilever(aspect,
                      shape,
                      material,
                      case="a",
                      ne=10,
                      nen=2,
                      element="ExactFrame",
                      section="Elastic"):


    E = material["E"]
    G = material["G"]
    v = 0.5*E/G - 1

    L   = shape.d/aspect
    nn = ne*(nen-1)+1

    model = ops.Model(ndm=3, ndf=7)

    model.eval(f"set E {E}")
    model.eval(f"set G {G}")
    model.eval(f"set L {L}")

    mat = 1
    sec = 1
    model.material('ElasticIsotropic', mat, E, v)


    if section == "Elastic":
        cmm = shape.cmm()
        cnn = shape.cnn()
        cnv = shape.cnv()
        cnm = shape.cnm()
        cmw = shape.cmw()
        cvv = shape.cvv()
        cww = shape.cww()
        A = cnn[0,0]
        model.section("ElasticFrame", sec,
                        E=E,
                        G=G,
                        A=A,
                        Ay=1*A,
                        Az=1*A,
#                       Qy=cnm[0,1],
#                       Qz=cnm[2,0],
                        Iy=cmm[1,1],
                        Iz=cmm[2,2],
                        J = shape._analysis.torsion_constant(),
                        Cw= cww[0,0],
                        Ry= cnv[1,0],
                        Rz= cnv[2,0],
                        Sy= cvv[1,1],
                        Sz= cvv[2,2]
        )
    else:


        model.section("ShearFiber", 1, GJ=0)


        for fiber in shape.create_fibers():

            model.fiber(**fiber, material=mat, section=1)



    model.geomTransf("Linear", 1, (0,0,1))


    for i,x in enumerate(np.linspace(0, L, nn)):
        model.node(i, (x,0,0))

    for i in range(ne):
        start = i * (nen - 1)
        nodes = list(range(start, start + nen))
        model.element(element, i+1, nodes, section=1, transform=1, shear=1)

    wi = int(case in "cb")
    wj = int(case in "c")

    model.fix(0,     (1,1,1,  1,1,1, wi))
    model.fix(nn-1,  (0,0,0,  0,0,0, wj))
    return model, shape


if __name__ == "__main__":
    th = 0.05 #0.05
    depth = 20

    # shape = Channel(
    #             tf=th*depth,
    #             tw=th*depth,
    #             d=depth,
    #             b=depth*0.4,
    #             mesh_scale=1/400 #800
    # )
    # shape = shape.translate(shape._analysis.shear_center())

    # shape = Rectangle(d=depth, b=0.4*depth, mesh_scale=1/200)

    # shape = Circle(depth/2, divisions=8, mesh_scale=1/200)

    # # W21x93
    # shape = WideFlange(
    #             tf = 0.93,
    #             tw = 0.58,
    #             d  = 21.62,
    #             b  = 8.42,
    #             mesh_scale=1/200
    #         )

    shape = HollowRectangle(
                tf = th*depth*2,
                tw = th*depth,
                d  = depth,
                b  = depth*0.4,
                mesh_scale=1/200
            )

    material = dict(
        G = 11.2e3,
        E = 29e3
    )

    print(shape.summary())

    element = os.environ.get("Element", "ExactFrame")
    section = os.environ.get("Section", "ShearFiber")

    GJ = material["G"]*shape._analysis.torsion_constant()
    Cv  = shape.cvv()[0,0]
    Cw  = shape.cww()[0,0]

    # print(f"eta = {eta}, lam = {lam}")

    for case in "cb":

        # slenderness = 0.5
        fig,  ax  = plt.subplots()
        ax.set_xlabel(r"Number of elements, $n$")
        ax.set_ylabel(r"Flexibility, $(T/\vartheta)/\bar{F}$")
        ax.axvline(0, color='black', linestyle='-', linewidth=1)
        ax.axhline(0, color='black', linestyle='-', linewidth=1)
        for slenderness in [5, 1, 0.5]:
            u = []
            P = []
            for n in [1, 2, 4, 8, 16, 24]:


                model, shape = create_cantilever(
                    slenderness,
                    shape,
                    material,
                    case,
                    ne=n,
                    nen=3 if element == "ExactFrame" else 2,
                    section = section,
                    element = element)
                end = model.getNodeTags()[-1]
                L = model.nodeCoord(end, 1)


                # Apply torsional moment
                nsteps =  5
                Mmax   = 1.2e3
                model.pattern("Plain", 1, "Linear")
                model.load(end, (0,0,0,  1,0,0,  0), pattern=1)

                model.system('Umfpack')
                model.numberer("Plain")
                model.integrator("LoadControl", Mmax/nsteps)
                model.test("Energy", 1e-12, 10,1)
                model.algorithm("Newton")
                model.analysis("Static")

                while model.getTime() < Mmax:
                    if model.analyze(1) != 0:
                        print(f"Failed at time = {model.getTime()}")
                        sys.exit()
                        break

                model.reactions()
                u.append(n)
                P.append((model.getTime()/model.nodeDisp(end,4))/(GJ/L))

            ax.plot(u, P, label=f"$h/L = {slenderness}$")
            ax.axhline((Mmax/Shaft(case, L, shape, material).angle(L, Mmax))/(GJ/L),
                       linestyle='--', color="gray")

        marker = "+x."["abc".index(case)]
        color  = "rbg"["abc".index(case)]
        _,    (ax2, ax3) = plt.subplots(2, 1, sharex=True)
        _,    (ax4, ax5) = plt.subplots(2, 1, sharex=True)


        ax2.set_ylabel(r"Twist, $\vartheta$")
        ax2.axvline(0, color='black', linestyle='-', linewidth=1)
        ax2.axhline(0, color='black', linestyle='-', linewidth=1)

        ax3.set_xlabel("$x/L$")
        ax3.set_ylabel(r"Warp")
        ax3.axvline(0, color='black', linestyle='-', linewidth=1)
        ax3.axhline(0, color='black', linestyle='-', linewidth=1)

        ax4.set_ylabel(r"$B$")
        ax4.axvline(0, color='black', linestyle='-', linewidth=1)
        ax4.axhline(0, color='black', linestyle='-', linewidth=1)
        ax5.set_ylabel(r"$Q$")
        ax5.axvline(0, color='black', linestyle='-', linewidth=1)
        ax5.axhline(0, color='black', linestyle='-', linewidth=1)
        ax5.set_xlabel("$x/L$")


        x = np.array([model.nodeCoord(node, 1) for node in model.getNodeTags()])


        twist = [model.nodeDisp(node,4) for node in model.getNodeTags()]
        ax2.plot(x/L, twist, ".")
        ax3.plot(x/L,
                [model.nodeDisp(node,7) for node in model.getNodeTags()],
                ":",
                label=r"$\alpha$"
        )
        rate = np.gradient(twist, x)
        ax3.plot(x/L, rate, "--", label=r"$\vartheta'$")


        xs = [(x+model.nodeCoord(model.eleNodes(tag)[0], 1))/L
              for tag in model.getEleTags()
                for x in np.atleast_1d(model.eleResponse(tag, "integrationPoints"))
        ]
        ws = [
            model.eleResponse(tag, "section", i+1, "resultant")[6]/(Mmax*L)
            for tag in model.getEleTags()
            for i in range(len(np.atleast_1d(model.eleResponse(tag, "integrationPoints"))))
        ]
        ax4.plot(xs, ws, "-")
        vs = [
            model.eleResponse(tag, "section", i+1, "resultant")[9]/Mmax
            for tag in model.getEleTags()
            for i in range(len(np.atleast_1d(model.eleResponse(tag, "integrationPoints"))))
        ]
        ax5.plot(xs, vs, "-")

        #
        # Plot the analytical solution
        #

        x = np.linspace(0,L,100)
        ax2.plot(x/L, Shaft(case, L, shape, material).angle(x, Mmax), "-.", label="Exact")


        ax.legend()
        ax3.legend()
        ax2.legend()
        ax4.legend()

        fig.savefig(f"img/e0011-convergence-{case}.png")
        ax3.figure.savefig(f"img/e0011-kinematics-{case}.png")
        ax4.figure.savefig(f"img/e0011-resultants-{case}.png")
        plt.show()

