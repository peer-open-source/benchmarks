
from typing import Optional, Sequence
import numpy as np
from tqdm import tqdm
from xsection.analysis.venant import SaintVenantSectionAnalysis

class PlaneField:
    pass

_i = np.array([[1],[0],[0]], dtype=float)
_ix = np.array([[0,-1],[1,0]], dtype=float)

def _shear_poisson(r, rc, nu):
    devR = np.outer(r, r) - 0.5*np.dot(r, r)*np.eye(2)
    return -nu*(devR - np.outer(r, rc))

class _RigidMotion:
    def __init__(self,  iesan, trace=None):
        xu, xr = 0.0, 0.0
        u0 = np.zeros(3)
        self._b_theta = 0
        self.rotation = np.zeros(3)
        self.position = np.zeros(3)
        Xb = trace.shift_shear_gamma()
        if True:
            # x_gamma = trace.shift_shear_twist()
            # rho_psi = trace.iesan_center()
            # iesan_twist = iesan._c + iesan._ath
            # g = Xb.T@rho_psi + trace.shift_axial_twist()
            # lamda = ...
            # beta = np.dot(x_gamma, rho_psi) + lamda
            # twist = (iesan_twist - np.dot(g, np.linalg.solve(Xb, iesan._bv)))/(
            #     beta - np.dot(g, np.linalg.solve(Xb, x_gamma))
            # )
            # shear = np.linalg.solve(Xb, iesan._bv - x_gamma*twist)
            trace_soln = trace.solve(iesan.p)
            shear = trace_soln.gamma(xu)[1:]
            # self.rotation[ 0] = trace_soln.kappa(xu)[0]
            # self.rotation[0] = - trace_soln.rotation(xu)[0]
            self.rotation[1:] = _ix@shear

            # self.position[0] = trace_soln.gamma(xu)[0]

        else:
            self.rotation[1:] = _ix@np.linalg.solve(Xb,iesan._bv)

    def u(self, x, r=None):
        x = float(x)
        if r is None:
            r = [0,0]

        return np.cross(self.rotation, np.array([x, *r])) + self.position



class SaintVenant:
    """
    Minimal Saint-Venant beam helper tied to the notation in the provided notes.

    Coordinates/components:
      - x is the axial coordinate.
      - r = (y, z) are section coordinates.
    """

    def __init__(self,
                 shape,
                 length=None,
                 material=None,
                 N: float = 0.0,
                 M: list | tuple | None = None,
                 T: float = 0.0,
                 V: list | tuple | None = None,
                 root: float = 0.0,
                 sv=None,
                 imode="fiber"):
        """
        Parameters
        ----------
        shape : object
            Cross-section container. Expected attributes:
              - A : float                  (area)
              - E : float                  (Young's modulus)
              - G : float                  (Shear modulus)
              - centroid : (2,)                  (centroid coords, w.r.t chosen origin)
              - J : (2,2)                  (J_{αβ} = ∫ x_α x_β dA)
              - Jo : float                 (St-Venant torsion constant; only if T != 0)

        length : float
            Beam length h.
        N : float
            Axial force F3 (sign per your convention).
        M : (M1, M2)
            Bending resultants about section axes 1≡y and 2≡z.
        T : float
            Torsional resultant M3.
        V : (F1, F2)
            Transverse shear resultants.
        root : float
            x-location of the “fixed root”. Displacements are referenced so that
            u(x=root) = 0 (rigid offset removed).
        """
        if hasattr(shape, "length"):
            length = shape.length
            self.E = shape.material["E"]
            self.G = shape.material["G"]
            shape  = shape.shape
        else:
            if length is None:
                raise ValueError
            material = shape.material or material
            self.shape  = shape
            self.E = material["E"]
            self.G = material["G"]


        if sv is None:
            sv = SaintVenantSectionAnalysis(shape)#, nu=nu)

        nu = self.E/(2*self.G) - 1.0
        self._section_analysis = sv
        self._section_mesh = self._section_analysis._model
        self._nu = nu
        self.root   = float(root)
        self.length = float(length)


        # self.A = shape.elastic.A
        self.centroid = self._section_analysis.centroid()
        cmm = self._section_analysis.cmm(weight="e")[1:,1:]
        self.Jm  = _ix@cmm@_ix.T
        self.EJ = _ix@cmm@_ix.T #self._section_analysis.moment_tensor()# 
        self.GJ = self._section_analysis.twist_rigidity()
        self.EA = self._section_analysis.axial_rigidity()

        self._m_node_tree = None
        self._m_node_map = None
        self._warp_shear = self._section_analysis.solve_shear()
        self._warp_twist = self._section_analysis.solve_twist()

        # Resultants
        self.M = -np.array([(M or (0.0, 0.0))[0], (M or (0.0, 0.0))[1]])
        self.V = -np.array([(V or (0.0, 0.0))[0], (V or (0.0, 0.0))[1]])
        if root == 0:
            self.M[0] -= self.V[1]*self.length
            self.M[1] += self.V[0]*self.length


        # (P1) Solve Eq. (2-15) for a = (a1, a2, aε) and aθ
        self._aS, self._ae, self._ath = self._solve_p1(
            N=float(N), 
            M=self.M,
            T=float(T)
        )

        # (P2) Solve Eq. (2-18) for b = (b1, b2, bε)
        self._bv, self._be, self._c = self._solve_p2(self.V)
        self.p = [
            self._ae, 
            *self._aS, 
            self._ath+self._c, 
            *self._bv
        ]


    def _solve_p1(self, N: float, M: tuple[float, float], T: float) -> tuple[np.ndarray, float, float]:
        """
        Solve: 
          E*(J a + A r0 aε) = -i x M,  
          E*A (r0·a + aε) = -N,  
          G*Jo*aθ = -M3,
        (cf. Eq. (2-15)).
        """

        ixM = -_ix@M #np.array([M2, -M1], dtype=float)
        E  = self.E
        EA = self.EA

        top    = np.hstack((self.EJ, (EA * self.centroid).reshape(2, 1)))
        bottom = np.hstack(((EA * self.centroid).reshape(1, 2), np.array([[EA]])))
        A_sys  = np.vstack((top, bottom))
        b_sys  = np.array([*ixM, -N], dtype=float)

        sol = np.linalg.solve(A_sys, b_sys)
        aS = sol[:2]
        ae = float(sol[2])

        # Torsion parameter aθ
        ath = 0.0
        if self.G > 0.0 and self.GJ > 0.0:
            ath = - T / (self.GJ)  # from G*Jo*aθ = -M3

        return aS, ae, ath

    def _solve_p2(self, V: tuple[float, float]) -> tuple[np.ndarray, float]:
        """
        Solve: E*(J b + A r0 bε) = -V,  (r0·b + bε) = 0  (cf. Eq. (2-18)).
        Here bθ=0 automatically in this skeleton.
        """
        E  = self.E
        EA = self.EA

        V1, V2 = float(V[0]), float(V[1])
        rhs    = np.array([-V1, -V2])

        top    = np.hstack((self.EJ, (EA * self.centroid).reshape(2, 1)))
        bottom = np.hstack((self.centroid.reshape(1, 2), np.array([[1.0]])))
        A_sys  = np.vstack((top, bottom))
        b_sys  = np.concatenate((rhs, np.array([0.0])))

        sol = np.linalg.solve(A_sys, b_sys)
        bS = sol[:2]
        be = float(sol[2])


        # nu = self._nu
        rho_psi = self._section_analysis.iesan_center()
        c = np.dot(rho_psi, bS)
        # cmn = self.shape._analysis.shear_model(nu).cmn()
        # c  = -(cmn@[0,*bS])[0]/self.Jo
        return bS, be, c

    def _find_node(self, r: Sequence[float]) -> int:
        """
        Find the node number closest to section coords r = (y,z).
        """
        model = self._section_mesh
        if self._m_node_map is None:
            key_nodes = np.round(model.nodes, 8)
            self._m_node_map = {tuple(pt): i for i, pt in enumerate(key_nodes)}

        return self._m_node_map.get(tuple(np.round(r, 8)), None)
    
    def _node_tree(self):
        from scipy.spatial import KDTree
        if self._m_node_tree is None:
            model = self._section_mesh
            self._m_node_tree = KDTree(model.nodes)
        return self._m_node_tree

    # ------------------------------
    # Public API
    # ------------------------------

    def u(self, x: float, r: Optional[Sequence[float]] = None, n:int=None, trace=None) -> list[float]:
        """
        Return [u1, u2, ux] = [u_y, u_z, u_x] at (x, r), *relative to* u(x=root)=0.
        Only r=None (or r=(0,0)) is implemented.

        On-axis (r=0), the Saint-Venant contributions reduce to:
          P1: u_α = -(1/2) a_α x^2,   u_3 = aε x      (torsional warping cancels under root-anchoring)
          P2: u_α = -(1/6) b_α x^3,   u_3 = (1/2) bε x^2
        """
        if r is None and n is None:
            r = [0.0, 0.0]
        elif n is not None:
            r = self._section_mesh.nodes[n]
        r = np.array(r, dtype=float)

        x  = float(x)
        xr = self.root

        # (P1) extension + bending (torsion warping cancels under [u(x) - u(root)] at same r)
        ux_p1 = self._ae * (x - xr)
        u1_p1 = -0.5 * self._aS[0] * (x**2 - xr**2)
        u2_p1 = -0.5 * self._aS[1] * (x**2 - xr**2)
        u1 = np.array([ux_p1, u1_p1, u2_p1])

        # (P2) shear flexure (on-axis; c_i=0, c_θ terms drop out on-axis and under anchoring)
        ux_p2 =  0.5 * self._be * (x**2 - xr**2)
        u1_p2 = -(1.0/6.0) * self._bv[0] * (x**3- xr**3)
        u2_p2 = -(1.0/6.0) * self._bv[1] * (x**3- xr**3)
        u2 = np.array([ux_p2, u1_p2, u2_p2])

        if np.linalg.norm(r) > 0:
            model = self._section_mesh
            usvx = self._section_analysis.solve_twist()
            i = self._find_node(r)

            # mask = np.nonzero(np.all(np.isclose(model.nodes, r), axis=1))[0]
            # if mask.size == 0:
            if i is None:
                # usv = model.create_handle(self.shape._analysis.warping())(r)
                # usy = model.create_handle(self._sm._u[0])(r)
                # usz = model.create_handle(self._sm._u[1])(r)
                raise ValueError("Node not found")
            else:
                # i = mask[0]
                usv = usvx[i]
                usy = self._warp_shear[0][i]
                usz = self._warp_shear[1][i]

            nu = self._nu
            devR = np.outer(r, r) - np.eye(2)*np.dot(r, r)*0.5
            u1[1:] += -0.5*x**2*self._aS
            u1[1:] -= nu*devR@self._aS
            u1[1:] += -nu*r*self._ae
            u1[1:] += x*_ix@r*self._ath

            u1[0] += self._ae*x
            u1[0] += x*np.dot(r, self._aS)
            u1[0] += usv*self._ath


            u2[0] += 0.5*x**2*np.dot((r - self.centroid), self._bv)
            u2[0] += self._c*usv + np.dot([usy, usz], self._bv)
            u2[1:] += x*self._c*_ix@r
            u2[1:] += nu*x*np.dot(self.centroid, self._bv)*r
            u2[1:] += nu*x*(0.5*np.dot(r,r)*self._bv - np.dot(self._bv, r)*r)


        # u = np.array([ux_p1 + ux_p2, u1_p1 + u1_p2, u2_p1 + u2_p2])
        u = u1 + u2
        if trace is not None:
            offset = _RigidMotion(self, trace=trace)
            return list(map(float, u + offset.u(x, r)))
        else:
            return list(map(float, u))
    


    def strain(self, x: float, 
               r: Optional[Sequence[float]] = None, 
               fiber=None, n=None) -> list[float]:
        """
        Return [ε_xx, γ_x1, γ_x2] at (x, r).
        - ε_xx is axial (component 33).
        - γ_x1 ≡ γ_13, γ_x2 ≡ γ_23.
        """
        model = self._section_mesh
        if r is None and fiber is None and n is None:
            r = np.array([0.0, 0.0], dtype=float)
        elif fiber is not None:
            # r = model.nodes[n]
            r = fiber.coord
        elif n is not None:
            r = model.nodes[n]
        else:
            r = np.array(r, dtype=float)

        x = float(x)

        model = self._section_mesh
        # uv = model.create_handle(model.warping())
        # eps_xx  = self._ae + (self._be + np.dot(self._aS+self._bv, r))*x
        eps_xx = self._ae + np.dot(self._aS, r) + x*np.dot(self._bv, r - self.centroid)

        gamma = (self._ath + self._c)*(_ix@r) + _shear_poisson(r, self.centroid, self._nu)@self._bv
        # gamma = list(map(float, gamma))

        if np.linalg.norm(r) > 0:
            model = self._section_mesh
            if fiber is None:
                raise ValueError("Cell not found")
            
            gamma +=  (self._ath + self._c)*model.cell_gradient(fiber, self._warp_twist)
            gamma +=  model.cell_gradient(fiber, self._warp_shear.T@self._bv)

            # du_shear = [model.cell_gradient(fiber, self._warp_shear[0]),
            #             model.cell_gradient(fiber, self._warp_shear[1])]
            # gamma[0] += (self._ath + self._c)*du_twist[0]
            # gamma[0] += du_shear[0][0]*self._bv[0] + du_shear[0][1]*self._bv[1]
            # gamma[1] += (self._ath + self._c)*du_twist[1]
            # gamma[1] += du_shear[1][0]*self._bv[0] + du_shear[1][1]*self._bv[1]

        return [eps_xx, *map(float, gamma)]


    def stress(self, x: float, **kwds) -> list[float]:
        """
        Return [σ_xx, τ_x1, τ_x2] at (x, r).
        Only r=None (or r=(0,0)) is implemented.
        """
        eps_xx, gamma_x1, gamma_x2 = self.strain(x, **kwds)
        sig_xx = self.E * eps_xx
        tau_x1 = self.G * gamma_x1
        tau_x2 = self.G * gamma_x2
        return [sig_xx, tau_x1, tau_x2]

    def moment(self, x: float) -> list[float]:
        """
        Return bending moments [M1, M2] at location x.
        """
        m = np.zeros(3)
        model = self._section_mesh
        for fiber in model.fibers:
            m += np.cross(np.array([0.0, *fiber.coord]), self.stress(x, fiber=fiber))*fiber.area
        return m


    def render(self, state=None, scale: float=1.0, trace=None):
        import xara
        import veux
        from veux.config import MeshStyle, NodeStyle
        from shps.frame.extrude import ExtrudeTetrahedron
        shape = self.shape

        n = 10
        ex = ExtrudeTetrahedron(shape.model, direction=[0, 0, self.length/n])
        # ex = ExtrudeTetrahedron(shape.model, direction=[0, 0, shape.mesh_size])
        model = xara.Model(ndm=3, ndf=3)

        model.material("ElasticIsotropic", 1, self.E, 0.28)

        x = 0
        for i in range(n):
            for tag, coords in ex.nodes():
                y,z, x = coords
                model.node(tag, float(x), float(y), float(z))

            for tag, cell in ex.cells():
                model.element("FourNodeTetrahedron", tag, tuple(cell), 1)

            ex.advance()

        if state is None:
            def state(n):
                x, *r = model.nodeCoord(n)
                return self.u(x, r, trace=trace)
        artist = veux.create_artist(model, ndf=3, vertical=3)
        artist.draw_origin(extrude=True)
        artist.draw_outlines(state=state, scale=scale)
        artist.draw_surfaces(state=state, scale=scale)
        veux.serve(artist)



def plot_grid(x,y,z, u=None, ax=None, **kwargs):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Line3DCollection
    if u is None:
        u = lambda x,y,z: (0.*x, 0.*y, 0.*z)

    if ax is None:
        _, ax = plt.subplots(1,1,subplot_kw={"projection": "3d"})

    ax.set_xlim(x[0]*1.1, x[1]*1.1)
    ax.set_ylim(z[0]*1.1, z[1]*1.1)
    ax.set_zlim(y[0]*1.1, y[1]*1.1)
    #
    X,Y = np.meshgrid(np.linspace(*x), np.linspace(*y))
    Z = z[0]*np.ones(X.shape)
    segs1 = np.stack((X,Z,Y)+np.stack(u(X,Y,Z)), axis=2)
    segs2 = segs1.transpose(1,0,2)
    ax.add_collection(Line3DCollection(segs1, **kwargs))
    ax.add_collection(Line3DCollection(segs2, **kwargs))
    Z = z[1]*np.ones(X.shape)
    ux,uy,uz = u(X,Y,Z)
    segs1 = np.stack((X,Z,Y)+np.stack(u(X,Y,Z)), axis=2)
    segs2 = segs1.transpose(1,0,2)
    ax.add_collection(Line3DCollection(segs1, **kwargs))
    ax.add_collection(Line3DCollection(segs2, **kwargs))

    #
    X,Z = np.meshgrid(np.linspace(*x), np.linspace(*z))
    Y = y[0]*np.ones(X.shape)
    segs1 = np.stack((X,Z,Y)+np.stack(u(X,Y,Z)), axis=2)
    segs2 = segs1.transpose(1,0,2)
    ax.add_collection(Line3DCollection(segs1, **kwargs))
    ax.add_collection(Line3DCollection(segs2, **kwargs))
    Y = y[1]*np.ones(X.shape)
    segs1 = np.stack((X,Z,Y)+np.stack(u(X,Y,Z)), axis=2)
    segs2 = segs1.transpose(1,0,2)
    ax.add_collection(Line3DCollection(segs1, **kwargs))
    ax.add_collection(Line3DCollection(segs2, **kwargs))

    #ax.autoscale()
    aspect = [ub - lb for lb, ub in (getattr(ax, f'get_{a}lim')() for a in 'xyz')]
    aspect = [max(a,max(aspect)/8) for a in aspect]
    ax.set_box_aspect(aspect)
    ax.axis("off")
    return ax


if __name__ == "__main__":
    import xara.units.iks as units
    from xsection.library import from_aisc
    shape = from_aisc("W18x40", units=units, mesh_scale=1/100, fillet=True)
    shape = shape.rotate(np.pi/4)
    shape = shape.translate(-shape.centroid)

    sv = SaintVenant(shape,
                     length=shape.d*3,
                     material=dict(E=1,G=1),
                     N=0.0,
                     M=[0.0, 0.0],
                     T=0.0,
                     V=[0.0, 10.0])
    print(sv.strain(0.3))  # [ε_xx, γ_x1, γ_x2]
    print(sv.stress(0.3))  # [σ_xx, τ_x1, τ_x2]
    print(sv.u(0))       # [u1, u2, ux]
    print(sv.u(sv.length))       # [u1, u2, ux]

