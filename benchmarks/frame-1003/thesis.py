from xara.benchmarks import Prism
from xara.helpers import find_node
from xara.units.mks import cm, MPa, N, m
import matplotlib.pyplot as plt
from xara.post import PlotConvergenceRate
import veux, veux.motion
try:
    plt.style.use("thesis")
except:
    pass




def analyze(model, prism, w, basis, post=None):
    divisions = prism.divisions

    #
    # Create distributed load
    #
    model.pattern("Plain", 1, "Linear")

    if basis is None:
        for i in range(divisions):
            model.eleLoad("-type", "BeamUniform", (0.0, w), 
                          ele=i+1, pattern=1)
    else:

        model.eleLoad("Frame",
                    "Heaviside",
                    basis = basis,
                    force = [0, 0, w],
                    pattern=1,
                    elements=list(range(1, divisions+1))
        )


    #
    # Solution Strategy
    #
    steps = 40
    model.system('Umfpack')
    model.integrator("LoadControl", 1/steps)
    model.test("Energy", 1e-16, 20, 0)
    model.algorithm("Newton")
    model.analysis("Static")


    u = [0]
    P = [0]
    for i in range(steps):

        if model.analyze(1) != 0:
            print(f"Failed at time = {model.getTime()}")
            raise RuntimeError(f"Analysis failed at step {i+1}")
            break

        u.append(model.nodeDisp(find_node(model, x=length/2), 3))
        P.append(model.getTime()*w)

        if post is not None:
            for p in post:
                p.update(model)
    return u, P


if __name__ == "__main__":
    from xsection.library import Rectangle

    length = 50*cm
    E = 220e3 * MPa
    G = 0.5*E/(1 + 0.27)
    w = 4.0e6 * N/m
    shear = 1

    shape = Rectangle(d=1*cm, b=50*cm)
    I = shape.cmm()[1,1]
    A = shape.cnn()[0,0]


    fig, ax = plt.subplots()
    ax.axhline(0, color='black', linestyle='-', linewidth=1)
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    markers = iter(["s", "^", ".", "+", "x", ".", "^", "v", "<", ">"])

    cr = PlotConvergenceRate()

    n_e = 20
    c = 0
    i = 0
    for basis in ["director", "reference", None]:
        for element in ["ExactFrame", "ForceFrame"]:

            assert n_e % 2 == 0, "Number of divisions must be even"

            if "Exact" in element and basis is None:
                continue

            i += 1

            prism = Prism(
                length=length,
                element=element,
                shape=shape,
                material = {"E": E, "G": G},
                vertical = 3,
                boundary = ((1, 1, 1, 1, 0, 0),
                            (c, 1, 1, 1, 0, 0)),
                section="Elastic",
                transform="Corotational02",
                shear=shear,
                # geometry="delta",
                order=1 if "Exact" not in element else 1,
                divisions = n_e
            )

            model = prism.create_model(echo_file=open(f"x-{i}.tcl", "w"))
            cr.reset(label=f"{element}, basis={basis}")
            u, P = analyze(model, prism, w, basis, post=[cr])

            cr.draw()

            ax.plot(u, P, next(markers), label=fr"$\texttt{{{element}}}$, {basis} load")
            print(element, basis,  u[-1], P[-1])

    cr.finalize()
    cr.savefig("img/1003-convergence.png", dpi=600)

    ax.legend()
    ax.grid("on")
    ax.set_ylabel("$\\lambda$")
    ax.set_xlabel("$u$ [m]")
    ax.set_xlim([0, None])
    ax.set_ylim([0, None])
    fig.savefig("img/1003-bases.png",dpi=600)
    plt.show()


    # motion.add_to(artist.canvas)
    # veux.serve(artist)
