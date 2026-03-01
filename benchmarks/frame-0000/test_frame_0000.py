import xara

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
        return 
    
    raise Exception("Expected error not raised")

