
# With about 20,000 CST triangles:
#   J = 0.000122176208309753

from xsection.library import WideFlange


def ApproxWideFlange(shape):
    tf = shape.tf
    tw = shape.tw
    bf = shape.bf
    d = shape.d

    Iw = tf*(d-tf)**2*bf**3/24
    J  = 1/3*((d-2*tf)*tw**3  +  2*tf**3*bf)

    print(f"{J  = }")
    print(f"{Iw = }")
    return J,Iw

if __name__ == "__main__":
    shape = WideFlange(
            d = 1,
            b = 1,
            tf = 0.05,
            tw = 0.05,
            mesh_scale=1/10000
    )
    J = shape._analysis.torsion_constant()
    Iw = shape.cww()[0,0]
    print(f"{J  = }")
    print(f"{Iw = }")

    J, Iw = ApproxWideFlange(shape)

    E = 1e6
    nu = 0.3
    G = E/(2*(1+nu))

    L = 5
    print(L/(G*J))

