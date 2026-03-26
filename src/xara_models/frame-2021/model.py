import os 
import sys
from xml.parsers.expat import model
import xara
import numpy as np


verbose = False
if verbose:
    progress = lambda x: x
else:
    from tqdm import tqdm as progress
    # progress = lambda x: x


def create_cantilever(aspect,
                      shape,
                      material,
                      case="a",
                      ne=10,
                      nen=2,
                      warp_type=None,
                      element="ExactFrame",
                      section="Elastic"):

    E = material["E"]
    G = material["G"]
    v = 0.5*E/G - 1

    L   = shape.d*aspect
    nn = ne*(nen-1)+1

    model = xara.Model(ndm=3, ndf=7)

    model.eval(f"set E {E}")
    model.eval(f"set G {G}")
    model.eval(f"set L {L}")

    model.material(material, 1)
    model.section(section, 1)


    transform = os.environ.get("Transform", "Linear")
    model.geomTransf(transform, 1, (0,0,1))


    for i,x in enumerate(np.linspace(0, L, nn)):
        model.node(i, (x,0,0))

    for i in range(ne):
        start = i * (nen - 1)
        nodes = list(range(start, start + nen))
        if "Force" in element:
            model.element(element, i+1, 
                          nodes, 
                          section=1, 
                          transform=1, 
                          shear=1,
                          gauss_type="Legendre",
                          n=5#8
            )
        else:
            model.element(element, i+1, nodes, section=1, transform=1, shear=1)

    wi = int(case in "cb")
    wj = int(case in "c")

    model.fix(0,     (1,1,1,  1,1,1, wi))
    model.fix(nn-1,  (0,0,0,  0,0,0, wj))
    return model



def analyze(model: xara.Model, Mmax,  tol=1e-16):
    # Apply torsional moment
    nsteps =  100
    end = model.getNodeTags()[-1]
    model.pattern("Plain", 1, "Linear")
    model.load(end, (0,0,0,  1,0,0,  0), pattern=1)

    model.system('BandGeneral')
    model.numberer("RCM")
    model.integrator("LoadControl", Mmax/nsteps,
                     iter=5,
                     min_step=Mmax/nsteps/20, 
                     max_step=Mmax/nsteps
    )

    if False: # "Force" in element:
        model.test("Residual", 1e-9, 1,0)
    else:
        model.test("Energy", tol, 10,0)
    # model.algorithm("KrylovNewton")
    model.analysis("Static")

    u, T = [], []
    failures = 0
    # while model.getTime() < Mmax:
    while model.state.u(end, 4) < 0.15:
        if model.analyze(1) != 0:
            raise RuntimeError(f"Failed at time = {model.state.time}")
            print(f"Failed at time = {model.getTime()}")
            break
        # print(model.getTime()/Mmax)
        u.append(model.nodeDisp(end, 4))
        T.append(model.state.time)
    return u, T
