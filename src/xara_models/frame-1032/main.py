#
# Cantilever with channel section and eccentric loading
#
# Gruttmann, Sauer, Wagner (2000), Example 6.2
#
# Previously 0013
#
import os

# External libraries
import numpy as np
import veux
import matplotlib.pyplot as plt
from xara_models._plots import PlotResponse

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("--warp-type", default=None, help="Warping type: NT, UE, NR")
parser.add_argument("--mesh-scale", type=float, default=1.0, help="Mesh scale factor")
parser.add_argument("--wagner",  default=False, help="Whether to include Wagner effect", action="store_true")
parser.add_argument("-L", "--length", type=float, default=900.0, help="Beam length")
parser.add_argument("-O", "--origin", default="O", help="Origin point: O, C, D")
parser.add_argument("-B", "--warp-boundary", default="n", help="Warping boundary condition: n, f, r")
parser.add_argument("-N", "--ne", type=int, default=30, help="Number of elements along the length")


def _post_p(p):
    from scipy.spatial.transform import Rotation
    offset = p.load_offset

    def _post_u(model):
        tip = model.getNodeTags()[-1]
        un = model.nodeDisp(tip)[:3]
        Rn = Rotation.from_quat(model.nodeRotation(tip)).as_matrix()
        rn = [0, *offset]
        un += Rn@rn - rn
        return [
            -un[0],  # ux
             un[1],  # uy
            -un[2], # uz
        ]

    return _post_u

if __name__ == "__main__":
    from model import Problem
    options = parser.parse_args()
    if options.wagner:
        os.environ["Wagner"] = "1"
    # Good:
    #   1032-D-D-n-fiber-force-02-wagner0-displacements.png
    
    p = Problem(origin  = options.origin,
                length = options.length,
                mesh_scale = options.mesh_scale,
                warp_type = options.warp_type,
                wagner = options.wagner,
                warp_base=options.warp_boundary,
            )
    
    post = [
            PlotResponse(
                y=lambda m: m.getTime(),
                x=_post_p(p),
            ), 
            # PlotConvergenceRate()
    ]

    # p.render()
    ne = options.ne
    m = p.create_model(
                ne = ne,
                element = os.environ.get("Element", "ExactFrame"),
                section = os.environ.get("Section", "MixedFiber"),
                transform = os.environ.get("Transform", "Corotational02"),
                nen=2)

    p.analyze(model=m,
              Pmax=20 if options.length == 900 else 80,
              post=post)
    

    for post_ in post:
        post_.draw()


    for post_ in post:
        post_.finish()


    name = p.name + f"-ne{ne}"
    post[0].save_data(f"out/{name}.txt")


    # artist = veux.create_artist(m, vertical=3, model_config={
    #     "frame_shape": p.shape
    # })
    # artist.draw_sections()
    # artist.draw_sections(position=m.nodeDisp, rotation=m.nodeRotation)
    # veux.serve(artist)

    plt.show()