import sys
import veux
import numpy as np
from xsection.library import from_aisc, aisc_data, WideFlange
from xsection.analysis.interaction import limit_surface, plot_limit_surface


def wide_flange_cowper(shape: WideFlange, nu=0.3):
    b  = shape.bf
    tf = shape.tf
    tw = shape.tw
    d  = shape.d

    m = 2*b*tf/(d*tw)
    n = b/d
    return (10*(1+nu)*(1+3*m)**2)/((12 + 72*m + 150*m**2 + 90*m**3) + nu*(11+66*m + 135*m**2 + 90*m**3) + 30*n**2*(m + m**2) + 5*nu*n**2*(8*m+9*m**2))

def wide_flange_timoshenko(shape: WideFlange, nu=0.3):
    b  = shape.bf
    tf = shape.tf
    tw = shape.tw
    d  = shape.d
    A  = shape.area
    I  = shape.elastic.Iy
    return float(8*tw*I/(A*(b*d**2 - (b - tw)*(d - 2*tf)**2)))

def wide_flange_newlin(shape: WideFlange, nu=0.3):
    b  = shape.bf
    tf = shape.tf
    tw = shape.tw
    d  = shape.d
    A  = shape.area
    I  = shape.elastic.Iy
    d1 = d - 2*tf
    aw = A*b/(64*I**2)*(d1**5*(8*tw/(15*b)+b/tw-4/3)-d1**3*d**2*(2*b/tw-4/3)+d1*d**4*(b/tw))
    af = A*b/(64*I**2)*(-d1**5/5 + 2/3*d1**3*d**2 - d1*d**4 + 8/15*d**5)
    return float(1/(aw + af))


if __name__ == "__main__":
    c = "centroid"

    # "W14x48"
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "W18x40"
    shape = from_aisc(name, mesh_scale=1/20)
    d = shape.d

    print(shape.summary(shear=True))


    print("Cowper\t",     wide_flange_cowper(shape))
    print("Cowper\t",     wide_flange_cowper(shape, nu=0))
    print("Timoshenko\t", wide_flange_timoshenko(shape))
    print("Newlin\t",     wide_flange_newlin(shape))
    print("A/(d*tw)",     shape.depth*shape.tw/shape.elastic.A)

    Xr = shape._analysis.shear_factor_romano(nu=0.0)[0][1]
    print("Romano\t", Xr)


    print("tan(alpha): ", np.tan(shape._principal_rotation()))


    # 1) create basic section
#   basic = shape.linearize()

    field = shape._analysis.solve_shear()[1]

    # 3) view warping modes
    artist = veux.create_artist(shape.model, ndf=1, ndm=2)

    field = {node: (shape.depth/6)*value/max(field) for node, value in enumerate(field)}

    artist.draw_surfaces(field = field,
                         state=field
                         )
    artist.draw_outlines()
    artist.draw_surfaces()
    R = artist._plot_rotation

#   artist.canvas.plot_vectors([[0,0,0] for i in range(3)], d/5*R.T, extrude=True)
#   artist.canvas.plot_vectors([R@[*shape._analysis.shear_center(), 0] for i in range(3)], d/5*R.T, extrude=True)
    artist.draw_outlines(state=field)
    veux.serve(artist)
