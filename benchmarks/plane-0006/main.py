#
# 
#
import xara
import veux
from xara.units.iks import kip, inch, foot, ksi
from xara.helpers import find_node, find_nodes
from veux.stress import node_average
from scipy.spatial.distance import euclidean as distance
import matplotlib.pyplot as plt
try:
    plt.style.use("veux-web")
except:
    pass


class PlanePrism:
    def __init__(self,
                 length,
                divisions,
                material,
                depth, width,
                order=1,
                element: str = "LagrangeQuad"):

        self.length = length
        self.divisions = divisions
        self.material = material
        self.order = order
        self.thickness = width
        self.element = element
        self.depth = depth


    def create_model(self):
        # Define geometry
        # ---------------
        L = self.length
        element = self.element
        order = self.order
        material = self.material
        d = self.depth
        thick = self.thickness

        nx, ny = self.divisions

        #
        # Create model
        #
        # create model in two dimensions with 2 DOFs per node
        model = xara.Model(ndm=2, ndf=2)

        # Define the material
        # -------------------
        #                                 tag
        model.material("ElasticIsotropic", 1, **material)
        model.section("PlaneStress", 1, 1, thick)

        # now create the nodes and elements using the surface command
        # {"quad", "enhancedQuad", "tri31", "LagrangeQuad"}:


        mesh = model.surface((nx, ny),
                    element=element,
                    args={"section": 1},
                    order=order,
                    points={
                        1: [  0.0,   0.0],
                        2: [   L,    0.0],
                        3: [   L,     d ],
                        4: [  0.0,    d ]
                })


        # Single-point constraints
        boundary = ((1,1,1, 1,1,1),
                    (1,1,1, 1,1,1))

        # for x, dofs in zip((0, L), boundary):
        #     for i, dof in enumerate(dofs):
        #         if dof:
        #             for node in find_nodes(mesh, x=x):
        #                 model.fix(node, dof=i+1)

        for node in find_nodes(model, x=0):
            model.fix(node, (1, 1))

        for node in find_nodes(model, x=L):
            model.fix(node, (1, 1))


        model.mesh = mesh
        return model



def analyze(prism, model, w):
    L = prism.length
    d = prism.depth

    # Define gravity loads
    # create a Plain load pattern with a linear time series
    model.pattern("Plain", 1, "Linear")

    # Load all nodes with y-coordinate equal to `d`
    for nodes in model.mesh.walk_edge():
        # skip edges that arent on the top
        if abs(model.nodeCoord(nodes[0], 2) -d) < 1e-10:
            continue
        if abs(model.nodeCoord(nodes[-1], 1) -L) < 1e-10:
            continue
        if abs(model.nodeCoord(nodes[0], 1)) < 1e-10:
            continue

        # Edge length
        Le = distance(model.nodeCoord(nodes[0]), model.nodeCoord(nodes[-1]))

        if order == 1:
            model.load(nodes[0], (0,   w*Le/2), pattern=1)
            model.load(nodes[1], (0,   w*Le/2), pattern=1)
        elif order == 2:
            model.load(nodes[0], (0,   w*Le/6), pattern=1)
            model.load(nodes[1], (0, 2*w*Le/3), pattern=1)
            model.load(nodes[2], (0,   w*Le/6), pattern=1)

    #
    # Run Analysis
    #
    model.integrator("LoadControl", 1.0)
    model.analysis("Static")
    model.analyze(1)

    #
    # Beam theory solution
    #

    xn = [
         model.nodeCoord(node,1) for node in find_nodes(model, y=d/2)
    ]

    um = [
         model.nodeDisp(node, 2) for node in find_nodes(model, y=d/2)
    ]

    material = prism.material
    nu    = material["nu"]
    E     = material["E"]
    d     = prism.depth
    thick = prism.thickness
    A = thick*d
    k = 5/6
    I = thick*d**3/12
    G = E / (2 * (1 + nu))
    uy = lambda x: w*x**2/(24*E*I)*(L - x)**2 - w/(k*G*A)*L**2/24*(1 - 12*x/L + 12*(x/L)**2) + w*L**2/(24*G*A*k)
    ue = [uy(x) for x in xn]

#   model.reactions()
#   print(sum(model.nodeReaction(node, 2) for node in model.getNodeTags()))

    return xn, um, ue




if __name__ == "__main__":
    fig, ax = plt.subplots()
    L = 240.0*inch

    material = dict(
        E  = 4000.0*ksi,
        nu = 0.25
    )
    load = -20.0*kip
    w = load/L
    for order in 1,2:
        # model, xn, um, ue = create_beam((40,8), element="quad", order=order)
        prism = PlanePrism(
            divisions=(12,4),
            length=L,
            depth = 24.0*inch,
            width = 1.0*inch,
            material=material,
            element="quad", 
            order=order
        )

        model = prism.create_model()
        xn, um, ue =  analyze(prism, model, w)
        ax.plot(xn, um, ":", label=f"FEA ({order = })")

    ax.plot(xn, ue, label="Beam theory")

    ax.set_xlabel("Coordinate, $x$")
    ax.set_ylabel("Deflection, $u_y$")
    ax.legend()
    # plt.savefig("img/beam_solution.png", dpi=300)
    plt.show()


    artist = veux.create_artist(model, canvas="gltf")

    stress = {node: stress["sxx"] for node, stress in node_average(model, "stressAtNodes").items()}

    artist.draw_nodes()
    artist.draw_outlines()
    artist.draw_surfaces(state=model.nodeDisp, scale=50, field=stress)
#   artist.draw_surfaces(field = stress)
    artist.draw_outlines(state=model.nodeDisp, scale=50)
    veux.serve(artist)


#       print(model.nodeDisp(l2))
