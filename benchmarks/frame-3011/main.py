#
# Inelastic nonlinear uniform torsion
#
# Jan 12, 2026
#

import os
import veux
from xara.benchmarks import Prism
import xara.units.us as units
from xara.helpers import find_node
from xsection.library import WideFlange
import numpy as np
import matplotlib.pyplot as plt
# plt.style.use("typewriter")

verbose = True
if verbose:
    progress = lambda x: x
else:
    from tqdm import tqdm as progress
    # progress = lambda x: x


def create_section(shape, trace, shear_, warp_=1):

    def section(model, tag, shape, material):
        # shape = shape.translate(-shape.centroid)
        m1 = {k: v for k, v in material[0].items() if k not in {"type"}}
        if not shear_:
            model.section("Fiber", tag, GJ=m1["G"]*shape.elastic.J)
        elif trace is not None:
            trace_ = shape.create_trace(form=trace)
            align = trace_.shift_shear_gamma()
            align = list(map(float, [align[0,0], align[0,1], align[1,0], align[1,1]]))
            model.section("ShearFiber", tag, 
                          align=align,
                          shiftTwist=trace_.shift_twist_gamma(),
                          shiftAxial=trace_.shift_twist_axial()
            )
        elif shear_:
            model.section("ShearFiber", tag)


        name = material[0]["type"]
        if not shear_:
            name = "Hardening"

        model.material(name, 1, **m1)

        for fiber in shape.create_fibers(warp=bool(warp_), shear=(trace is not None)):

            if not shear_:
                model.fiber(y=fiber["y"], 
                            z=fiber["z"],
                            area=fiber["area"],
                            material=1, section=tag)
            else:
                model.fiber(**fiber,
                            material=1, section=tag)

    return section

def analyze(model, T, shear=True, trace=None, plots=()):
    # Loading
    steps = 150 if "Wagner" not in os.environ else 400


    model.system("BandGeneral")
    # model.constraints("Transformation")
    model.algorithm("NewtonLineSearch", 0.6)
    # model.algorithm("Newton")
    model.integrator("LoadControl", 1/steps)
    model.analysis("Static")
    model.test("Energy", 1e-18, 15, 2 if verbose else 0)

    model.pattern("Plain", 1, "Linear", load={
        find_node(model, x=L/2): [0,0,0, T,0,0, 0]}
    )

    try:

        for _ in progress(range(steps)):

            if model.analyze(1) != 0:
                print(f"Failed at time = {model.state.time}")
                return

            for plot in plots:
                plot.update()
        return

    except KeyboardInterrupt:
        pass

    return


class PlotResponse:
    def __init__(self):
        self.node = None
        self.dof = None 
        self.model = None
        self.u = [0]
        self.V = [0]

        self.markers = iter(["-","-.","--","-.", ":"])
        self.colors  = iter(["gray", "r", "b", "g", "m"])

        fig, (ax,leg) = plt.subplots(ncols=2,
                                     gridspec_kw={"width_ratios": [5, 1.5]})#, constrained_layout=True)
        leg.axis("off")
        ax.axhline(0, color='k', lw=0.5)
        ax.axvline(0, color='k', lw=0.5)
        ax.set_xlabel("Rotation (rad)")
        ax.set_ylabel("Torque (kN·m)")
        ax.grid(True)
        self.fig = fig
        self.leg = leg
        self.ax = ax
    
    def reset(self, model, node, dof, label=None):
        self.label = label
        self.model = model
        self.node = node
        self.dof = dof
        self.u = [0]
        self.V = [0]

    def update(self):
        self.u.append(self.model.state.u(self.node, self.dof))
        self.V.append(self.model.getTime()*T/1000/(units.newton*units.meter))

    def draw(self):
        self.ax.plot(self.u,self.V,
                next(self.markers), 
                color=next(self.colors),
                label=self.label)

    def finish(self):
        h,l = self.ax.get_legend_handles_labels()
        self.leg.legend(h,l,borderaxespad=0)
        self.ax.set_xlim([0, None])
        self.ax.set_ylim([0, None])
        plt.tight_layout()



if __name__ == "__main__":
    from xara.post import FiberStress
    from post import PlotPlasticSpread, ElementFiberYieldMap
    os.environ["Wagner"] = "1"

    # Fy = 250*units.MPa
    # E  = 200*units.GPa
    Fy = 41.3*units.ksi
    E  = 29e3*units.ksi
    nu = 0.27 #7 # 0.25
    G  = E/(2*(1+nu))
    T = 22e3*units.newton*units.meter

    size = 4 # 3 # 40
    shape = WideFlange(
                    b=0.1509*units.meter,
                    d=0.1524*units.meter,
                    tf=0.0122*units.meter,
                    tw=0.0080*units.meter,
                    poisson=nu,
                    mesh_scale=1/size,
                    mesher="gmsh")

    print(shape.summary(shear=True))

    material = "J2BeamFiber" #  "NonlinearJ2" #  "J2" # "GeneralizedJ2" # "J2Simplified" #

    L = 1.93*units.meter
    transform = os.environ.get("Transform", "Corotational02")

    ##
    plot_1 = PlotResponse()

    ##
    i = 1
    for ne in [2]:
        # for shear in [1]:
        shear = 1
        for element in ["ExactFrame", "ForceFrame"]:#, "ExactFrame"]:
            for trace in ["energetic"]:

                if not shear and "Exact" in element:
                    continue

                print(f"Running {element} shear={shear} trace={trace}")
                prism = Prism(shape=shape,
                            length=L,
                            boundary=((1,1,1,  1,0,0,1),
                                      (1,1,1,  1,0,0,1)),
                            material=[
                                {
                                    "type": material,
                                    "E":  E,
                                    "G":  G,
                                    "Fy": Fy,
                                    "Hiso":  0.000*E,
                                    "Hkin":  0.003*E,
                                }
                            ],
                            element=element,
                            section=create_section(shape, trace, shear),
                            shear=shear,
                            # warp=[1],
                            integration={"points": 4, "type": "Legendre"},
                            transform=transform,
                            divisions=ne,
                            order=3 if "Exact" in element else 1
                        )

                model = prism.create_model(
                    # echo_file=open(f"out/{element}-{trace[0]}-{shear}.tcl", "w+")
                )
                plot_1.reset(model, find_node(model, x=L/2), 4,
                             label=f"({i}) {element}, $n_e = {ne}$, {' ('+str(trace)+')' if trace else ''}")

                analyze(model, T,
                        trace=trace,
                        shear=shear,
                        plots=[plot_1]
                )
                plot_1.draw()
                i += 1

    plt.tight_layout()

    plot_1.finish()
    plot_1.ax.figure.savefig(f"img/3011-mesh{size}.png", dpi=600)
    plt.show()

