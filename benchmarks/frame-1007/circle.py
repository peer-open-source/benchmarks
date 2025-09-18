#
# Bathe's curved cantilever analysis with Crisfield-Jelenic load paths
#
import os
import xara
import numpy as np
from shps.rotor import exp as ExpSO3


def Bathe(R,
          element: str,
          transform: str,
          ne: int = 8,
          arc: float = np.pi/4
    ):
    model = xara.Model(ndm=3, ndf=6)

    # Element and Material Properties
    nen   = 2         # nodes per element

    E     = 1e3
    A     = 1e4
    G     = 5e2
    I_val = A / 12
    J_val = 2*I_val #1e5 / (12 * 5)


    # Material and section
    section = {
         "E": E,
         "A": A,
         "Ay": A,
         "Az": A,
         "Iz": I_val,
         "Iy": I_val,
         "G": G,
         "J": J_val,
    }


    #
    # Model Generation
    #
    # Total number of nodes
    nn = ne * (nen - 1) + 1
    rad = 200000.0
    for i,arc in enumerate(np.linspace(0, arc, nn)):
        # Coordinates along the circular arc:
        x_local = rad * np.sin(arc)
        y_local = 0.0
        z_local = rad * (1.0 - np.cos(arc))
        # Rotate local coordinate into global system:
        coord = R.T@[x_local, y_local, z_local]
        model.node(i+1, tuple(coord))

    # Boundary Conditions
    # Fix the first node (all 6 DOFs)
    model.fix(1, (1, 1, 1, 1, 1, 1))

    #
    # Elements
    #
    model.geomTransf(transform, 1,  tuple(R@[0, 1, 1]))
    model.section("ElasticFrame", 1, **section)

    # Create Elements
    for i in range(ne):
        n1 = i * (nen - 1) + 1
        n2 = n1 + 1
        tag = i + 1
        model.element(
            element, tag, (n1, n2), section=1, transform=1 #, shear=int("xact" in element)
        )

    # Define the Loading
    load = [0,0,0, 0, 0, 0]
    model.pattern("Plain", 1, "Linear", load={nn: load})

    # Set Up the Analysis
    tol = 1e-13
    model.system("Umfpack")
    model.numberer("RCM")
    model.constraints("Plain")
    model.integrator("LoadControl", 1.0)
    model.algorithm("Newton")
    model.test("NormUnbalance", tol, 50, 0)
    model.analysis("Static")

    #
    # Multi-Step Incremental Analysis
    #
    model.analyze(1)

    return model


#
# Main Script
#

def main():
    # Global rotation matrix
    R = ExpSO3([-0.0, -0.1, 0.0])
    config = {
        "element":   os.environ.get("Element",   "ForceFrame"),
        "transform": os.environ.get("Transform", "Corotational")
    }
    ne = 3
    for arc in np.pi/2, : # np.linspace(np.pi/4, np.pi/2, 5):
        print(arc)
        # Ensure the arc is a float
        arc = float(arc)
        model = Bathe(R, config["element"], config["transform"], ne=ne, arc=float(arc))
        for i in range(1, ne + 2):
            node = model.nodeDisp(i)
            print(f"  Node {i}: {np.linalg.norm(node)}, {node}")


if __name__ == "__main__":
    main()

