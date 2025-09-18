from xara.benchmarks import Prism
from xara.helpers import find_node
from xara.units.mks import cm, MPa, N, m, ksi
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


def analyze(model, prism, w):
    divisions = prism.divisions
    model.pattern("Plain", 1, "Linear")

    if "Exact" not in prism.element:
        for i in range(divisions):
            model.eleLoad("-type", "BeamUniform", (0.0, w), 
                          ele=i+1, pattern=1)
    else:
        model.eleLoad("Frame", "Heaviside",
                    basis = "local",
                    force = [0, 0, w],
                    pattern=1,
                    elements=list(range(1, divisions+1))
        )


    steps = 40
    model.system('Umfpack')
    model.integrator("LoadControl", 1/steps)
    model.test("Energy", 1e-14, 20, 1)
    model.algorithm("Newton")
    model.analysis("Static")

    # artist = veux.create_artist(model, vertical=3,
    #                             model_config=dict(extrude_outline=shape))
    # motion = veux.motion.Motion(artist)

    u = [0]
    P = [0]
    for i in range(steps):

        if model.analyze(1) != 0:
            print(f"Failed at time = {model.getTime()}")
            break

        # motion.draw_sections(rotation=model.nodeRotation,
        #                      position=model.nodeDisp)
        # motion.advance(time=model.getTime()*10)

        u.append(model.nodeDisp(find_node(model, x=length/2), 3))
        P.append(model.getTime())

    return u,P

if __name__ == "__main__":
    from xsection.library import Rectangle 

    length = 50*cm
    E = 220e3*MPa
    G = E/(1 + 0.27)/2
    Fy = 300*MPa
    w = 1e4 * N/m # 4.0e4 * N/m

    print(f"{Fy = }")

    shape = Rectangle(d=5*cm, b=10*cm, mesh_scale=1/500)
    I = shape.cmm()[1,1]
    A = shape.cnn()[0,0]

    divisions = 8
    assert divisions % 2 == 0, "Number of divisions must be even"

    uy = Span1(w=w, L=length, E=E, I=I, k=1, A=A, G=G).uy(length/2)
    fig, ax = plt.subplots()
    ax.axhline(0, color='black', linestyle='-', linewidth=1)
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    ax.plot([0,uy], [0,1.0], color='red', linestyle='--', linewidth=1, label="Linear")
    
    element = "ForceFrame"
    for shear in [0,1]:
        prism = Prism(
            length=length,
            element=element,
            shape=shape,
            material = {"E": E, "G": G, 
                        "name": "ElasticIsotropic",
                        #"J2Simplified", 
                        #  "Fy": Fy, 
                        # "Hiso": 0.02*29e3*ksi
                        #, "Fs": Fy, "Hsat": 0
                        },
            vertical = 3,
            boundary = ((1, 1, 1, 1, 0, 0),
                        (0, 1, 1, 1, 0, 0)),
            section="ShearFiber",
            transform="Linear",
            shear=shear,
            order=1 if "Exact" not in element else 3,
            divisions = divisions
        )

        model = prism.create_model()
        u, P = analyze(model, prism, w)
        ax.plot(u, P, ".", label=f"Shear: {bool(shear)}")

    ax.legend()
    plt.show()


    model.reactions()
    print(
        w*length / sum(model.nodeResponse(i, 3, "reactionForce") for i in model.getNodeTags()),
    )
    print(f"{E = }, {G = }")
    # motion.add_to(artist.canvas)
    # veux.serve(artist)
