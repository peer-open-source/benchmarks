#
# Cantilever with channel section and eccentric loading
#
# Gruttmann, Sauer, Wagner (2000), Example 6.2
#
# Section=fiber Warping=p Pattern=D Center=D Element=ExactFrame python e0012.py
#
import veux
from veux.motion import Motion
from shps.shapes import Channel
import opensees.openseespy as ops

# External libraries
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
try:
    plt.style.use("veux-web")
except:
    pass


def create_cantilever(ne, shape, element, section, nen=2, warp_base="n", center=None):
    model = ops.Model(ndm=3, ndf=6 if warp_base in "mn" else 7)

    E = 2.1e4 # MPa, or 210 GPa
    v = 0.30  # 0.5*E/G - 1
    G = 0.5*E/(1+v) # 8076.92

    nmn = ne*(nen-1)+1
    L  = 900

    mat = 1
    sec = 1
    model.material('ElasticIsotropic', mat, E, v) #G=G)



    # _m = shape.mesh
    # veux.serve(veux.render((_m.nodes, _m.cells())))

    if "fiber" in section.lower():
        model.section("ShearFiber", sec, GJ=0)

        for fiber in shape.create_fibers(center=center):
            model.fiber(**fiber, material=mat, section=sec)

    else:
        # shape.torsion._solution = shape.translate(center).torsion.solution()
        cnn = shape.cnn()
        cnm = shape.cnm()
        cnv = shape.cnv()
        cmm = shape.cmm()
        cww = shape.cww()
        cmv = shape.cmv()
        cmw = shape.cmw()
        A = cnn[0,0]
        swch = 0 if warp_base == "m" else 1
        model.section("ElasticFrame", sec,
                        E=E,
                        G=G,
                        A=A,
                        Qy=cnm[0,1],
                        Qz=cnm[2,0],
                        Iy=cmm[1,1],
                        Iz=cmm[2,2],
#                       Iyz=-cmm[1,2],
                        J =shape.elastic.J,
                        Cw= cww[0,0]*swch,
                        Rw= 0, #cnw[0,0], # this is pretty much always 0.0
                        Ry= cnv[1,0],
                        Rz= cnv[2,0],
                        Sa= cmv[0,0]*swch,
                        Sy= cmw[1,0],#*swch,
                        Sz= cmw[2,0],#*swch
        )

    model.geomTransf("Corotational02", 1, (0,0,1))

    for i,x in enumerate(np.linspace(0, L, nmn)):
        model.node(i, (x,0,0))

    model.fix(0,  (1,1,1,  1,1,1, int(warp_base in "pr")))
#   if warp_base == "r":
#       model.fix(nmn-1,  (0,0,0,  0,0,0, 1))

    for i in range(ne):
        start = i * (nen - 1)
        nodes = list(range(start, start + nen))
        model.element(element, i+1, nodes, 
                      shear = 1 if "Exact" in element else 1,
                      section=sec, transform=1)

    return model


def analyze(element, section, pattern="D", nen=2, warp_base="n", cpoint=None, render=False):
    en = ne*(nen-1)
    shape = Channel(d=30, b=10, tf=1.6, tw=1.0, mesh_scale=1/10)

    if pattern in {"D", "node"}:
        # Top
        offset = ( 0,    15)
    elif pattern == "A":
        # Shear center
        offset = (-3.571, 0)
    elif pattern == "B":
        offset = (     0, 0)
    elif pattern == "C":
        # Centroid
        offset = shape.centroid #( 2.449, 0)

    o = np.array(offset)
    if cpoint in {"D", "node"}:
        # Top
        center = ( 0,    15) - o
    elif cpoint == "A":
        # Shear center
        center = (-3.571, 0) - o
    elif cpoint == "B":
        center = (     0, 0) - o
    elif cpoint == "C":
        # Centroid
        center = ( 2.449, 0) - o


    shape = shape.translate(offset)

    model= create_cantilever(ne,
                            shape,
                            center=center,
                            element=element,
                            section=section,
                            nen=nen,
                            warp_base=warp_base)
    if render:
        artist = veux.create_artist(model, model_config=dict(extrude_outline=shape))
        artist.draw_nodes(size=10)
        # artist.draw_sections()
        # veux.serve(artist)
        motion = Motion(artist)

    #
    # Apply vertical load
    #
    speed  =  1 # animation frames
    Pmax   =  20 # kN

#   model.pattern("Plain", 2, "Constant", load={en: (0,0.1*(-1)**int(warp_base != "r"),0,  0,0,0,  0)})

    model.pattern("Plain", 1, "Linear")
    if pattern in {"D", "node"}:
        print("Pattern = node")
        model.load(en, (0,0,-1,  0,0,0,0), pattern=1)
#       model.load(ne, (0,-1,0,  0,0,0), pattern=1)

    else:
        model.eleLoad("Frame", 
                      "Dirac",
                      basis = "global",
                      force = [0, 0, -1],
                      offset=[ 1.0,
                               0.0-offset[0],
                              15.0-offset[1]],
                      pattern=1,
                      elements=[ne]
        )


    model.system('BandGen')
    model.integrator("LoadControl", Pmax/50, 5, Pmax/1000, Pmax/10)
    model.test("NormDispIncr", 1e-11, 50, 2)
#   model.test('NormUnbalance',1e-6,10,1)
    model.algorithm("Newton")
    model.analysis("Static")
    fg_warp, ax_warp = plt.subplots()

    u = []
    v = []
    w = []
    P = []
    i = 0
    while model.getTime() <= Pmax:
        i += 1
        if render:
            motion.advance(time=model.getTime()*speed)
            motion.draw_sections(rotation=model.nodeRotation,
                                 position=model.nodeDisp)
        u.append(-model.nodeDisp(ne, 1))
        v.append( model.nodeDisp(ne, 2))
        w.append(-model.nodeDisp(ne, 3))
        P.append( model.getTime())

        status = model.analyze(1)


        if status != 0:
            print(f"Failed at time = {model.getTime()} with v = {v[-1]}")
            break


    if True:
        fig, ax = plt.subplots()
        ax.set_xlabel(r"Displacements")
        ax.set_ylabel(r"Load, $\bar{F}$")
        # force y-axis ticks to even integers
        ax.yaxis.set_major_locator(MultipleLocator(2))

#       ax.set_xlim([-100, 280])
#       ax.set_xlim([-100, 280])
        ax.set_ylim([0,   Pmax])
        ax.axvline(0, color='black', linestyle='-', linewidth=1)
        ax.axhline(0, color='black', linestyle='-', linewidth=1)
        slines = iter(["-", "--", "-.", ":"])
        for file in Path("out").glob("shell-1032-case*.txt"):
            case = file.stem.split("-")[-1]
            try:
                us, ps = np.loadtxt(file, unpack=True)
            except:
                continue
            ax.plot(us, ps, label=f"Shell({case}) $u_z$", 
                    linestyle=next(slines), color="gray")
        ax.plot(u, P, label="$u_x$")
        ax.plot(v, P, label="$u_y$")
        ax.plot(w, P, label="$u_z$")
        ax.grid(True)
        ax.legend()

        name = f"{pattern}-{cpoint}-{warp_base}-{section}-{element[:5].lower()}"
        fig.savefig(f"img/1032-{name}-displacements.png")


        x = [model.nodeCoord(node, 1) for node in model.getNodeTags()]
        if warp_base not in "mn":
            ampl = [model.nodeDisp(node,7) for node in model.getNodeTags()]
            ax_warp.plot(x, ampl)

        twist = [model.nodeDisp(node,4) for node in model.getNodeTags()]
        rate = np.gradient(twist, x)
        ax_warp.plot(x, rate)

        

#           ampl[np.isclose(ampl, 0, atol=1e-8)] = 0.0
        ax_warp.set_xlim([0,  900])
#       ax_warp.set_ylim([-0.009,  0.009])
        ax_warp.axvline(0, color='black', linestyle='-', linewidth=1)
        ax_warp.axhline(0, color='black', linestyle='-', linewidth=1)
        # fg_warp.savefig(f"img/{name}-warping.png")

        if render:
            plt.show()
            motion.add_to(artist.canvas)
            veux.serve(artist)


if __name__ == "__main__":
    import os
    ne = 30
    analyze(pattern = os.environ.get("Pattern", "D"),
            element = os.environ.get("Element", "ExactFrame"),
            section = os.environ.get("Section", "ShearFiber"),
            nen=2,
            render=False,
            cpoint  = os.environ.get("Center", "D"),
            warp_base=os.environ.get("Warping", "p") # "f", "r", "n"
            )

    plt.show()