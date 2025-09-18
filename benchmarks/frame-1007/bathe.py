#
# Bathe's curved cantilever analysis with Crisfield-Jelenic load paths
#
import os
import xara
import numpy as np


def Bathe(Path, R,
          element: str,
          transform: str):
    model = xara.Model(ndm=3, ndf=6)

    # Element and Material Properties
    nen   = 2         # nodes per element
    ne    = 8         # total number of elements
    E     = 1e3
    A     = 1e4
    G     = 5e2
    I_val = A / 12
    J_val = 2*I_val #1e5 / (12 * 5)

    # Compute load vector P = R * [0; 600; 0] (since ExpSO3([0,0,0]) is identity)
    P = R@[0, 600, 0]

    tol = 1e-4

    # Define load steps based on Path
    if Path == 1:
        steps = [1/3] * 3
    elif Path == 2:
        # Simo
        steps = [0.5, 0.25, 0.25]
    elif Path == 3:
        steps = [1/10] * 10
    elif Path == 4:
        steps = [1/6] * 6
    elif Path == 5:
        steps = [1/8] * 8
    elif Path == 6:
        steps = [0.5, 0.25, 0.125, 0.0625, 0.0625]
    else:
        steps = [1.0]


    # --- Store element property data ---
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
    rad = 100.0
    for i,arc in enumerate(np.linspace(0, np.pi/4, nn)):
        # Coordinates along the circular arc:
        x_local = rad * np.sin(arc)
        y_local = 0.0
        z_local = rad * (1 - np.cos(arc))
        # Rotate local coordinate into global system:
        coord = R.T@[x_local, y_local, z_local]
        model.node(i+1, tuple(coord))

    # Boundary Conditions
    # Fix the first node (all 6 DOFs)
    model.fix(1, (1, 1, 1, 1, 1, 1))

    #
    # Elements
    #
    model.geomTransf(transform, 1,  tuple(R@[0, 0, 1]))
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
    load = [P[0], P[1], P[2], 0, 0, 0]
    model.pattern("Plain", 1, "Linear", load={nn: load})

    # Set Up the Analysis
    model.system("BandGeneral")
    model.numberer("RCM")
    model.constraints("Plain")
    model.integrator("LoadControl", steps[0])
    model.algorithm("Newton")
    model.test("NormUnbalance", tol, 100, 0)
#   model.test("RelativeNormDispIncr", tol, 20)
    model.analysis("Static")

    #
    # Multi-Step Incremental Analysis
    #
    converged = True
    step_results = []
    iterations = 0
    for i,dlam in enumerate(steps):
        model.integrator("LoadControl", dlam)
        ret = model.analyze(1)
        if ret != 0:
            converged = False
            print(f"Step with dLambda={dlam} did not converge.")
            break
        # Save displacement at the last node:
        disp = model.nodeDisp(nn)
        step_results.append(disp)
        iterations += (model.numIter() - iterations)/(i+1)

    # Collect results and return
    return model, {
         "converged": converged,
         "final_disp": model.nodeDisp(nn),
         "step_results": step_results,
         "load_steps": steps,
         "iterations": iterations
    }


def print_row(model, result, R, relative=False):
    if not result["converged"]:
        print(f" {len(result['step_results'])}")
    else:
        disp = result["final_disp"]
        if not relative:
            disp[0] += 70.71
            disp[2] += 29.29
        itrs = result["iterations"]
        # Print first three displacement components:
        print(f"{disp[0]:14.6f} {disp[1]:14.6f} {disp[2]:14.6f} {itrs}")

#
# Main Script
#

def main():
    # Global rotation matrix
    R = np.eye(3)
    config = {
            "element":   os.environ.get("Element",   "ExactFrame"),
            "transform": os.environ.get("Transform", "Corotational")
    }

    for path in [3, 5, 2]:
        print_row(*Bathe(path, R, **config), R)


if __name__ == "__main__":
    main()

