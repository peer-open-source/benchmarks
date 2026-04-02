#
# Inelastic nonlinear uniform torsion
#
# Jan 12, 2026
#

import os
import xara
from xara.benchmarks import Prism
import xara.units.iks as units
from xara.helpers import find_node
from xara.post.convergence import PlotConvergenceRate
from xsection.analysis import SaintVenantSectionAnalysis
from xsection.library import WideFlange
from xsection.properties import plastic_torque
import thesis as plt
import thesis
import numpy as np

verbose = False
if verbose:
    progress = lambda x: x
else:
    from tqdm import tqdm as progress
    # progress = lambda x: x

from post import PlotResponse


Cases = [
    dict(element="ExactFrame", wagner=False, trace="NR", tag=1),
    dict(element="ExactFrame", wagner=True,  trace="NR", tag=2),

    # dict(element="ForceFrame", wagner=False, trace="NR", tag=3),
    # dict(element="ForceFrame", wagner=True,  trace="NR", tag=4),

    # dict(element="ExactFrame", wagner=False, trace="NT", tag=5),
    # dict(element="ExactFrame", wagner=True,  trace="NT", tag=6),

    # dict(element="ExactFrame", wagner=False, trace="UE", tag=5),
    # dict(element="ExactFrame", wagner=True,  trace="UE", tag=6),

    # dict(element="ForceFrame", wagner=False, trace="UG", tag=7),
    # dict(element="ForceFrame", wagner=True,  trace="UG", tag=8),
    # dict(element="ForceFrame", wagner=False, trace="MS", tag=9),
    dict(element="ExactFrame", wagner=True,  trace="NR", tag=10, nonlinear=True),
]

class Test4:
    def __init__(self):
        self.name = "Test 4"
        self.Tmax = 19e3*units.newton*units.meter
        self.L = 1.93*units.meter
        self.a =  self.L*0.3
        self.b = [self.L*0.3, self.L*0.7]


        self.shape = WideFlange(
                    b=0.1509*units.meter,
                    d=0.1524*units.meter,
                    tf=0.0122*units.meter,
                    tw=0.0080*units.meter,
                    material=xara.Material(
                        E  = 29e3*units.ksi,
                        nu = 0.27,
                        Fy = 41.3*units.ksi,
                        Hkin = 0.03 * 29e3*units.ksi,
                        type = "J2BeamThread"
                    ),
                    mesh_scale=1/5,
                    mesh_type="T6",
                    mesher="gmsh"
        )
        self.data = [
            # rotation (rad), torque (inch-kip)
            0,                      0,
            0.018046240419439140,  15.306122448979579,
            0.025780343456341615,  23.265306122448976,
            0.033514446493244140,  26.938775510204096,
            0.038670515184512480,  32.755102040816325,
            0.051560686912683285,  39.183673469387756,
            0.056716755603951620,  45.61224489795919,
            0.074762996023390760,  51.42857142857143,
            0.095387270788464100,  56.632653061224474,
            0.118589579899171520,  63.67346938775509,
            0.185618472885659800,  72.24489795918366,
            0.417641563992734600,  87.24489795918366,
            0.585213796458955200,  97.95918367346937,
            0.881687746206884400, 122.44897959183672,
            1.064728184746910000, 138.36734693877548,
        ]


class Test5:
    def __init__(self):
        self.name = "Test 5"
        self.Tmax = 24e3*units.newton*units.meter
        self.L = 1.93*units.meter
        self.a = self.L/2
        self.b = [self.L/2]

        self.shape = WideFlange(
                    b=0.1509*units.meter,
                    d=0.1524*units.meter,
                    tf=0.0122*units.meter,
                    tw=0.0080*units.meter,
                    material=xara.Material(
                        E  = 29e3*units.ksi,
                        nu = 0.29,
                        Fy = 41.3*units.ksi,
                        Hkin = 0.03*29e3*units.ksi,
                        type = "J2BeamThread"
                    ),
                    mesh_scale=1/2,
                    mesh_type="T6",
                    mesher="gmsh"
        )

        self.data = [
            0.0,                    0.78431372549020,
            0.029581851728717468,  25.09803921568627,
            0.039442468971623235,  33.33333333333334,
            0.046016213800227135,  40.78431372549022,
            0.062450575871736860,  50.98039215686276,
            0.069024320700340760,  60,
            0.085458682771850370,  68.62745098039215,
            0.098606172429058170,  77.64705882352942,
            0.118327406914869810,  86.66666666666669,
            0.138048641400681400,  96.47058823529413,
            0.161056748300795030, 107.84313725490196,
            0.213646706929626060, 120.00000000000001,
            0.808570613918277100, 161.96078431372550,
            0.913750531175939100, 171.37254901960785,
            1.084667896719639700, 184.70588235294120,
        ]


def _plastic_torque(shape, test, Fy):
    Tp = 0.25*shape.tf*shape.bf**2*Fy
    Ts = plastic_torque(shape)*Fy/np.sqrt(3)
    To = Ts + Tp*shape.d/test.b[0]
    print(f"{Ts = }, {Tp = }, {To = }")
    return To


def analyze(model, T, test, plots=()):
    # Loading
    # time step can be much larger. Fine stepping for plots.

    steps = 100

    model.system("BandGeneral")
    # model.constraints("Transformation")
    # model.algorithm("NewtonLineSearch", 0.6)
    model.algorithm("Newton")
    model.integrator("LoadControl", 1/steps)
    model.analysis("Static")
    # model.test("Residual", 1e-8, 20, 1 if verbose else 0)
    # model.test("Energy", 1e-14, 200, 2 if verbose else 0)
    model.test("NormDispIncr", 1e-9, 10, 1 if verbose else 0)

    model.pattern("Plain", 1, "Linear", load={
            find_node(model, x=b): [0,0,0, T,0,0, 0]
        for b in test.b}
    )
    tip = find_node(model, x=test.a)
    try:
        while model.state.u(tip, 4) < test.data[-2]:

            if model.analyze(1) != 0:
                if model.state.u(tip,4)/test.data[-2] < 0.95:
                    raise RuntimeError(f"Failed at {model.state.u(tip,4)/test.data[-2]}")
                return

            for plot in plots:
                plot.update(model)#/1000/(units.newton*units.meter))
        return

    except KeyboardInterrupt:
        pass




def create_section(shape, trace, wagner):

    def section(model, tag, shape, material):

        model.material(material, 1)
        if trace == "MS":
            name = "NDFiber"
        else:
            name = "ShearFiber"

        section = xara.Section(name, shape, 
                               mixed_type=trace, wagner=wagner)
        model.section(section, tag)

    return section




if __name__ == "__main__":
    import sys 
    # os.environ["Wagner"] = "1"
    Save = False
    transform = os.environ.get("Transform", "Corotational02")

    test = Test4()
    if len(sys.argv) > 1 and sys.argv[1] == "5":
        test = Test5()

    Fy = 41.3*units.ksi #36.2594*units.ksi # 
    E  = 29e3*units.ksi
    # Fy = 250*units.MPa
    # E  = 200e3*units.GPa
    nu = 0.29 #7 # 0.25
    G  = E/(2*(1+nu))
    T = test.Tmax
    print(f"{Fy = }")


    if False:
        material = xara.Material(
            E  = E,
            nu = nu,
            Fy = Fy,
            # Hiso = 0.03 * E,
            Hkin = 0.03 * E,#900*units.ksi, #
            # Fsat = 1.5*Fy,
            type =  "J2BeamThread" # "NonlinearJ2" #  "J2" # "GeneralizedJ2" # "J2Simplified" #
        )
    else:
        material = xara.Material(
            E  = E,
            nu = nu,
            Fy = Fy,
            Hiso = 0.01*E,
            # Hkin = 0.03 * E,#900*units.ksi, #
            Hsat = 50, #0.005*Fy/(Fu-Fy)*E,
            Fsat = 1.5*Fy,
            type = "NonlinearJ2" # "J2BeamThread" #   "J2" # "GeneralizedJ2" # "J2Simplified" #
        )

    size = 1 # 3 # 40
    shape = WideFlange(
                    b=0.1509*units.meter,
                    d=0.1524*units.meter,
                    tf=0.0122*units.meter,
                    tw=0.0080*units.meter,
                    material=material,
                    mesh_scale=1/size,
                    mesh_type="T6",
                    mesher="gmsh")
    

    L = test.L
    To = _plastic_torque(shape, test, Fy)
    sv = SaintVenantSectionAnalysis(shape)
    GJ = sv.twist_rigidity()
    print(sv.summary(format="texsection"))

    ##
    plot_1 = PlotResponse(test.Tmax/To)
    plot_2 = PlotConvergenceRate(n_ex_start=0, skip=False)
    if True: #test.name == "Test 5":
        plot_1.ax.plot(
            [d for d in test.data[::2]],
            [t/To/(units.kip*units.inch) for t in test.data[1::2]],
            "o--", color="k", 
            fillstyle="none",
            # markersize=3, 
            label="Experiment"
        )

    ##
    A = 1 if test.name == "Test 5" else 0
    ne = 10 # if test.name == "Test 4" else 10
    shear = 1

    for case in Cases:
        i = case["tag"]
        element = case["element"]
        wagner  = case["wagner"]
        trace   = case["trace"]
        nonlinear = case.get("nonlinear", False)
        if nonlinear:
            shape.material = xara.Material(
                E  = E,
                nu = nu,
                Fy = Fy,
                Hiso = 0.03*E,
                # Hkin = 0.03 * E,#900*units.ksi, #
                Hsat = 15, #0.005*Fy/(Fu-Fy)*E,
                Fsat = 1.5*Fy,
                type = "NonlinearJ2" # "J2BeamThread" #   "J2" # "GeneralizedJ2" # "J2Simplified" #
            )

        if not shear and "Exact" in element:
            continue


        print(f"Running {element} shear={shear} trace={trace}")

        prism = Prism(shape=shape,
                    length=L,
                    boundary=((1,1,1,  1,0,0, 0),
                              (A,1,1,  1,0,0, 0)),
                    material=shape.material,
                    element=element,
                    section=create_section(shape, trace, wagner),
                    shear=shear,
                    warp = [1] if "N" in trace else None,
                    integration={"points": 3, "type": "Legendre"},
                    transform=transform,
                    divisions=ne,
                    order=2 if "Exact" in element else 1,
                    # iter=(20, 1e-10)
                )

        model = prism.create_model(iter=(40, 1e-14),
                                    echo_file=open(f"out/T{test.name[-1]}_C{case['tag']}.tcl", "w+")
                )
        model.print(json=f"out/T{test.name[-1]}_C{case['tag']}.json")


        plot_2.reset(label=f"({i}) {element}, {' (Wagner)' if wagner else 'Linear'}{' ('+str(trace)+')' if trace else ''}")
        plot_1.reset(model, find_node(model, x=test.a), 4,
                    label=f"({i}) {element}, {'Wagner' if wagner else 'Linear'} {' ('+str(trace)+')' if trace else ''}")

        analyze(model, T, test,
                plots=[plot_1, plot_2]
        )

        plot_1.draw()
        plot_2.draw()

        if Save:
            plot_1.save_data("out/T{}_C{}_data.txt".format(test.name[-1], i))

    
    plot_1.finish()
    plot_2.finish()
    thesis.legend(plot_1.ax)
    plot_1.ax.figure.savefig(f"img/3011-{test.name[-1]}-mesh{size}.pgf", backend="pgf")
    plt.show()

