import xara
import jax
jax.config.update("jax_enable_x64", True)
from xara.para import ChainModel
from xara.auto import StaticAnalysis, Array
import jax.numpy as np

import pytest


nx, ny = 3,3
nc = 1

L = 10.0
H = 300  # Load applied at the top node
nu = 0.3

def _test_bwd():
    from xsection.library._rectangle import create_core_fibers, create_core_mesh
    from xsection.analysis.xvenant import venant_warping

    # Model factory
    def create_model(L, E, 
                     fibers: Array[:, ("y", "z", "area", "wx", "wxy", "wxz", "wy", "wyy", "wyz", "wz", "wzy", "wzz")],
        ):

        m = ChainModel(ndm=3, ndf=6, parameters=2+len(fibers)*3)

        m.node(1,  (0,0,0))
        m.node(2,  (L,0,0))
        m.fix( 1,  (1,1,1,1,1,1))

        m.material("ElasticIsotropic", 1, E, nu)

        m.section("ShearFiber", 1, mixed_type="None")
        for fiber in fibers:
            m.fiber(*fiber, material=1, section=1)


        m.geomTransf("Linear", 1,(0,0,1))

        m.element("ForceFrame", 1, (1,2),
                section=1,
                transform=1, shear=1)


        m.pattern("Plain", 1, "Linear")
        m.load(2, (0.0,0,H, 0.0,0.0,0.0), pattern=1)

        m.constraints("Plain")
        m.system("ProfileSPD")
        m.integrator("LoadControl", 1)
        m.analysis("Static")
        return m


    # Physical Parameters
    E  = 200e6           # Young's modulus
    G  = E / (2 * (1 + nu))
    d  = 0.35           # Web height
    b  = 0.35           # Flange width
    c  = 0.25*d # cover
    
    Iy = d**3 * b / 12.0
    Iz = b**3 * d / 12.0
    A  = d * b

    mesh = create_core_mesh((b, d, c), (nx, ny, nc))
    fibers = create_core_fibers(mesh)

    print("A = " + str(A))
    print("As = " + str(sum(fiber[2] for fiber in fibers)))

    print("Iy = " + str(Iy))
    print("Iyf = " + str(sum(fiber[2]*fiber[1]**2 for fiber in fibers)))
    print("Iz = " + str(Iz))
    print("Izf = " + str(sum(fiber[2]*fiber[0]**2 for fiber in fibers)))

    # Bind function for node=2,dof=3
    analyze_1 = StaticAnalysis(create_model, output=(2, 3))

    uy   = analyze_1(L,E, fibers)  
    print("uy =", uy)


    #
    # Chain Rule
    #
    def analyze_2(L, E, d, b):
        mesh = create_core_mesh((b, d, c), (nx, ny, nc), (E, E*0.5, nu))
        fibers, materials = create_core_fibers(mesh)
        warp = np.zeros((len(fibers), 3, 3))
        fibers = np.concatenate((fibers, warp), axis=1)
        return analyze_1(L, E, fibers, materials)

    du = jax.jacrev(analyze_2, (0,1,2,3))
    dL, dE, dh, db = map(float,du(L, E, d, b))
    print("∂u/∂E  =",  dE)
    print("∂u/∂h =",  dh)
    print("∂u/∂b  =", db)

    dI = -H*L**3/(3*E*Iy**2)
    dA = -H*L/(G*A**2)
    dIdh, dIdb = jax.grad(lambda d, b: b*d**3/12.0, (0,1))(d,b)
    dAdh, dAdb = jax.grad(lambda d, b: b*d, (0,1))(d,b)

    # dudI = -H*L**3/(3*E*I**2)
    # dudA = -H*L/(G*A**2)
    assert uy == pytest.approx(H*L**3/(3*E*Iy) + H*L/(G*A))
    assert dh == pytest.approx(dIdh*dI + dAdh*dA, rel=1e-3)
    assert db == pytest.approx(dIdb*dI + dAdb*dA, rel=1e-3)
    assert dL == pytest.approx(H*L**2/(E*Iy) + H/(G*A), rel=1e-3)
    assert dE == pytest.approx(-H*L**3/(3*E**2*Iy)- (H*L/(G**2*A))*G/E, rel=1e-3)# 


if __name__ == "__main__":
    _test_bwd()
