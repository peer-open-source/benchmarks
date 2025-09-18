# Test of the Wagner strain term.
# Battini et al. (2002a), Example 7.4
#
import veux
from shps.shapes import Rectangle
import opensees.openseespy as ops
import matplotlib.pyplot as plt
try:
    pass
    plt.style.use("veux-web")
except:
    pass


def create_cantilever(shape, element, section):


    E = 2.1e6 # MPa
    v = 0.33 #0.5*E/G - 1
    G = 0.5*E/(1+v) # 787500

    L  = 50
    ne = 20 # 20

    model = ops.Model(ndm=3, ndf=6)

    mat = 1
    sec = 1
    model.material('ElasticIsotropic', mat, E, v)


    if section == "Elastic":
        cmm = shape.torsion.cmm()
        cnn = shape.torsion.cnn()
        cnv = shape.torsion.cnv()
        cnm = shape.torsion.cnm()
        cmw = shape.torsion.cmw()
        A = cnn[0,0]
        model.section("ElasticFrame", sec,
                        E=E,
                        G=G,
                        A=A,
                        Ay=1*A,
                        Az=1*A,
                        Qy=cnm[0,1],
                        Qz=cnm[2,0],
                        Iy=cmm[1,1],
                        Iz=cmm[2,2],
                        J =shape._analysis.torsion_constant(),
                        Ry= cnv[1,0],
                        Rz=-cnv[2,0],
                        Sy= cmw[1,0],
                        Sz=-cmw[2,0]
        )
    else:
        model.section("ShearFiber", 1, GJ=0)
        for fiber in shape.create_fibers():
            model.fiber(**fiber, section=1, material=mat)

    model.geomTransf("Linear", 1, (0,0,1))

    model.node(0, (0,0,0))
    for i in range(ne):
        model.node(i+1, ((i+1)*L/ne, 0, 0))
        model.element(element, i+1, (i, i+1), section=1, transform=1)

    model.fix(0,  (1,1,1,  1,1,1))
    return model


if __name__ == "__main__":
    import os
    import sys
    L  = 50
    d  = 10
    b  = .5
#   L = 1e3
#   d = 200
#   b = 10
    E = 2.1e6 # MPa
    v = 0.33 #0.5*E/G - 1
    G = 0.5*E/(1+v) # 787500
#   EI = d**3*b/12 * 2.1e6
#   EI = E*0.85976
    GJ = G*(
            (d/2)*(b/2)**3 *(16/3 - 3.36*b/d*(1 - (b/d)**4/12))
           )
#   print(GJ/G)
    GJ = G*0.40433# *0.4824 #
    EI = 0.33333333333*2*GJ*L**2
    shape = Rectangle(d=d, b=b, mesh_scale=1/500)
    print(shape.summary())

    model = create_cantilever(shape,
                      section = os.environ["Section"],
                      element = os.environ.get("Element", "ExactFrame")
                   )
    end = len(model.getNodeTags()) - 1

    # MODEL DONE
    artist = veux.create_artist(model, model_config=dict(extrude_outline=shape))
    artist.draw_surfaces()
    artist.draw_outlines()

    # Apply torsional moment
    nsteps =  15
    Mmax   = 9e3
    model.pattern("Plain", 1, "Linear")
    model.load(end, (0,0,0,  1,0,0), pattern=1)

    model.system('Umfpack')
    model.integrator("LoadControl", Mmax/nsteps)
    model.test("NormDispIncr",1e-8,100,1)
#   model.test('NormUnbalance',1e-6,10,1)
    model.algorithm("Newton")
    model.analysis("Static")

    u = []
    P = []
    while model.getTime() < Mmax:
        u.append(model.nodeDisp(end, 4))
        P.append(model.getTime())
        if model.analyze(1) != 0:
            print(f"Failed at time = {model.getTime()}")
            break


    fig, ax = plt.subplots()
    ax.set_xlabel(r"Twist, $\vartheta$")
    ax.set_ylabel("Torque, $T$")
#   ax.set_xlim([0,    2])
#   ax.set_ylim([0, Mmax])
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    ax.axhline(0, color='black', linestyle='-', linewidth=1)
    ax.plot(u, P)
    ax.plot(u, [GJ*ui/L + 0.5*EI*(ui/L)**3 for ui in u])

    plt.show()
#   plt.savefig("img/e0010.png")

    artist.draw_sections(state=model.nodeDisp)
    if len(sys.argv) > 1:
        artist.save(sys.argv[1])
    else:
        veux.serve(artist)

