import numpy as np
import sys
from xara.helpers import Prism

if __name__ == "__main__":
    import sys

    A = 112.0
    ne = int(sys.argv[2])
    prism = Prism(
        length = 60.0,
        element = sys.argv[1],
        section = dict(
            E  = 29000.0,
            G =  11200.0,
            A  = A,
            J  = 220.0,
            Iy = 110.0,
            Iz = 110.0,
            Ay = 3/6*A,
            Az = 3/6*A),
        boundary  = ("fix", "free"),
        geometry  = "Linear",
        transform = "Corotational",
        divisions = ne
    )

    model = prism.create()

    model.pattern("Plain", 1, "Linear", load={ne+1: [1, 0, 0, *[0]*3]})
    model.integrator("LoadControl", 500)
    model.analysis("Static")
    model.analyze(1)

    print(model.nodeDisp(2))


