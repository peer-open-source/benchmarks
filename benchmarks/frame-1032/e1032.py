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
import xara
from xara.post import PlotConvergenceRate

# External libraries
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
try:
    plt.style.use("veux-web")
except:
    pass


def create_cantilever(ne, 
                      shape, 
                      element, 
                      transform,
                      section, 
                      nen=2,
                      warp_base="n", 
                      center=None):

    if warp_base in "mn":
        warp_type = "UT"
    else:
        warp_type = "NT"
    model = xara.Model(ndm=3, ndf=6 if warp_base in "mn" else 7)

    E = 2.1e4 # MPa, or 210 GPa
    v = 0.30  # 0.5*E/G - 1
    G = 0.5*E/(1+v) # 8076.92

    nmn = ne*(nen-1)+1
    L  = 900

    mat = 1
    sec = 1
    model.material('ElasticIsotropic', mat, E, v) #G=G)


    if "fiber" in section.lower():
        model.section("ShearFiber", sec)

        for fiber in shape.create_fibers(warp_type=warp_type): #(center=center):
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
        cvv = shape.cvv()
        # cnw = shape.cnw()
        A = cnn[0,0]
        swch = 0 if warp_base == "m" else 1
        model.section("ElasticFrame", sec,
                        E=E,
                        G=G,
                        A=A,
                        Ay=A,
                        Az=A,
                        Qy=cnm[0,1],
                        Qz=cnm[2,0],
                        Iy=cmm[1,1],
                        Iz=cmm[2,2],
                        Iyz=-cmm[1,2],
                        J =shape.elastic.J,
                        Cw= cww[0,0]*swch,
                        Rw= 0,#cnw[0,0], # this is pretty much always 0.0
                        Ry= cnv[1,0],
                        Rz= cnv[2,0],
                        # Sy= cvv[1,1],#*swch,
                        # Sz= cvv[2,2],#*swch
                        Sy= cmw[1,0],#*swch,
                        Sz= cmw[2,0],#*swch
        )

    model.geomTransf(transform, 1, (0,0,1))

    for i,x in enumerate(np.linspace(0, L, nmn)):
        model.node(i, (x,0,0))

    model.fix(0,  (1,1,1,  1,1,1, int(warp_base in "pr")))
#   if warp_base == "r":
#       model.fix(nmn-1,  (0,0,0,  0,0,0, 1))

    for i in range(ne):
        start = i * (nen - 1)
        nodes = list(range(start, start + nen))
        if "Exact" in element:
            model.element(element, i+1, nodes, 
                          shear = 1,
                          section=sec, transform=1)
        else:
            model.element(element, i+1, nodes, 
                        gauss_type="Legendre",
                        gauss_points=8,
                        shear=1,
                        section=sec, 
                        transform=1,
                        iter=(100,1e-14)
            )

    return model


def analyze(element, 
            section, 
            transform,
            pattern="D", 
            nen=2, 
            warp_base="n", 
            cpoint=None, 
            render=False):

    en = ne*(nen-1)
    shape = Channel(d=30, b=10, tf=1.6, tw=1.0, 
                    mesh_scale=1/5,
                    mesher="gmsh")

    print(shape.summary())
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
                            transform=transform,
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


    model.system('Umfpack')
    model.integrator("LoadControl",
                     Pmax/50 if "Exact" in element else Pmax/300, # 50 
                     iter=20, 
                     min_step=Pmax/1000,
                     max_step=Pmax/50 if "Exact" in element else Pmax/200
    )
    model.test("NormDispIncr", 1e-11, 500, 2)
    # model.test("Energy", 1e-16, 5000, 2)
#   model.test('NormUnbalance',1e-6,10,1)
    # model.algorithm("KrylovNewton")
    # model.algorithm("BFGS")
    # model.algorithm("AcceleratedNewton", accelerator="Secant")
    model.analysis("Static")
    # model.initialize()

    plot_cr = PlotConvergenceRate()
    fg_warp, ax_warp = plt.subplots()

    u = []
    v = []
    w = []
    P = []
    i = 0
    algorithms = iter([
        ("Newton",),
        # ("BFGS",), 
        # ("Broyden",),
        ("AcceleratedNewton", "-accelerator", "Krylov"),
        # ("BFGS",), 
        # ("Broyden",),
        # ("AcceleratedNewton", "-accelerator", "Krylov"),
        # ("BFGS",), 
        # ("Broyden",),
        # ("AcceleratedNewton", "-accelerator", "Krylov"),
        # ("BFGS",), 
        # ("Broyden",),
        # ("AcceleratedNewton", "-accelerator", "Krylov"),
        # ("BFGS",), 
        # ("Broyden",),
        # ("AcceleratedNewton", "-accelerator", "Krylov"),
        # ("BFGS",), 
        # ("Broyden",),
        # ("BFGS",), 
        # ("Broyden",),
        # ("BFGS",), 
        # ("Broyden",),
        # ("KrylovNewton",), 
        # ("NewtonLineSearch",),
    ])
    status = -1
    while model.getTime() <= Pmax:
        i += 1
        if status != 0:
            try:
                alg = next(algorithms)
                print(f"Switching to algorithm: {alg}")
                model.algorithm(*alg)
                # status = 0
            except StopIteration:
                print(f"Failed at time = {model.getTime()} with v = {v[-1]}")
                break

        if render:
            motion.advance(time=model.getTime()*speed)
            motion.draw_sections(rotation=model.nodeRotation,
                                 position=model.nodeDisp)
        u.append(-model.nodeDisp(ne, 1))
        v.append( model.nodeDisp(ne, 2))
        w.append(-model.nodeDisp(ne, 3))
        P.append( model.getTime())

        status = model.analyze(1)
        plot_cr.update(model)

        # import sys
        # from pandas import DataFrame as df
        # print(df(model.getTangent()))
        # sys.exit()

    plot_cr.draw()
    plot_cr.finalize()


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
        for file in Path("out").glob("shell-1032-case3-pu.txt"):
            case = file.stem.split("-")[-1]
            try:
                # us, ps = np.loadtxt(file, unpack=True)
                ps, us, vs, ws = np.loadtxt(file, unpack=True)
            except:
                continue
            ax.plot(us, ps, label=f"Shell({case}) $u_z$", 
                    linestyle=next(slines), color="gray")
            ax.plot(vs, ps, label=f"Shell({case}) $u_y$", 
                    linestyle=next(slines), color="lightgray")
            ax.plot(ws, ps, label=f"Shell({case}) $u_x$", 
                    linestyle=next(slines), color="darkgray")
        ax.plot(u, P, label="$u_x$")
        ax.plot(v, P, label="$u_y$")
        ax.plot(w, P, label="$u_z$")
        ax.grid(True)
        ax.legend()


        wagner = int("Wagner" in os.environ)
        name = f"{pattern}-{cpoint}-{warp_base}-{section}-{element[:5].lower()}-{transform[-2:]}-wagner{wagner}"
        # fig.savefig(f"img/1032-{name}-displacements.png")


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
    ne = 20
    # Good:
    #   1032-D-D-n-fiber-force-02-wagner0-displacements.png
    
    analyze(pattern = os.environ.get("Pattern", "D"),
            element = os.environ.get("Element", "ExactFrame"),
            section = os.environ.get("Section", "ShearFiber"),
            transform = os.environ.get("Transform", "Corotational02"),
            nen=2,
            render=False,
            cpoint  = os.environ.get("Center", "D"),
            warp_base=os.environ.get("Warping", "p") # "f", "r", "n"
            )

    plt.show()