# Test of the warping DOF
#
# Linear 7-DOF analysis of a cantilever subjected to a torque
#
import os
import sys
import veux
from pathlib import Path
from veux.motion import Motion
from xsection.analysis import SaintVenantSectionAnalysis
from xsection._benchmarks import load_shape
from xsection.library import WideFlange, HollowRectangle, Channel, Rectangle, Circle

import xara
from xara import Section, Material
from xara.post import FiberStress, NodalAverage

# External libraries
import numpy as np
import thesis as plt


from post import (
    PlotTwist2, 
)
from model import create_cantilever, analyze


class Cases:
    def __init__(self, cases):
        self._cases = cases
        tag = 1
        for case in self._cases:
            case["tag"] = tag
            tag += 1

    def code(self, case):
        return f"C{case['tag']}"

def plot_linear(ax, GJ, Mmax, L):
    T = [0, Mmax]
    u = [0, Mmax*L/GJ]
    ax.plot(u, T, label="Linear")


def plot_solid(ax, s, shape_name="H05"):
    # u,T = np.loadtxt("out/solid_2_b.txt", skiprows=1, unpack=True)
    # ax.plot(u, T, marker="o", markersize=3, label="Solid b")
    for file in Path("out").glob(f"solid_{shape_name}_{int(s)}*.txt"):
        try:
            u,T = np.loadtxt(file, skiprows=1, unpack=True)
        except:
            continue
        ax.plot(u[::10], T[::10], marker="2", markersize=3, label=f"{file.name}")

if __name__ == "__main__":

    cases = Cases([
        dict(element="ExactFrame", section="MixedFiber", shape="h", boundary="b", mixed_type="NR"),
        dict(element="ExactFrame", section="MixedFiber", shape="h", boundary="c", mixed_type="NR"),
        dict(element="ExactFrame", section="MixedFiber", shape="h", boundary="b", mixed_type="NT"),
        dict(element="ExactFrame", section="MixedFiber", shape="h", boundary="c", mixed_type="NT"),
    ])

    # Mmax   = 1.2e3
    shape_name = "H03"
    slenderness = 1.4 #2 # 2
    if len(sys.argv) > 1:
        shape_name = sys.argv[1]
    if len(sys.argv) > 2:
        slenderness = float(sys.argv[2])
    element = os.environ.get("Element", "ExactFrame")
    section = os.environ.get("Section", "MixedFiber")

    WarpTypes = os.environ.get("WarpType", "NT,NR").split(",")
    Boundary  = os.environ.get("Boundary", "b,c").split(",")


    material = xara.Material(
        "J2BeamThread", #"NonlinearJ2", #"J2Simplified",
        E=29e3, 
        nu=0.27,
        Fy=60,
        Fsat=60,
        Hiso=0.03*29e3,
        tol=1e-16
    )

    print(f"Shape {shape_name.upper()}")
    shape = load_shape(shape_name, mesher="gmsh", material=material, mesh_type="T6")
    shape = shape.translate(-shape._analysis.shear_center())

    depth = shape.d

    # a_sec = veux.draw_shape(shape, origin=True)
    # veux.serve(a_sec)

    sv = SaintVenantSectionAnalysis(shape)
    print(sv.summary(format="texsection"))

    GJ = sv.twist_rigidity()
    Mmax = GJ/(depth/2)*np.pi*2*1e-3
    fig, ax = plt.subplots()

    plot_solid(ax, s=slenderness, shape_name=shape_name)



    for boun in Boundary:


        # plot_linear(ax, GJ, Mmax, depth*slenderness)
        p1 = PlotTwist2(Mmax, GJ, boun,
                        title=f"Shape {shape_name.upper()}, Case {boun.upper()}, slenderness {slenderness}",
                        skip="Batch" in os.environ)

        for warp_type in WarpTypes:

            key = f"{element[:5]}-{shape_name}-{int(slenderness)}-{boun}-{warp_type}"
            print(f"Shape {shape_name.upper()} Case {boun}, slenderness {slenderness}, warp {warp_type}")
            p1.reset(label=f"warp = {warp_type}")


            model = create_cantilever(
                slenderness,
                shape,
                material,
                boun,
                ne=4, #16,
                warp_type=warp_type,
                nen=3 if element == "ExactFrame" else 2,
                section = Section(type=section, 
                                    shape=shape,
                                    material=material,
                                    mixed_type=warp_type),
                element = element)
            
            model.print(json=f"out/{key}.json")

            u,T = analyze(model, Mmax,tol=1e-12)
            ax.plot(u, T, label=f"{boun} {warp_type}")

            np.savetxt(f"out/{key}.txt", np.array([T,u]).T, header="T u", comments="")

            model.reactions()
            p1.update(model)

        
            p1.finalize()


    
            artist = veux.ShapeArtist(shape, 
                                      title=f"Case {key}",)
            artist.draw_surfaces(
                field=FiberStress(model, shape, section=1, stress="sxx", element=1),
                cbar_label="Von Mises Stress (ksi)",
            )
            artist.save(f"img/C{key}_stress.pgf", backend="pgf")

    fig.legend()


    if "Batch" not in os.environ:
        plt.show()
