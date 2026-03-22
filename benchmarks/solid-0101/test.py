import numpy as np
import xara

def prescribe_homogeneous_strain(model, L,
                                 exx=0.0, eyy=0.0, ezz=0.0,
                                 gxy=0.0, gxz=0.0, gyz=0.0,
                                 series_tag=1, pattern_tag=1,
                                 times=(0.0, 1.0), path=(0.0, 1.0)):
    """
    Apply an affine displacement field corresponding to the given small-strain components
    using SP constraints scaled by a Path time series a(t) in [0,1].

    Parameters
    ----------
    L : float
        Cube side length.
    exx, eyy, ezz : float
        Normal strain components.
    gxy, gxz, gyz : float
        Engineering shear strains (gamma = 2*epsilon_offdiag).
    times : sequence of float
        Monotone times for the Path series.
    path : sequence of float
        Same length as `times`; scaling a(t) for the imposed displacements (0->1 ramp etc).
    """

    # Node coordinates (your numbering)
    coords = {
        1: (0.0, 0.0, 0.0),
        2: ( L , 0.0, 0.0),
        3: ( L ,  L , 0.0),
        4: (0.0,  L , 0.0),
        5: (0.0, 0.0,  L ),
        6: ( L , 0.0,  L ),
        7: ( L ,  L ,  L ),
        8: (0.0,  L ,  L ),
    }

    # Displacement field u = E x (using engineering shear)
    def u_at(x, y, z):
        ux = exx*x + 0.5*gxy*y + 0.5*gxz*z
        uy = 0.5*gxy*x + eyy*y + 0.5*gyz*z
        uz = 0.5*gxz*x + 0.5*gyz*y + ezz*z
        return ux, uy, uz

    # Time series and pattern
    model.timeSeries("Path", series_tag, time=list(times), values=list(path))
    model.pattern("Plain", pattern_tag, series_tag)

    # --- Kinematic boundary conditions for a uniform strain test ---
    # Lock the origin to remove rigid body motion
    model.fix(1, 1, 1, 1)  # node 1: u=v=w=0

    # Constrain minimal sets on the three edges through node 1,
    # and prescribe displacements elsewhere according to the affine field.
    #
    # Edge 1-2: keep v,w = 0 on node 2, prescribe u on node 2.
    # Edge 1-4: keep u,w = 0 on node 4, prescribe v on node 4.
    # Edge 1-5: keep u,v = 0 on node 5, prescribe w on node 5.
    #
    # Remaining nodes (3,6,7,8): prescribe all 3 components from the affine field.

    for nd, (x, y, z) in coords.items():
        ux, uy, uz = u_at(x, y, z)

        if nd == 1:
            # already fixed
            continue

        if nd == 2:
            # v=w fixed; prescribe u
            model.fix(2, 0, 1, 1)
            model.sp(2, 1, ux, series_tag)  # dof 1 = u
        elif nd == 4:
            # u=w fixed; prescribe v
            model.fix(4, 1, 0, 1)
            model.sp(4, 2, uy, series_tag)  # dof 2 = v
        elif nd == 5:
            # u=v fixed; prescribe w
            model.fix(5, 1, 1, 0)
            model.sp(5, 3, uz, series_tag)  # dof 3 = w
        else:
            # prescribe full vector
            model.sp(nd, 1, ux, series_tag)
            model.sp(nd, 2, uy, series_tag)
            model.sp(nd, 3, uz, series_tag)


def create_cube(L):

    # Build your model
    model = xara.Model(ndm=3, ndf=3)
    name = "GeneralizedJ2"
    model.material(name, 1, E=100.0, nu=0.3, Fy=15.0, Hiso=0.0, Hkin=0.0, delta=50.0, beta=10.0)

    # Nodes (your numbering)
    model.node(1, 0.0, 0.0, 0.0)
    model.node(2,  L , 0.0, 0.0)
    model.node(3,  L ,  L , 0.0)
    model.node(4, 0.0,  L , 0.0)
    model.node(5, 0.0, 0.0,  L )
    model.node(6,  L , 0.0,  L )
    model.node(7,  L ,  L ,  L )
    model.node(8, 0.0,  L ,  L )

    # Single 8-node brick
    model.element("bbarBrick", 1, (1,2,3,4,5,6,7,8), 1)
    return model 


def run_material_brick_test():
    L = 10.0
    model = create_cube(L)

    # Example history: combined gamma_xz(t) and epsilon_zz(t)
    #   gamma_xz ramps 0 -> 2% in 50 steps, then holds
    #   epsilon_zz ramps 0 -> -1% (compression) over the same 50 steps
    nsteps = 50
    times  = np.linspace(0.0, 1.0, nsteps+1).tolist()
    path   = np.linspace(0.0, 1.0, nsteps+1).tolist()

    gxz_final = 0.02     # 2% engineering shear
    ezz_final = -0.01    # 1% axial compression

    prescribe_homogeneous_strain(model, L,
                                 exx=0.0, eyy=0.0, ezz=ezz_final,
                                 gxy=0.0, gxz=gxz_final, gyz=0.0,
                                 series_tag=1, pattern_tag=1,
                                 times=times, path=path)

    # Basic static analysis setup
    model.system("FullGeneral")
    model.numberer("Plain")
    model.constraints("Plain")
    model.integrator("LoadControl", 1.0/len(path[1:]))
    model.algorithm("Newton")
    model.analysis("Static")

    # Optional: record element stress/strain at Gauss points if your API exposes it
    # (pseudo-API shown; adjust to your recorder interface)
    # model.recorder("Element", "-ele", 1, "-time", "-file", "elem1_stress.out", "stress")
    # model.recorder("Element", "-ele", 1, "-time", "-file", "elem1_strain.out", "strain")

    ok = model.analyze(len(path)-1)
    if ok != 0:
        raise RuntimeError(f"analysis failed with code {ok}")

    return model
