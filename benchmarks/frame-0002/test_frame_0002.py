import xara
import jax
from xara.para import ParaModel
from xara.auto import NodalValue as StaticAnalysis
import pytest


def _section_properties(tw, hw, bf, tf):
    # Area and moment of inertia
    A = tw * (hw - 2 * tf) + 2 * bf * tf
    I = tw * (hw - 2 * tf)**3/12.0 + 2*bf*tf*(0.5 * (hw - tf))**2
    return A, I


def _is_close(a, b, tol=1e-6):
    return abs(a - b) < tol


def test_old_prism():
    """
    """
    # Input [N, m, kg, sec]
    L = 5.0              # Total length of cantilever
    H = 300000.0         # Lateral point load
    P = 0.0              # Axial force
    w = 10000.0          # Distributed load
    E = 200e9            # Modulus of elasticity
    nu = 0.3
    G = E / (2 * (1 + nu))
    
    hw = 0.355           # Web height
    bf = 0.365           # Flange width
    tf = 0.018           # Flange thickness
    tw = 0.011           # Web thickness

    nel = 1

    # Area and moment of inertia
    A, Iz = _section_properties(tw, hw, bf, tf)

    Ay =  A*1e5
    Az =  A*1e5

    # Iz = I
    Iy = Iz #2*(bf**3*tf/12.0) + tw**3*(hw-2*tf)/12.0
    J  = Iy + Iz

    # Create the model
    model = xara.Model(ndm=3, ndf=6)


    # Define nodes
    model.node(1, (0, 0, 0))
    model.node(2, (L, 0, 0))
    model.fix(1,  (1, 1, 1, 1, 1, 1))

    # Configure material and element properties
    model.section("FrameElastic", 1, *model.symbols(
                  E=E, 
                  A=A, 
                  Ay=Ay, 
                  Az=Az, 
                  Iz=Iz, 
                  Iy=Iy, 
                  J=J,
                  G=G
    ))
    model.geomTransf("Linear", 1, (0, 0, 1))
    # Create the frame element
    model.element("PrismFrame", 1, (1, 2), section=1, transform=1)

    # Define parameters
    model.parameter(1, "element", 1, "E")
    model.parameter(2, "element", 1, "A")
    model.parameter(3, "element", 1, "Iz")
    model.parameter(4, "node", nel+1, "coord", 1)

    model.pattern("Plain", 1, "Linear")
    model.load(2, (0.0, 1.0, 0.0, 0.0, 0.0, 0.0), pattern=1)


    model.constraints("Plain")
    model.system("ProfileSPD")

    if True:

        Pmax = H
        Nsteps = 1
        dP = Pmax / Nsteps

        model.integrator("LoadControl", dP)
        model.analysis("Static")


        model.sensitivityAlgorithm("-computeAtEachStep")

        model.analyze(1)
        print(model.nodeDisp(2, 2), model.getLoadFactor(1))

        for param in model.getParamTags():
            print("\t", param, model.sensNodeDisp(2, 2, param))

        assert _is_close(model.nodeDisp(2, 2), H*L**3/(3*E*Iy))
        assert _is_close(model.sensNodeDisp(2, 2, 1), -H*L**3/(3*E**2*Iy))
        assert _is_close(model.sensNodeDisp(2, 2, 2), 0)
        assert _is_close(model.sensNodeDisp(2, 2, 3), -H*L**3/(3*E*Iy**2))
        assert _is_close(model.sensNodeDisp(2, 2, 4), H*L**2/(E*Iy))

    if False:
        model.wipeAnalysis()

        Umax = 2.2
        Nsteps = 100
        Uincr = Umax/Nsteps

        model.integrator("DisplacementControl",2,2,Uincr)
        model.analysis("Static")

        model.sensitivityAlgorithm("-computeAtEachStep")

        for i in range(Nsteps):
            model.analyze(1)
            print(model.nodeDisp(2,1), model.getLoadFactor(1))
            for param in model.getParamTags():
                print(param, model.sensLambda(1, param))
    #           print(param, model.sensNodeDisp(2, 1, param))



def test_old_force():
    """
    """
    # Input [N, m, kg, sec]
    L = 5.0              # Total length of cantilever
    H = 300.0         # Lateral point load
    P = 0.0              # Axial force
    w = 10000.0          # Distributed load
    E = 200e3            # Modulus of elasticity
    nu = 0.3
    G = E / (2 * (1 + nu))
    
    hw = 0.355           # Web height
    bf = 0.365           # Flange width
    tf = 0.018           # Flange thickness
    tw = 0.011           # Web thickness

    nel = 1

    # Area and moment of inertia
    A, I = _section_properties(tw, hw, bf, tf)

    Ay =  A*1e5
    Az =  A*1e5

    Iy = I
    Iz = I #2*(bf**3*tf/12.0) + tw**3*(hw-2*tf)/12.0
    J  = Iz + Iy

    # Create the model
    model = xara.Model(ndm=3, ndf=6)


    # Define nodes
    model.node(1, (0, 0, 0))
    model.node(2, (L, 0, 0))
    model.fix(1,  (1, 1, 1, 1, 1, 1))

    # Configure material and element properties
    model.section("Elastic", 1, *model.symbols(
                  E=E, 
                  A=A, 
                #   Ay=Ay, 
                #   Az=Az, 
                  Iz=Iz, 
                  Iy=Iy, 
                  J=J,
                  G=G
    ))
    model.geomTransf("Linear", 1, (0, 0, 1))
    # Create the frame element
    model.element("ForceFrame", 1, (1, 2), section=1, transform=1, shear=0)

    # Define parameters
    model.parameter(1, "element", 1, "allSections", "E")
    model.parameter(2, "element", 1, "allSections", "A")
    model.parameter(3, "element", 1, "allSections", "Iz")
    model.parameter(4, "node", nel+1, "coord", 1)

    model.pattern("Plain", 1, "Linear")
    model.load(2, (0.0, 1.0, 0.0, 0.0, 0.0, 0.0), pattern=1)

    # model.print(json="/dev/stdout")
    model.constraints("Plain")
    model.system("ProfileSPD")

    if True:

        Pmax = H
        Nsteps = 1
        dP = Pmax / Nsteps

        model.integrator("LoadControl", dP)
        model.analysis("Static")


        model.sensitivityAlgorithm("-computeAtEachStep")

        model.analyze(1)
        print(model.nodeDisp(2, 2), model.getLoadFactor(1))

        for param in model.getParamTags():
            print("\t", param, model.sensNodeDisp(2, 2, param))

        assert model.nodeDisp(2, 2) == pytest.approx(H*L**3/(3*E*I))
        dE = model.sensNodeDisp(2, 2, 1)
        dL = model.sensNodeDisp(2, 2, 4)
        dA = model.sensNodeDisp(2, 2, 2)
        dI = model.sensNodeDisp(2, 2, 3)
        assert dL == pytest.approx( H*L**2/(E*I), rel=1e-3)
        assert dE == pytest.approx(-H*L**3/(3*E**2*I), rel=1e-3)
        assert dA == pytest.approx(0)
        assert dI == pytest.approx(-H*L**3/(3*E*I**2))





def test_new():
    L = 5.0
    H = 300e3  # Load applied at the top node

    # Model factory (pure builder, no analysis)
    def create_model(L, E, A, Iz):

        H = 300e3  # Load applied at the top node

        nu = 0.3
        G  = E / (2 * (1 + nu))
        Ay =  A*1e5
        Az =  A*1e5
        J  = 2*Iz # NOTE: J turns into a regular float, not a Parameter?

        m = ParaModel(ndm=3, ndf=6, parameters=4)

        m.node(1,  (0,0,0))
        m.node(2,  (L,0,0))
        m.fix( 1,  (1,1,1,1,1,1))

        m.section("FrameElastic",1,
                    E=E, A=A, Ay=Ay, Az=Az,
                    Iz=Iz, Iy=Iz, J=J, G=G)

        m.geomTransf("Linear", 1,(0,0,1))

        m.element("PrismFrame", 1, (1,2),
                section=1,
                transform=1)#, shear=1)


        m.pattern("Plain", 1, "Linear")
        m.load(2, (0.0, H,0.0,0.0,0.0,0.0), pattern=1)

        m.constraints("Plain")
        m.system("ProfileSPD")
        m.integrator("LoadControl", 1)
        m.analysis("Static")
        return m




    # Physical Parameters
    E  = 200e9           # Young's modulus
    hw = 0.355           # Web height
    bf = 0.365           # Flange width
    tf = 0.018           # Flange thickness
    tw = 0.011           # Web thickness

    # Derived Parameters
    A, I = _section_properties(tw, hw, bf, tf)

    # Bind function for node=2,dof=2
    g = StaticAnalysis(create_model,
                       output=(2, 2))


    uy   = g(L,E,A,I)  
    print("uy =", uy)


    #
    # Gradients
    #
    dg = jax.grad(g, (0,1,2,3))
    dL, dE, dA, dI = dg(L,E,A,I)
    print("∂g/∂L =", dL)
    print("∂g/∂E =", dE)
    print("∂g/∂A =", dA)
    print("∂g/∂I =", dI)
    print()


    #
    # Chain Rule
    #
    def h(L, E, tw, hw, bf, tf):
        A, I = _section_properties(tw, hw, bf, tf)
        return g(L, E, A, I)

    dh = jax.grad(h, (0,1,2,4))
    dL, dE, dtw, dhw = dh(L, E, tw, hw, bf, tf)
    print("∂h/∂E  =",  dE)
    print("∂h/∂tw =",  dtw)
    print("∂h/∂hw  =", dhw)

    assert _is_close(uy,  H*L**3/(3*E*I))
    assert _is_close(dE, -H*L**3/(3*E**2*I))
    assert _is_close(dA, 0)
    assert _is_close(dI, -H*L**3/(3*E*I**2))
    assert _is_close(dL, H*L**2/(E*I))
