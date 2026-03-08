import xara
import pytest

def _test_constructors():
    # From SAP2000 1-0014a
    A  = 216
    Iz = 2592
    Iy = 5832
    J = 6085.1201362
    E = 3600
    G = 1500
    L = 96.0
    m = 4.968e-05

    def add_element(model, syntax):
        match syntax:
            case "a":
                model.element("ForceFrame", 1, 
                              (1, 2), 
                              section=1, 
                              transform=1, 
                              shear=0,
                              mass=m, 
                              n=8, 
                              gauss_type="Legendre"
                )


    for syntax in {"a"}:
        model = xara.Model(ndm=3, ndf=6)
        i,j = 1,2
        model.node(i, 0,0,0)
        model.node(j, L,0,0)
        model.fix(i, 1,1,1,1,1,1)
        model.fix(j, 1,0,0,1,0,0)
        # model.section("Elastic", 1, E=E, A=A, Iz=Iz, Iy=Iy, G=G, J=J)
        model.section("ElasticFrame", 1, E=E, A=A, Iz=Iz, Iy=Iy, G=G, J=J, Ay=A, Az=A)
        model.geomTransf("Linear", 1, (0,0,1))

        add_element(model, syntax)


        model.print(json="/dev/stdout")

        model.constraints("Transformation")
        model.system("BandGeneral")
        # model.analysis("Static")
        ev = model.eigen(2)#, solver="-genBandArpack")

        assert len(ev) == 2
        assert ev[0] == pytest.approx(13268.512, rel=1e-6), ev[0]
        assert ev[1] == pytest.approx(29854.153, rel=1e-6), ev[1]



def test_transform():
    """
    Ensure graceful handling of invalid geometric transformation vectors 
    in 3D frame elements.
    This segfaults upstream.
    """
    # Set up the model
    model = xara.Model(ndm=3, ndf=6)

    model.node(1, 0, 0, 0)
    model.node(2, 0, 5, 0)
    model.node(3, 0, 5, 5)

    fixed = 6 * [1]
    model.fix(1, *fixed)

    # Define geometry transforms
    model.geomTransf("Linear", 1, (-1, 0, 0))
    model.geomTransf("Linear", 2, ( 0, 0, 1))             # <---- note subtly wrong vecxz

    # Some reasonable properties (~300x600mm RC)
    A, E, G, J, Iz, Iy = 0.18, 30e9, 12e9, 0.01, 0.005, 0.005

    model.section("ElasticFrame", 1, E=E, A=A, Iz=Iz, Iy=Iy, G=G, J=J)
    # define elements
    ele_type = "PrismFrame"
    # tag *[ndI ndJ]  A  E  G  Jx  Iy   Iz  transfOBJs
    #osp.element(ele_type, 1, (1, 2), A, E, G, J, Iz, Iy, 1)
    #osp.element(ele_type, 2, (2, 3), A, E, G, J, Iz, Iy, 2)           # <-- crashes

    ele_type = "forceBeamColumn"
    model.element(ele_type, 1, (1, 2), section=1, transform=1)
    try:
        model.element(ele_type, 2, (2, 3), section=1, transform=2)           # <-- crashes
    except:
        model.wipe()
        return 
    
    raise Exception("Expected error not raised")



# if __name__ == "__main__":
#     test_constructors()