import opensees.openseespy as osp

# Set up the model
osp.wipe()
osp.model("basic", "-ndm", 3)

osp.node(1, 0, 0, 0)
osp.node(2, 0, 5, 0)
osp.node(3, 0, 5, 5)

fixed = 6 * [1]
osp.fix(1, *fixed)

# Define geometry transforms
osp.geomTransf("Linear", 1, (-1, 0, 0))
osp.geomTransf("Linear", 2, ( 0, 0, 1))             # <---- note subtly wrong vecxz

# Some reasonable properties (~300x600mm RC)
A, E, G, J, Iz, Iy = 0.18, 30e9, 12e9, 0.01, 0.005, 0.005

osp.section("ElasticFrame", 1, E=E, A=A, Iz=Iz, Iy=Iy, G=G, J=J)
# define elements
ele_type = "PrismFrame"
# tag *[ndI ndJ]  A  E  G  Jx  Iy   Iz  transfOBJs
#osp.element(ele_type, 1, (1, 2), A, E, G, J, Iz, Iy, 1)
#osp.element(ele_type, 2, (2, 3), A, E, G, J, Iz, Iy, 2)           # <-- crashes

ele_type = "forceBeamColumn"
osp.element(ele_type, 1, (1, 2), section=1, transform=1)
osp.element(ele_type, 2, (2, 3), section=1, transform=2)           # <-- crashes



#osp.analysis("Static")
#osp.analyze(1)
