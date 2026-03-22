import sys
import veux
import xara
import numpy as np
import xara.units.iks as units
from xsection.library import WideFlange



if __name__ == "__main__":
    # os.environ["Wagner"] = "1"
    import sys 


    Fy = 41.3*units.ksi #36.2594*units.ksi # 
    E  = 29e3*units.ksi
    # Fy = 250*units.MPa
    # E  = 200e3*units.GPa
    nu = 0.29 #7 # 0.25
    G  = E/(2*(1+nu))
    print(f"{Fy = }")


    material = xara.Material(
        E  = E,
        nu = nu,
        Fy = Fy,
        # Hiso = 0.001 * E,
        Hkin = 0.03 * E,#900*units.ksi, #
        type = "J2BeamThread" #  "NonlinearJ2" #  "J2" # "GeneralizedJ2" # "J2Simplified" #
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

    veux.draw_shape(shape).show()