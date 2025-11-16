#
# Simply supported beam with concentrated load at mid-span
#
from xara.benchmarks import Prism
from xara.helpers import find_node
from xara.units.mks import cm, MPa, N, m
from xsection.library import Rectangle



def analyze(model, a, P):
    model.pattern("Plain", 1, "Linear")

    model.eleLoad("Frame",
                  "Point",
                   basis = "local",
                   offset=[a,0,0],
                   force = [0, -P, -P],
                   pattern=1,
                   elements=1
    )

    steps = 2
    model.system('Umfpack')
    model.integrator("LoadControl", 1/steps)
    model.test("Energy", 1e-20, 10, 1)
    model.algorithm("Newton")
    model.analysis("Static")

    for i in range(steps):
        if model.analyze(1) != 0:
            print(f"Failed at time = {model.getTime()}")
            raise RuntimeError(f"Analysis failed at step {i+1}")
            break


if __name__ == "__main__":

    length = 100*cm
    L = length
    E = 220e3 * MPa
    G = 0.5*E/(1 + 0.27)*100
    w = 1.0e4 * N/m
    shear = 1

    shape = Rectangle(d=10*cm, b=10*cm, mesh_scale=1/400)

    I = float(shape.cmm()[1,1])
    A = float(shape.cnn()[0,0])


    n_e = 1
    for element in ["ExactFrame", "ForceFrame"]:
        for a in [0.5, 0.75]:
            P =  w*length/2
            prism = Prism(
                length=length,
                element=element,
                shape=shape,
                material = {"E": E, "G": G},
                vertical = 3,
                boundary = ((1, 1, 1, 1, 0, 0),
                            (0, 1, 1, 0, 0, 0)),
                section="ElasticFrame",
                transform="Linear",
                shear=shear,
                order=1 if "Exact" not in element else 3,
                divisions = n_e
            )

            model = prism.create_model()
            analyze(model, a, P)

            b = (1-a)
            theta_i = P*a*L*b*L*(L + b*L)/(6*E*I*L)
            theta_j =-P*b*L*a*L*(L + a*L)/(6*E*I*L)
            print(f"{theta_i = }, {theta_j = }")
            theta_i = model.nodeDisp(1,5)
            theta_j = model.nodeDisp(2,5)
            print(f"{theta_i = }, {theta_j = }")
            theta_i = model.nodeDisp(1,6)
            theta_j = model.nodeDisp(2,6)
            print(f"{theta_i = }, {theta_j = }")
