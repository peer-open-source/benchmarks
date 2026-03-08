# Test of the warping DOF
#
# Linear 7-DOF analysis of a cantilever subjected to a torque
#
import os

import veux
from veux.motion import Motion
from xsection.analysis import SaintVenantSectionAnalysis
from xsection.library import WideFlange, HollowRectangle, Channel, Rectangle, Circle

import xara
from xara import Section, Material

# External libraries
import numpy as np
import matplotlib.pyplot as plt
try:
    plt.style.use("veux-web")
except:
    pass

from plots import (
    PlotTwist2, 
    PlotConvergence,
    plot_resultants, 
    plot_kinematics
)
from model import create_cantilever, analyze

class Shaft:
    def __init__(self, case, L, shape, warp_type=None, sv=None):
        if warp_type is None:
            warp_type = "NT"
        
        self.warp_type = warp_type
        if sv is None:
            sv = SaintVenantSectionAnalysis(shape)

        # J = shape._analysis.torsion_constant()

        GJ = sv.twist_rigidity() # = GIo - GJv
        # E = material["E"]
        GJv  = shape.cvv()[0,0]
        ECw  = shape.cww()[0,0]
        GIo  = GJ + GJv
        if warp_type == "NT":
            eta = 1 + GJ/GJv
            GJvm = GJ
        else:
            E = shape.material["E"]
            G = shape.material["G"]
            EJa = sv.css()*E/G
            b = ECw/EJa

            Jm = (GJv - b*ECw)
            eta_bar = Jm/(GJv-2*b*ECw+b**2*EJa)
            eta_hat = (GIo - eta_bar*Jm)/(GJv - eta_bar*Jm)
            if False:
                eta = 1 + GJ/(ECw**2/EJa)
            else:
                eta = eta_hat

            print(f"eta_bar = {eta_bar}, eta_hat = {eta_hat}, eta = { 1 + (E/G)*GJ/(ECw**2/EJa)}")
            # assert abs(eta_bar - 1.0) < 1e-10, f"Unexpected eta_bar = {eta_bar}"
            # assert abs(eta_hat - eta) < 1e-10, f"Unexpected eta_hat = {eta_hat}"


            if True:
                print(f"Jw = {ECw/E}, Ja = {EJa/E}, Jv = {GJv/G}, Jm = {Jm/G}, eta = {eta}")

        lam = np.sqrt(GJ/(eta*ECw))

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
        elif case == "a":
            self.C1 = 0
            self.C2 = 0
            self.C3 = 0

    def twist(self, x, T)->float:
        return T/(self.GJ*self.lam*self.eta)*(
            self.C1 \
                + self.C2*np.cosh(self.lam*x) \
                    + self.C3*np.sinh(self.lam*x) \
                        + x*self.lam*self.eta
        )


if __name__ == "__main__":
    th = 0.1 #0.05
    depth = 20
    width = 8 # depth*0.4
    Failed = []

    material = Material(
        G = 11.2e3,
        E = 29e3
    )

    print(f"G = {material['G']}, E = {material['E']}")
    # Mmax   = 1.2e3

    element = os.environ.get("Element", "ExactFrame")
    section = os.environ.get("Section", "ShearFiber")

    WarpTypes = os.environ.get("WarpType", "NT,NR").split(",")
    Boundary  = os.environ.get("Boundary", "b,c").split(",")


    Shapes = os.environ.get("Shape", "w,h,c,r").split(",")
    mesh_scale = 1/int(os.environ.get("Mesh", "200"))

    for shape_name in Shapes:
        print(f"Shape {shape_name.upper()}")
        if shape_name == "c":
            shape = Channel(
                        tf=th*depth,
                        tw=th*depth,
                        d=depth,
                        b=depth*0.4,
                        material=material,
                        mesh_type="T6",
                        mesher="gmsh",
                        mesh_scale=1/15 #800
            )
            # shape = shape.translate(-shape._analysis.shear_center())

        elif shape_name == "r":
            shape = Rectangle(d=depth, 
                              b=0.4*depth, 
                              material=material,
                              mesh_scale=1/20, 
                              mesh_type="T6", 
                              mesher="gmsh")

        elif shape_name == "o":
            shape = Circle(depth/2, 
                           divisions=8, 
                           mesh_scale=1/200, 
                           material=material)

        elif shape_name == "w":
            # W21x93
            shape = WideFlange(
                        tf = 0.93,
                        tw = 0.58,
                        d  = 21.62,
                        b  = 8.42,
                        material=material,
                        mesher="gmsh",
                        mesh_type="T6",
                        mesh_scale=1/4
                    )
            # shape = WideFlange(
            #             tf = th*depth,
            #             tw = th*depth,
            #             d  = depth,
            #             b  = width,
            #             mesh_scale=1/10,
            #             mesher="gmsh"
            #         )
        elif shape_name == "h":
            shape = HollowRectangle(
                        tf = th*depth*2,
                        tw = th*depth,
                        d  = depth,
                        b  = width,
                        material=material,
                        mesher="gmsh",
                        mesh_type="T6",
                        mesh_scale=1/8
                    )
        elif shape_name == "h02":
            shape = HollowRectangle(
                        tf = th*depth,
                        tw = th*depth,
                        d  = depth,
                        b  = width,
                        material=material,
                        mesher="gmsh",
                        mesh_scale=1/8#0
                    )
        else:
            raise ValueError("Unknown shape")


        # print(shape.summary())

        sv = SaintVenantSectionAnalysis(shape)

        GJ = sv.twist_rigidity()
        Mmax = GJ/(depth/2)*np.pi*2*1e-5


        for boun in Boundary:

            key = f"{element[:5]}-{section[:5]}-{shape_name}-{boun}"

            for slenderness in [2,1,0.5]:#, 1, 0.5]:

                p1 = PlotTwist2(Mmax, GJ, boun,
                                title=f"Shape {shape_name.upper()}, Case {boun.upper()}, slenderness {slenderness}",
                                skip="Batch" in os.environ)

                for warp_type in WarpTypes:

                    print(f"Shape {shape_name.upper()} Case {boun}, slenderness {slenderness}, warp {warp_type}")
                    p1.reset(label=f"warp = {warp_type}")


                    model = create_cantilever(
                        slenderness,
                        shape,
                        material,
                        boun,
                        ne=8, #16,
                        warp_type=warp_type,
                        nen=3 if element == "ExactFrame" else 2,
                        section = Section(type=section, 
                                          shape=shape,
                                          material=material,
                                          mixed_type=warp_type),
                        element = element)

                    analyze(model, Mmax, element,tol=1e-12)

                    model.reactions()
                    p1.update(model)

                    end = model.getNodeTags()[-1]
                    L = model.nodeCoord(end, 1)
                    shaft = Shaft(boun, L, shape, warp_type=warp_type, sv=sv)
                    # p1.draw(L, shaft, Mmax)
                    try:
                        model.eval(f"verify error [nodeDisp {end} 4] {shaft.twist(L, Mmax):.12f} 1e-3 \"{boun}\"")
                    except:
                        Failed.append(f"{key} slenderness {slenderness} warp {warp_type}")
                        pass
                        # raise

            
                p1.finalize()


    if "Batch" not in os.environ:
        plt.show()

    print("Failed cases:")
    for i,f in enumerate(Failed):
        print(" ", i+1, " ", f)