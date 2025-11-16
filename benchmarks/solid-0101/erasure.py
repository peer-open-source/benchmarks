
# Auricchio, F., and R.L. Taylor. 
#   “Two Material Models for Cyclic Plasticity: Nonlinear Kinematic Hardening and Generalized Plasticity.” 
#   International Journal of Plasticity 11, no. 1 (1995): 65–98. 
#   https://doi.org/10.1016/0749-6419(94)00039-5.

import numpy as np
import xara


class Block:
    def __init__(self,  length: float):
        L = length
        self.nodes = {
            1:(0.0,0.0,0.0), 2:(L,0.0,0.0), 3:(L,L,0.0), 4:(0.0,L,0.0),
            5:(0.0,0.0,L),   6:(L,0.0,L),   7:(L,L,L),   8:(0.0,L,L)
        }
        self.width = L
        self.depth = L
        self.height = L


# Displacement field u = E x (using engineering shear)
def create_field(exx=0, eyy=0, ezz=0, gxy=0, gxz=0, gyz=0):
    E = [exx, eyy, ezz, gxy, gxz, gyz]
    n = 0
    for i,e in enumerate(E):
        if isinstance(e, (list, tuple, np.ndarray)):
            n = len(e)
            for j in range(len(E)):
                if j == i:
                    continue
                elif  np.isscalar(E[j]):
                    E[j] = np.full(n, E[j], dtype=float)
                elif len(E[j]) != n:
                    raise ValueError("all non-scalar strain components must have the same length")
            break
    
    exx, eyy, ezz, gxy, gxz, gyz = E

    def u(x, y, z):
        ux =     exx*x + 0.5*gxy*y + 0.5*gxz*z
        uy = 0.5*gxy*x +     eyy*y + 0.5*gyz*z
        uz = 0.5*gxz*x + 0.5*gyz*y +     ezz*z
        print(ux, uy, uz)
        return np.array([ux, uy, uz])
    return u


def apply_shear_axial_histories(block, model,
                                shear_hist, axial_hist, 
                                base_series_tag=100):
    """
    Superpose independent γxz(t) and εzz(t) histories on the cube using per-DOF Path series.
    """


    def u_from_unit_shear(x, y, z):  # γxz = 1
        return 0.5*z, 0.0, 0.5*x

    def u_from_unit_axial(x, y, z):  # εzz = 1
        return 0.0, 0.0, z

    t_s, g_s = map(np.array, zip(*shear_hist))
    t_a, e_a = map(np.array, zip(*axial_hist))
    times    = np.unique(np.concatenate([t_s, t_a]))
    gamma_xz = np.interp(times, t_s, g_s)
    eps_zz   = np.interp(times, t_a, e_a)

    # prescribe SPs on every DOF exactly once

    series_tag = base_series_tag + 1

    def add_sp_series(node, dof, values):
        nonlocal series_tag
        model.timeSeries("Path", series_tag,
                         time=times.tolist(),
                         values=np.asarray(values, dtype=float).tolist())
        # Activate a Plain pattern that uses this time series
        model.pattern("Plain", series_tag, series_tag)
        # Add the SP while this pattern is active (no pattern arg on sp)
        model.sp(node, dof, 1.0, pattern=series_tag)
        series_tag += 1

    # Prescribe all 3 DOFs at all nodes
    u_s = create_field(gxz=gamma_xz)
    u_a = create_field(ezz=eps_zz)
    for nd, xn in block.nodes.items():
        (x, y, z) = xn
        u = u_s(*xn) + u_a(*xn)
        # ux_s, uy_s, uz_s = u_from_unit_shear(x, y, z)
        # ux_a, uy_a, uz_a = u_from_unit_axial(x, y, z)

        add_sp_series(nd, 1, u[0]) #ux_s*gamma_xz + ux_a*eps_zz)
        add_sp_series(nd, 2, u[1]) #uy_s*gamma_xz + uy_a*eps_zz)
        add_sp_series(nd, 3, u[2]) #uz_s*gamma_xz + uz_a*eps_zz)

    return times


def test_erasure(name = "GeneralizedJ2"):
    block = Block(length=10.0)

    model = xara.Model(ndm=3, ndf=3)

    model.material(name, 1, E=100.0, nu=0.3, Fy=15.0,
                   Hiso=0.0,
                   Hkin=0.0,
                   Hsat=50.0,
                   Fs=25.0)

    for i,(x,y,z) in block.nodes.items():
        model.node(i, x, y, z)

    model.element("bbarBrick", 1, (1,2,3,4,5,6,7,8), 1)


    #
    # Loading
    #
    # engineering strain for shear γxz, and axial εzz
    shear = [(0,0), (1,1.2), (3,-1.2), (5,1.2), (6,0), (7,1.2), (9,-1.2), (11,1.2), (12,0), (13,1.2)]
    axial = [(0,0), (5,0), (6,0.7), (7,0), (11,0), (12,0.7), (13,0)]

    times = apply_shear_axial_histories(block, model, shear_hist=shear, axial_hist=axial)

    # Static analysis over the merged time grid
    nstep = 1000

    model.system("FullGeneral")
    model.numberer("Plain")
    model.constraints("Transformation")
    model.test("Residual", 1e-12, 10, 1)
    model.integrator("LoadControl", max(times)/nstep)
    model.algorithm("Newton")
    model.analysis("Static")


    tau = []   # shear stress history
    sig = []   # axial stress history
    gam = []   # shear strain history
    eps = []   # axial strain history
    for _ in range(nstep):
        if model.analyze(1) != 0:
            raise RuntimeError(f"analysis failed at step {_+1}")
        # Get stress at element 1 integration point 1
        s = model.eleResponse(1, "stress", 1)
        tau.append(s[5])
        sig.append(s[2])
        # Get strain at element 1 integration point 1
        e = model.eleResponse(1, "strains", 1)
        gam.append(e[5])
        eps.append(e[2])

    return tau,sig,gam,eps


if __name__ == "__main__":
    tau,sig,gam,eps = test_erasure("J2") #"J2Simplified")

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2,1)
    ax[0].plot(eps, sig)
    ax[0].set_ylabel(r'$\sigma_{zz}$')
    ax[0].set_xlabel(r'$\varepsilon_{zz}$')
    ax[1].plot(gam, tau)
    ax[1].set_ylabel(r'$\sigma_{xz}$')
    ax[1].set_xlabel(r'$\gamma_{xz}$')
    plt.show()
