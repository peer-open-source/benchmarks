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
import matplotlib.pyplot as plt


if __name__ == "__main__":
    from model import Problem
    # Good:
    #   1032-D-D-n-fiber-force-02-wagner0-displacements.png
    
    p = Problem(origin  = os.environ.get("Origin", "O"),
                warp_base=os.environ.get("Warping", "n") # "f", "r", "n"
            )
    
    # p.render()

    m = p.create_model(
                ne = 30,
                element = os.environ.get("Element", "ExactFrame"),
                section = os.environ.get("Section", "ShearFiber"),
                transform = os.environ.get("Transform", "Corotational02"),
                nen=2)
    p.analyze(model=m)

    plt.show()