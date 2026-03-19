#
# Tip loaded cantilever beam - Poisson effect
#
import os
from argparse import ArgumentParser
import veux
import xara

from xara.benchmarks import Prism
import xara.units.iks as units
import numpy as np
import matplotlib.pyplot as plt

from xsection._benchmarks import load_shape
from xsection.analysis import SaintVenantSectionAnalysis

from venant import SaintVenant
import xara.units.us as units

def error(a, b):
    if abs(b) < 1e-15:
        return abs(a - b)
    return abs(a - b)/abs(b)


def analyze(model, P, T):
    nn = len(model.getNodeTags())
    n = 1
    model.pattern("Plain", 1, "Linear", load={nn: [0,0,P, T,0,0]})
    model.integrator("LoadControl", 1/n)
    model.system("BandGen")
    model.analysis("Static")
    model.test("Energy", 1e-16, 10, 1)

    assert model.analyze(n) == 0


def run_trace(options):

    # element = os.environ.get("Element", "ForceFrame")
    element = options.element
    case = options.shape
    try:
        case = int(case)
    except:
        pass

    NIP = 5
    P =  0.18159
    T  = 0.1 # 0
    if "Exact" in element:
        T /= 10 
        P /= 10
        NIP = 2

    E  = 2.9
    nu = options.poisson 
    G = E/(2*(1+nu))
    material = xara.Material(E=E, G=G)

    print(f"Shape {case}")
    shape = load_shape(case, material=material, units=units, mesh_type="T6")

    # G = E/(2*(1+nu))
    print(f"{nu = }")


    # shape = shape.translate(-shape.centroid)
    shape = shape.translate(-shape._analysis.shear_center())
    if options.rotate:
        shape = shape.rotate(-np.pi/8)
    # shape = shape.rotate(np.pi/8)


    sv = SaintVenantSectionAnalysis(shape)
    print(sv.summary(format="texsection"))

    # veux.serve(veux.render(shape.model))


    EI = E*shape.cmm()[1,1]


    L = shape.d*options.length # 1.5
    soln = SaintVenant(shape, length=L, sv=sv, material={"E": E, "G": G}, V=[0.0, P], T=-T)

    fig, ax = plt.subplots()

    for trace_name in ["energetic", "geometric"]: # 
        trace = sv.create_trace(form=trace_name)
        print(f"Trace: {trace_name}")

        # Kp = trace.iesan_matrix()
        # Cp = trace._energy_matrix()
        # print(df(np.linalg.solve(Cp, Kp.T)))

        # print(df(trace.trace_matrix()))
        # Cse = trace.cse(E, G)
        # print("Ks: ")
        # print(df(Cse))
        # print("Trace: ")
        # e = np.linalg.solve(Cse, [0, 0, P, T, 0., 0.])
        # print(e)


        u_iesan = np.array(soln.u(L, trace=trace))
        prism = Prism(shape=shape,
                      length=L,
                      boundary=((1,1,1,  1,1,1),
                                (0,0,0,  0,0,0)),
                      material=material,#{"type": "ElasticIsotropic", "E": E, "G": G},
                      element=element,
                      section=xara.Section("MixedFiber", shape, material, mixed_type=trace_name),#create_section(trace),
                      shear=1,
                      vertical=3,
                      integration={"points": NIP, "type": "Legendre"},
                      divisions=int(os.getenv("ne", 1)),
                      order=1 if "shear" not in element.lower() else 2
                )


        model = prism.create_model(options={"iter": (100, 1e-16)})

        analyze(model, P, T)
        ifib = 3
        r = sum(shape.model.nodes[shape.model.elems[ifib].nodes])/3
        ie = 1
        smap = np.array([0, 4, 5, 1, 2, 3])
        # print(df(model.state.element(1).section(NIP).tangent()[np.ix_(smap,smap)]))

        # Ks = model.state.element(1).section(NIP).tangent(expand=True)
        # print(df(Ks))
        print(model.state.element(1).section(NIP).stress())
        print(model.state.element(1).section(NIP).strain())

        print()
        ax.plot([model.nodeCoord(n)[0]/L for n in model.getNodeTags()],
                [model.state.u(node, 3) for node in model.getNodeTags()],
                color='blue',  linestyle='--',
                label=f"FEM ({trace_name})"
        )
        trace_soln = trace.solve(soln.p)
        X = np.linspace(0, L, 100)
        ax.plot(X/L, 
                [trace_soln.position(x)[2] for x in X],
                color='gray', linestyle='-',
                label="Reference"
        )

        end = len(model.getNodeTags())
        uz  = model.state.u(end, 3)
        u_euler = P*L**3/(3*EI)
        u_shear = uz - u_euler

        # print(f"Uz = {uz:.8f}, Uz theory = {u_iesan[2]:.8f} ({u_euler:.6f} + {u_shear:.6f})")
        # u_end = model.state.u(end)
        # print("FEA: ", u_end)
        # print("Trace: ", trace.solve(soln.p).position(L))
        # print(".      ", trace.solve(soln.p).rotation(L))

        # print(error(u_end[1], u_iesan[1]))
        # print(error(u_end[2], u_iesan[2]))
        # print(error(u_end[3], trace.solve(soln.p).rotation(L)[0]))
        try:
            model.eval(f"verify error [nodeDisp {end} 3] {u_iesan[2]:.18f} 2e-3")
        except:
            pass
        try:
            model.eval(f"verify error [nodeDisp {end} 2] {u_iesan[1]:.18f} 2e-3")
        except:
            pass
        try:
            model.eval(f"verify error [nodeDisp {end} 4] {trace.solve(soln.p).rotation(L)[0]:.12f} 1e-2")
        except:
            pass

    # plot.finalize()
    plt.show()
    # import sys
    # sys.exit()
    return

    soln.render(trace=trace)
    artist = veux.create_artist(model, vertical=3, model_config={
        "frame_shape": shape
    })
    artist.draw_sections(state=model.nodeDisp)
#       artist.draw_surfaces()
    # artist.draw_outlines()#state = lambda _: 1)
    # stress = FiberStress(model, shape, section=1, stress="sxz", element=1)
    # artist.draw_surfaces(
    #     field=stress,
    #     state=stress,
    #     scale=1/max(stress(n) for n in range(len(shape.model.nodes)))
    # )
    veux.serve(artist)

       #a = veux.create_artist(model)
       #a.draw_sections()
       #veux.serve(a)



if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-e", "--element", default="ForceFrame",    help="Element type")
    parser.add_argument("-s", "--shape",   type=str,   default="2",  help="Shape case")
    parser.add_argument("-n", "--number",  type=int,   default=1,    help="Number of elements")
    parser.add_argument("-v", "--poisson", type=float, default=-0.5, help="Poisson ratio")
    parser.add_argument("-r", "--rotate",  default=False,  help="Rotate", action="store_true")
    options = parser.parse_args()

    run_trace(options)
