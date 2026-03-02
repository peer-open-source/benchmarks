#
# Cantilever with channel section and eccentric loading
#
# Gruttmann, Sauer, Wagner (2000), Example 6.2
#
# Section=fiber Warping=p Pattern=D Center=D Element=ExactFrame python e0012.py
#
import veux
from xara import Material, Section
from veux.motion import Motion
from shps.shapes import Channel
import opensees.openseespy as ops

# External libraries
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
# try:
#     # plt.style.use("veux-web")
#     plt.style.use("thesis")
# except:
#     pass


def create_cantilever(ne, shape, element, section, material,
                      nen=2, warp_base="n", center=None):

    if warp_base in "mn":
        warp_type = "UT"
    else:
        warp_type = "NT"
    model = ops.Model(ndm=3, ndf=6 if warp_base in "mn" else 7)

    E = material["E"]
    # v = material["nu"]
    # G = 0.5*E/(1+v)
    nmn = ne*(nen-1)+1
    L  = 900

    mat = 1
    sec = 1
    model.material(material, 1)
    # model.material("J2BeamThread", #"NonlinearJ2", #
    #                mat, E=E, nu=v, 
    #                Hkin=material["Hk"],
    #                Fy=material["Fy"])



    model.section("ShearFiber", sec)

    for fiber in shape.create_fibers(center=center, warp_type=warp_type):
        model.fiber(**fiber, material=mat, section=sec)


#   model.geomTransf("Corotational", 1, (0,1,0))
    model.geomTransf("Corotational02", 1, (0,0,1))

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
                          section=sec,
                          transform=1,
                        #   shear= 1 if "Exact" in element else 0
            )
        else:
            model.element(element, i+1, nodes,
                          section=sec,
                          transform=1,
                          n=3, gauss_type="Legendre",
                          shear=1,
                          iter=(15, 1e-9)
                        #   shear= 1 if "Exact" in element else 0
            )

    return model


def analyze(element, section, pattern="D", nen=2, warp_base="n", cpoint=None, render=False):
    material = Material(
        E  = 2.1e4, # MPa, or 210 GPa
        nu = 0.30,  # 0.5*E/G - 1
        Fy = 36.0,
        Hkin = 0.001 * 2.1e4,
        type="J2BeamThread"
    )
    # material["Hk"] = 0.001 * material["E"]

    en = ne*(nen-1)
    shape = Channel(d=30, b=10, tf=1.6, tw=1.0, 
                    mesh_scale=1/3,
                    mesher="gmsh",
                    mesh_type="T3")

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
                            material=material,
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


    model.system("BandGeneral")
    model.integrator("DisplacementControl", 
                     ne, 3, -0.1 if "Exact" in element else -0.1)
    model.test("Energy", 
               1e-18 if "Exact" in element else 1e-16, 40, 1)
#   model.algorithm("KrylovNewton")
    model.algorithm("Broyden")
    model.analysis("Static")
    fg_warp, ax_warp = plt.subplots()

    w = []
    P = []
    i = 0
    try:
        while model.nodeDisp(ne, 3) > -250.0:
            i += 1
            if render:
                motion.advance(time=model.getTime()*speed)
                motion.draw_sections(rotation=model.nodeRotation,
                                    position=model.nodeDisp)
            w.append(-model.nodeDisp(ne, 3))
            P.append( model.getTime())


            if model.analyze(1) != 0:
                print(f"Failed at time = {model.getTime()} with u = {w[-1]}")
                break
    except KeyboardInterrupt:
        pass


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
        ax.plot(w, P, label="$u_z$")
        ax.grid(True)
        ax.legend()

        name = f"{pattern}-{cpoint}-{warp_base}-{section}-{element[:5].lower()}"
#       fig.savefig(f"img/{name}-displacements.png", dpi=600)


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

    ne = 30 # 30
    analyze(pattern = os.environ.get("Pattern", "D"),
            element = os.environ.get("Element", "ExactFrame"),
            section = os.environ.get("Section", "ShearFiber"),
            nen=2,
            render=False,
            cpoint  = os.environ.get("Center", "D"),
            warp_base=os.environ.get("Warping", "p") # "f", "r", "n"
            )

    plt.show()
