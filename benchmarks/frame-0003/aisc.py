# AISC Benchmark Problem, Case 1
#
# AISC 360-16, Commentary Figure C-C2.2
#
# Pinned-pinned column with uniform lateral load of 0.200 kip/ft and varying axial load
#

from xara.benchmarks import Prism
from xara.helpers import find_node
from xara.units.iks import cm, MPa, N, m, ft, inch, kip, ksi
from xara.units import iks as units
from xsection.library import from_aisc, aisc_data
import matplotlib.pyplot as plt
import veux, veux.motion


class Span15:
    # Encastred beam with distributed load
    def __init__(self, w, L, E, I, k=1, A=0, G=0):
        self.w = w
        self.L = L
        self.E = E
        self.I = I
        self.k = k

        self.uy = lambda x: \
            w*x**2/(24*E*I)*(L - x)**2 - \
                ((w/(k*G*A)*L**2/24*(1 - 12*x/L + 12*(x/L)**2) + w*L**2/(24*G*A*k)) if G and A else 0)


class Span1:
    # Simple span with distributed load
    def __init__(self, w, L, E, I, k=1, A=0, G=0):
        self.k = k
        self.A = A
        self.G = G
        self.w = w
        self.L = L
        self.E = E
        self.I = I

    def uy(self, x):
        L = self.L
        E = self.E
        I = self.I
        w = self.w
        k = self.k
        G = self.G
        A = self.A
        xi = x/L
        return w/(24*E*I)*(L**3*x - 2*L*x**3 + x**4) \
           + (
               w*L**2/(2*k*G*A)*(xi - xi**2) if G*A else 0
           )



def analyze(model, prism, w, basis):
    divisions = prism.divisions
    model.pattern("Plain", 1, "Constant")

    if basis is None:
        for i in range(divisions):
            model.eleLoad("-type", "BeamUniform", (0.0, w), 
                          ele=i+1, pattern=1)
    
    else:
        model.eleLoad("Frame", "Heaviside",
                    basis = basis,
                    force = [0, 0, w],
                    pattern=1,
                    elements=list(range(1, divisions+1))
        )



    model.system('Umfpack')
    model.test("Energy", 1e-18, 10, 2)
    model.algorithm("Newton")
    model.analysis("Static")
    model.analyze(1)
    model.loadConst(time=0)


    u = [model.nodeDisp(find_node(model, x=length/2), 3)]
    P = [0]
    steps = 3
    model.pattern("Plain", 2, "Linear", loads={
        find_node(model, x=prism.length): [-1, 0, 0, 0, 0, 0]
    })

    model.integrator("LoadControl", 450/steps)
    for i in range(steps):

        if model.analyze(1) != 0:
            print(f"Failed at time = {model.getTime()}")
            raise RuntimeError(f"Analysis failed at step {i+1}")
            break

        u.append(model.nodeDisp(find_node(model, x=length/2), 3))
        P.append(model.getTime())

    return u, P


if __name__ == "__main__":

    length = 28*ft
    E = 29e3 * ksi
    w = 0.2*kip/ft

    # shape = from_aisc("W14x48", mesh_scale=1/20)
    shape_data = aisc_data("W14x48", units=units)
    shape = {
        "Iy": shape_data["Ix"],
        "Iz": shape_data["Iy"],
        "A":  shape_data["A"],
        "Az": shape_data["d"]*shape_data["tw"],
        "Ay": shape_data["bf"]*shape_data["tf"],
        "J":  shape_data["J"],
        "Cw": shape_data["Cw"],
    }

    # I = shape.cmm()[1,1]
    # A = shape.cnn()[0,0]
    # print(f"A = {A/inch**2:.3f} in^2, I = {I/inch**4:.3f} in^4")


    # uy = Span1(w=w, L=length, E=E, I=I, k=1, A=A, G=G*shear).uy(length/2)
    # fig, ax = plt.subplots()
    # ax.axhline(0, color='black', linestyle='-', linewidth=1)
    # ax.axvline(0, color='black', linestyle='-', linewidth=1)
    # ax.plot([0,uy], [0,1.0], color='red', linestyle='--', linewidth=1, label="Linear")
    # markers = iter(["s", "^", "v", "o", "+", "x", ".", "^", "<", ">"])


    basis = "global"
    for shear in [0,1]:
        for (element, n_e) in [("ExactFrame",   2),
                               ("ForceFrame",   2),
                            #    ("ExactFrame",  40),
                               ("ForceFrame",  10),
                               ("ForceFrame",  40)]:

            assert n_e % 2 == 0, "Number of divisions must be even"

            print(f"{element} shear={shear} n_e={n_e}")
            if shear:
                G = 11200.0*ksi
            else:
                G = 11200.0*ksi*1e6  # Penalty

            # if "Exact" in element and not shear:
            #     continue 

            prism = Prism(
                length=length,
                element=element,
                shape=shape,
                material = {"E": E, "G": G},
                vertical = 3,
                boundary = ((1, 1, 1, 1, 0, 0),
                            (0, 1, 1, 1, 0, 0)),
                section="Elastic",
                transform="Corotational02",
                shear=shear if "Exact" not in element else 1,
                order=1 if "Exact" not in element else 3,
                divisions = n_e
            )

            model = prism.create_model(echo_file=open(f"x-{element[:5]}-{n_e}-{shear}.tcl", "w"))
            u, P = analyze(model, prism, w, basis)

            print(u)
            print(P)

        print()
