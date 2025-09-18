
from shps.rotor import exp
import os
import numpy as np
import veux
import xara

class Prism:
    def __init__(self,
                 length:    float,
                 element:   str,
                 section:   dict,
                 boundary:  tuple,
                 geometry:  str = None,
                 transform: str = None,
                 divisions: int = 1,
                 rotation = None,
                 shear = True):

        self.length    = length
        self.element   = element
        self.section   = section
        self.boundary  = boundary
        self.geometry  = geometry
        self.transform = transform
        self.divisions = divisions
        self.use_shear = shear
        self.rotation = rotation

    def create_model(self, file=None):

        L  = self.length
        boundary = self.boundary

        # Number of elements discretizing the column
        ne = self.divisions

        elem_type  = self.element
        geom_type  = self.transform

        # Number of integration points along each element
        nIP = 5
        nn = ne + 1
        if file is not None:
            file = open(file, "w+")

        model = xara.Model(ndm=3, ndf=6, echo_file=file)

        for i in range(1, nn+1):
            x = (i-1)/float(ne)*L
            location = (x, 0.0, 0.0)

            if self.rotation is not None:
                location = tuple(self.rotation@location)

            model.node(i, location)

            model.mass(i, *[1.0]*model.getNDF())


        # Define boundary conditions
        model.fix(1, boundary[0])

        model.fix(nn, boundary[1])

        #
        # Define cross-section 
        #
        sec_tag = 1
        properties = []
        for k,v in self.section.items():
            properties.append("-" + k)
            properties.append(v)

        model.section("ElasticFrame", sec_tag, *properties)
        # model.section("Elastic", sec_tag,
        #               self.section["E"],
        #               self.section["A"],
        #               self.section["Iz"],
        #               self.section["Iy"],
        #               self.section["G"],
        #               self.section["J"]
        # )

        # Define geometric transformation
        geo_tag = 1
        vector = (0,  0, 1)
#       vector = (0,  -1, 0)
        if self.rotation is not None:
            vector = tuple(map(float, self.rotation@vector))

        model.geomTransf(geom_type, geo_tag, *vector)

        # Define elements
        for i in range(1, ne+1):
            if self.geometry is None or self.geometry == "Linear" or "Exact" in elem_type:
                model.element(elem_type, i, (i, i+1),
                            section=sec_tag,
                            transform=geo_tag,
#                           iter=(2, 1e-12),
                            shear=int(self.use_shear))
            else:
                model.element(elem_type, i, (i, i+1),
                            section=sec_tag,
                            order={"Linear": 0, "delta": 1}[self.geometry],
                            transform=geo_tag,
                            shear=int(self.use_shear))

        return model


if __name__ == "__main__":

    ne = 20
    E  = 71_240
    G  = 27_190
    I  = 0.0833
    A  = 10.0
    prism = Prism(
        length = 240.,
        element = os.environ.get("Element", "ForceFrame"),
        section = dict(
            E   = E,
            G   = G,
            A   = A,
            J   = 2.16,
            Iy  = I,
            Iz  = I,
            Ay  = A,
            Az  = A),
        shear=True,
        # geometry="delta",
        boundary = ((1,1,1, 1,1,1),
                    (0,1,1, 0,1,1)),
        transform = os.environ.get("Transform", "Corotational02"),
        divisions = ne,
        rotation = exp([0,  0.00, 0.001])
    )

    model = prism.create_model()
#   model.fix(ne+1, (0, 1, 1, 0, 1, 1))


    #
    #
    #
    scale = 5 #0.0
    steps = 65
    Tref = 2*E*I/prism.length
    model.test("EnergyIncr", 1e-9, 1000, 1)
#   model.test("NormDispIncr", 1e-8, 50, 1)
#   model.test("RelativeNormDispIncr", 1e-6, 50, 1)

    # model.pattern("Plain", 2, "Linear", load={
    #     ne+1: [-1, 0, 0, 0, 0, 0]
    # })
    # model.integrator("LoadControl", 10)
    # model.analysis("Static")
    # model.analyze(1)
    # model.loadConst(time=0)

    f = [0, 0, 0] + list(map(float, prism.rotation@[Tref, 0, 0]))

    model.pattern("Plain", 1, "Linear", load={
        ne+1: f
    })
    # model.integrator("MinUnbalDispNorm", scale/300, 5, scale/steps/300, scale/200, det=True)
#   model.integrator("MinUnbalDispNorm", 1, 5,  1/steps/500, 1)
#   model.integrator("DisplacementControl", ne+1, 4, 1e-2, 5, 1e-4, 1e-1)
#   input()
    model.integrator("ArcLength", 0.5, exp=0.8, j=5, reference="point") #, 5,  scale/steps/1000, scale/100) #scale/steps)

    model.system("Umfpack", det=True)
    model.analysis("Static")

    artist = veux.create_artist(model)
    artist.draw_axes()
    artist.draw_outlines()

    u = []
    lam = []
    time = []

    iters = []

    for i in range(1000):
        u.append(model.nodeDisp(ne+1, 4)/np.pi)
        time.append(model.getTime())
        lam.append(model.getLoadFactor(1))

        if model.analyze(1) != 0:
            break
            raise RuntimeError(f"Failed at step {i}")
#           model.test("EnergyIncr", 1e-6, 200, 1)
        iters.append(model.numIter())

    print(sum(iters)/len(iters))

#       artist.draw_outlines(state=model.nodeDisp)
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot(u, lam, '-')
    ax.plot(u, time, '.', markersize=1)

    fig, ax = plt.subplots()
    ax.plot(lam,'.')
    plt.show()

#   veux.serve(artist)


