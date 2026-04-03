
import xara
from xsection._benchmarks import load_shape
import xara.units.iks as units
from argparse import ArgumentParser

def ParseFrameSpan():
    parser = ArgumentParser()
    parser.add_argument("-e", "--element",    default="ForceFrame",    help="Element type")
    parser.add_argument("-s", "--shape",      type=str,   default="C10",  help="Shape case", dest="shape_name")
    parser.add_argument("-n", "--number",     type=int,   default=1,    help="Number of elements")
    parser.add_argument("-m", "--mesh-scale", type=float, default=None,    help="Mesh scale")
    parser.add_argument("-v", "--poisson", type=float, default=0.25, help="Poisson ratio")
    parser.add_argument("-r", "--rotate",  default=None,  help="Rotate", action="store_true")
    parser.add_argument("-t", "--trace",   default="energetic", 
                        choices=["energetic", "geometric"],
                        help="Trace type")
    parser.add_argument("-o", "--origin", default="shear", 
                        choices=["shear", "centroid", "default"], 
                        help="Coordinate origin")
    parser.add_argument("-l", "--length", type=float, default=1.5, help="Aspect ratio L/d")

    parser.add_argument("--post", nargs="+", default=[], help="Post-processing steps")

    parser.add_argument("--save", default=False, action="store_true", help="Save results")


def parse_options():
    parser = ArgumentParser()
    parser.add_argument("-e", "--element",    default="ForceFrame",    help="Element type")
    parser.add_argument("-s", "--shape",      type=str,   default="C10",  help="Shape case", dest="shape_name")
    parser.add_argument("-n", "--number",     type=int,   default=1,    help="Number of elements")
    parser.add_argument("-m", "--mesh-scale", type=float, default=None,    help="Mesh scale")
    parser.add_argument("-v", "--poisson", type=float, default=0.25, help="Poisson ratio")
    parser.add_argument("-r", "--rotate",  default=None,  help="Rotate", action="store_true")
    parser.add_argument("-t", "--trace",   default="energetic", 
                        choices=["energetic", "geometric"],
                        help="Trace type")
    parser.add_argument("-o", "--origin", default="shear", 
                        choices=["shear", "centroid", "default"], 
                        help="Coordinate origin")
    parser.add_argument("-l", "--length", type=float, default=1.5, help="Aspect ratio L/d")

    parser.add_argument("--post", nargs="+", default=[], help="Post-processing steps")

    parser.add_argument("--save", default=False, action="store_true", help="Save results")
    options = parser.parse_args()

    if options.rotate is None and options.shape_name in ["C10", "W10"]:
        options.rotate = True


    print(f"Shape: {options.shape_name}")

    E  = 2.9 #29e3 # 2.9
    nu = options.poisson
    G = E/(2*(1+nu))
    material = xara.Material(E=E, G=G)

    if options.mesh_scale is not None:
        mesh_scale = 1/options.mesh_scale
    else:
        mesh_scale = None

    shape = load_shape(options.shape_name, 
                        mesh_scale=mesh_scale,
                        material=material,
                        units=units, 
                        mesh_type="T6")

    if options.origin == "shear":
        shape = shape.translate(-shape._analysis.shear_center())
    elif options.origin == "centroid":
        shape = shape.translate(-shape.centroid)
    elif options.origin == "default":
        pass

    if options.rotate:
        shape = shape.rotate(-units.pi/9)

    options.shape = shape

    return options
