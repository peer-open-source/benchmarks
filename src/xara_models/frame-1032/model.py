"""
             T
            _________
            |x _____|
     S    O | |
      x     |x| x C
            | |_____.
            |_______|

"""

import xara
import veux
import os
from xara.shapes import Channel
import numpy as np
from pathlib import Path
from scipy.spatial.transform import Rotation
from xsection.analysis import SaintVenantSectionAnalysis


class Problem:
    Cases = [
        dict(origin="O", warp_base="n", warp_type="UE"),
        dict(origin="O", warp_base="n", warp_type="UG"),
    ] + [
        dict(origin="O", warp_base=w,   warp_type="NT")
        for w in ["f", "r", "p"]
    ]  + [
        dict(origin="O", warp_base=w,   warp_type="NR")
        for w in ["f", "r", "p"]
    ] 
    # + [
    #     dict(origin="C", warp_base=w, warp_type="NT")
    #     for w in ["f", "r", "p"]
    # ] + [
    #     dict(origin="S", warp_base=w, warp_type="NT")
    #     for w in ["f", "r", "p"]
    # ] + [
    #     dict(origin="T", warp_base=w, warp_type="NT")
    #     for w in ["f", "r", "p"]
    # ]
    expl = "1032"
    def __init__(self,
                origin="O",
                length=900,
                warp_type=None,
                material=None,
                warp_base="n"):
        """
        origin:
        - C: centroid
        - S: shear center
        - O: center of web
        - T: top of the web

        warp_base:
        - n: no warping DOF
        - m: 
        """
        self.length = length
        
        if origin not in "CSOT":
            raise ValueError(f"Invalid origin: {origin}")

        if material is None:
            v = 0.3
            E = 2.1e4 # MPa, or 210 GPa
            self.material = xara.Material(
                E = E, # MPa, or 210 GPa
                G = 0.5*E/(1+v) # 8076.92
            )
        else:
            self.material = material

        # Natural origin is at center of web
        shape = Channel(d=30,
                        b=10,
                        tf=1.6, 
                        tw=1.0, 
                        material=self.material,
                        mesh_scale=1,
                        mesh_type="T6",
                        mesher="gmsh")
        
        self.origin = origin
        self.warp_base = warp_base

        print(shape.summary())

        print(SaintVenantSectionAnalysis(shape).summary(format=""))

        # veux.serve(veux.render(shape.model))

        if origin in {"T", "node"}:
            # Top
            offset = ( 0,   shape.d/2)
        elif origin == "S": # was A
            # Shear center
            offset = shape._analysis.shear_center()
        elif origin == "O": # was B
            offset = (     0, 0)
        elif origin == "C":
            # Centroid
            offset = ( 2.449, 0)# shape.centroid #

        offset = np.array(offset)
        self.load_offset = np.array([0, 15]) - offset

        print(f"Origin = {origin}, offset = {offset}, load_offset = {self.load_offset}, warp_base = {warp_base}")



        self.shape = shape.translate(-np.array(offset))


        if warp_base in "mn":
            warp_type = "UE"
        else:
            warp_type = "NT"

        self.warp_type = warp_type
        self.name = f"{origin}-{warp_base}-{warp_type}"



    def render(self):
        import veux
        model = self.create_model(element="ExactFrame", 
                                  section="MixedFiber", 
                                  transform="Linear", nen=2, ne=2)
        artist = veux.create_artist(model, 
                                    model_config=dict(extrude_outline=self.shape),
                                    vertical=3)
        artist.draw_sections()
        artist.draw_origin(extrude=True, scale=20)
        artist.draw_nodes(size=10)
        veux.serve(artist)
        return artist


    def create_model(self, element, section, transform, nen=2, ne=30):
        warp_base = self.warp_base
        wagner = int("Wagner" in os.environ)
        mname = f"{self.name}-{element[:5].lower()}"#-{transform[-2:]}" #-wagner{wagner}"
        model = create_cantilever(ne,
                                  self.length,
                                    self.shape,
                                    element=element,
                                    transform=transform,
                                    section=section,
                                    name =mname,
                                    nen=nen,
                                    warp_type=self.warp_type,
                                    warp_base=warp_base)

        model.name = mname
        return model


    def apply_loads(self, model):
        #
        # Apply vertical load
        #
        origin = self.origin
        offset = self.load_offset

        tip = model.getNodeTags()[-1]
        ne = model.getEleTags()[-1]
    #   model.pattern("Plain", 2, "Constant", load={en: (0,0.1*(-1)**int(warp_base != "r"),0,  0,0,0,  0)})

        model.pattern("Plain", 1, "Linear")
        if origin in {"T", "node"}:
            print("Nodal load")
            model.load(tip, (0,0,-1,  0,0,0,0), pattern=1)

        else:
            model.eleLoad("Frame", 
                        "Dirac",
                        basis = "global",
                        force = [0, 0, -1],
                        offset=[ 1.0, # 1.0 means load is applied at end j
                                 offset[0],
                                 offset[1]],
                        pattern=1,
                        elements=[ne]
            )

    def analyze(self, model, post=(), Pmax=20):
        from xara.post import PlotConvergenceRate
        import thesis as plt
        from matplotlib.ticker import MultipleLocator

        element = model.name.lower()

        self.apply_loads(model)
        tip = model.getNodeTags()[-1]
        model.system('Umfpack')
        model.integrator("LoadControl", Pmax/100
                        # Pmax/100 if "exact" in element else Pmax/300, # 50 
                        # iter=20, 
                        # min_step=Pmax/1000,
                        # max_step=Pmax/100 if "exact" in element else Pmax/200
        )

        # model.test("NormDispIncr", 1e-11, 500, 2)
        model.test("Energy", 1e-16, 500, 0)
        # model.test('Residual',1e-7,50,0)
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
                    # print(f"Switching to algorithm: {alg}")
                    model.algorithm(*alg)
                except StopIteration:
                    print(f"Failed at time = {model.getTime()} with v = {v[-1]}")
                    break

            un = model.nodeDisp(tip)[:3]
            Rn = Rotation.from_quat(model.nodeRotation(tip)).as_matrix()
            rn = [0, *self.load_offset]
            un += Rn@rn - rn
            u.append(-un[0])
            v.append( un[1])
            w.append(-un[2])
            # print(f"Time: {model.getTime():.4f}, ux = {u[-1]:.4f}, uy = {v[-1]:.4f}, uz = {w[-1]:.4f}")
            # u.append(-model.nodeDisp(tip, 1))
            # v.append( model.nodeDisp(tip, 2))
            # w.append(-model.nodeDisp(tip, 3))
            P.append( model.getTime())

            status = model.analyze(1)
            plot_cr.update(model)


        plot_cr.draw()
        plot_cr.finalize()


        if True:
            fig, ax = plt.subplots()
            ax.set_xlabel(r"Displacements")
            ax.set_ylabel(r"Load, $\bar{F}$")
            # force y-axis ticks to even integers
            ax.yaxis.set_major_locator(MultipleLocator(2))

            ax.set_xlim([0, 250])
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
            plt.legend(ax)


            name = model.name

            fig.savefig(f"img/og-1032-{name}-displacements.png", dpi=600)



            x = [model.nodeCoord(node, 1) for node in model.getNodeTags()]
            if self.warp_base not in "mn":
                ampl = [model.nodeDisp(node,7) for node in model.getNodeTags()]
                ax_warp.plot(x, ampl)

            twist = [model.nodeDisp(node,4) for node in model.getNodeTags()]
            rate = np.gradient(twist, x)
            ax_warp.plot(x, rate)



    #           ampl[np.isclose(ampl, 0, atol=1e-8)] = 0.0
            ax_warp.set_xlim([0,  self.length])
    #       ax_warp.set_ylim([-0.009,  0.009])
            ax_warp.axvline(0, color='black', linestyle='-', linewidth=1)
            ax_warp.axhline(0, color='black', linestyle='-', linewidth=1)
            # fg_warp.savefig(f"img/{name}-warping.png")



def create_cantilever(ne, 
                      length,
                      shape, 
                      element,
                      transform,
                      section, 
                      name=None,
                      warp_type=None,
                      nen=2,
                      warp_base="n"):

    model = xara.Model(ndm=3, ndf=6 if warp_base in "mn" else 7, 
                       echo_file=open(f"out/{name}.tcl","w+") if name is not None else None)


    nmn = ne*(nen-1)+1
    L  = length

    mat = 1
    sec = 1
    material = shape.material
    E = material["E"]
    G = material["G"]
    v = 0.5*E/G - 1
    model.material(material, 1)

    if warp_type and "C" in warp_type:
        model.section("ShearFiber", sec)

        for fiber in shape.create_fibers(warp_type=warp_type):
            model.fiber(**fiber, material=mat, section=sec)

    elif "fiber" in section.lower():
        model.section("ShearFiber", sec, shape, mixed_type=warp_type)

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
    if warp_base == "r":
        model.fix(nmn-1,  (0,0,0,  0,0,0, 1))

    for i in range(ne):
        start = i * (nen - 1)
        nodes = list(range(start, start + nen))
        if "Exact" in element:
            model.element(element, i+1, 
                          nodes, 
                          shear = 1,
                          section=sec, transform=1)
        else:
            model.element(element, i+1, nodes, 
                        gauss_type="Legendre",
                        gauss_points=3,
                        shear=0,
                        section=sec, 
                        transform=1,
                        iter=(20,1e-14)
            )

    return model
