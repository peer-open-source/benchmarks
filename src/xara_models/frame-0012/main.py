from argparse import ArgumentParser


from run_strain import run_strain
from run_trace import run_trace


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-e", "--element", default="ForceFrame",    help="Element type")
    parser.add_argument("-s", "--shape",   type=str,   default="C10",  help="Shape case")
    parser.add_argument("-n", "--number",  type=int,   default=1,    help="Number of elements")
    parser.add_argument("-v", "--poisson", type=float, default=0.3, help="Poisson ratio")
    parser.add_argument("-r", "--rotate",  default=True,  help="Rotate", action="store_true")
    parser.add_argument("-t", "--trace",   default="energetic", 
                        choices=["energetic", "geometric"],
                        help="Trace type")
    parser.add_argument("-c", "--center", default="shear", 
                        choices=["shear", "centroid"], 
                        help="Coordinate origin")
    parser.add_argument("-l", "--length", type=float, default=1.5, help="Aspect ratio L/d")
    options = parser.parse_args()

    run_strain(options)

    run_trace(options)
