from xara.benchmarks import Prism
from xara.helpers import find_node
from xara.units.mks import cm, MPa, N, m
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
            model.eleLoad("-type", "BeamUniform", (w, 0.0),
                          ele=i+1, pattern=1)
    else:
        model.eleLoad("Frame", "Heaviside",
                    basis = "local",
                    force = [0, w, w],
                    pattern=1,
                    elements=list(range(1, divisions+1))
        )


    steps = 20
    model.system('Umfpack')
    model.integrator("LoadControl", 1/steps)
    model.test("Energy", 1e-14, 10, 1)
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
            raise RuntimeError(f"Analysis failed at step {i+1}")
            break

        # motion.draw_sections(rotation=model.nodeRotation,
        #                      position=model.nodeDisp)
        # motion.advance(time=model.getTime()*10)

        u.append(model.nodeDisp(find_node(model, x=length/2), 2))
        P.append(model.getTime())

    return u, P

if __name__ == "__main__":
    from xsection.library import Rectangle 

    length = 50*cm
    E = 220e3 * MPa
    G = 0.5*E/(1 + 0.27)
    w = 1.0e3 * N/m
    shear = 1

    shape = Rectangle(d=50*cm, b=50*cm) #, mesh_scale=1/1000)
    # print(shape.summary())

    I = shape.cmm()[1,1]
    A = shape.cnn()[0,0]

    divisions = 2
    assert divisions % 2 == 0, "Number of divisions must be even"


    uy = Span1(w=w, L=length, E=E, I=I, k=1, A=A, G=G*shear).uy(length/2)
    fig, ax = plt.subplots()
    ax.axhline(0, color='black', linestyle='-', linewidth=1)
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    ax.plot([0,uy], [0,1.0], color='red', linestyle='--', linewidth=1, label="Linear")

    markers = iter([".", "x", "o", "s", "^", "v", "<", ">"])

    for element in ["ExactFrame", "ForceFrame"]:
        print(f"Element: {element}")
        marker = next(markers)
        prism = Prism(
            length=length,
            element=element,
            shape=shape,
            material = {"E": E, "G": G},
            vertical = 3,
            boundary = ((1, 1, 1, 1, 0, 0),
                        (0, 1, 1, 1, 0, 0)),
            section="Elastic", #"ShearFiber", #ElasticFrame",
            transform="Corotational02",
            shear=shear,
            order=1 if "Exact" not in element else 3,
            divisions = divisions
        )

        u, P = analyze(prism.create_model(), prism, w)
        ax.plot(u, P, marker, label=f"{element}")


    ax.legend()
    plt.show()

    # model.reactions()
    # print(
    #     w*length / sum(model.nodeResponse(i, 3, "reactionForce") for i in model.getNodeTags()),
    # )

    # motion.add_to(artist.canvas)
    # veux.serve(artist)
