import opensees.openseespy as ops

def frame_cantilever(element, nu):
    pass

def solid_cantilever(element, nu):
    model = ops.Model(ndm=3, ndf=3)
    model.material("ElasticIsotropic", 1, 100.0, nu)
    L  = 5
    nz = 6
    nx = 2
    ny = 2

    nn = int((nz+1)*(nx+1)*(ny+1))

    # mesh generation
    model.block3D((nx, ny, nz), 1, 1, element, 1, {
                  1: [-1.0, -1.0,  0.0],
                  2: [ 1.0, -1.0,  0.0],
                  3: [ 1.0,  1.0,  0.0],
                  4: [-1.0,  1.0,  0.0],
                  5: [-1.0, -1.0,   L ],
                  6: [ 1.0, -1.0,   L ],
                  7: [ 1.0,  1.0,   L ],
                  8: [-1.0,  1.0,   L ]})

    model.fixZ(0.0, (1, 1, 1))


def plane_cantilever(element, nu):
    model = ops.Model(ndm=2, ndf=2)
    model.material("ElasticIsotropic", 1, 100.0, nu)

