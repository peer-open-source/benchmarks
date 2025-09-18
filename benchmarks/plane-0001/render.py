#
# Claudio Perez
#
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection

def plot_grid(x,y,z, u=None, ax=None, **kwargs):
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

#plot_grid((0,5,9), (0, 1, 4), (-.5,.5,4))
#plt.show()

def plotu(domain, u=None):
    ndm = len(domain)
    if u is None:
        u = lambda x: np.zeros(ndm)

    proj = "3d" if ndm == 3 else None
    domain = np.atleast_1d(domain)
    grid, curv = 4, 10
    ax = plt.figure().add_subplot(projection=proj)


    # for crd in np.eye(len(domain),dtype=int)[:1,:]==1:
    #     #step[crd,:] = []
    #     idx = np.where(~crd)[0]
    #     step = np.zeros((ndm,curv*grid**(ndm-1)))
    #     step[crd,:] = np.tile(np.linspace(*domain[crd].T, curv*grid).T,grid).flatten()
    #     #step[crd,:] = np.linspace(*domain[crd].T, curv*grid*grid).T
    #     for i, mesh in enumerate(np.meshgrid(*np.linspace(*domain[~crd].T, grid).T)):
    #         #print(i,mesh)
    #         #step[idx[i],::curv] = mesh.flatten()
    #         #step[idx[i],:] = np.tile(mesh.flatten(),(curv)).flatten()
    #         step[idx[i],:] = np.tile(mesh,(curv)).flatten()
    #         print(step[idx[i],:])
    #     #step[:,1::curv] = np.nan
    #     #step[:,::2] = np.nan
    #     ax.plot(*step)
    #     #for step in zip(*mesh):
    #     #    print(step)

    for crd in np.eye(len(domain),dtype=int)==1:
        for i,fixed_coord in enumerate(np.linspace(*domain[~crd].T,grid)):
            print(crd, fixed_coord)
            base = np.zeros((ndm,curv))
            base[crd,:] = np.linspace(*domain[crd].T, curv).T
            base[~crd,:] = np.array([fixed_coord]*curv).T
            #base = np.zeros((ndm,*[curv]*(ndm-1)))
            #base[crd,:] = np.linspace(*domain[crd].T, curv).T
            #base[~crd,:] = fixed_coord#*np.ones(base[~crd,:].shape)

            ax.plot(*base, alpha=0.5, color="gray")
            #print(np.array([x.flatten()+u(x) for x in np.array(base).T]))
            ##plt.plot(*np.array([[[5,1],[-1,0]]@x for x in np.array(base).T]), color="red")
            #ax.plot(*np.array([x+u(x) for x in np.array(base).T]).T, color="red")

    if ndm == 2:
        ax.axis("equal")
    else:
        ax.autoscale()

def plotu(u, domain, ax=None):
    grid, curv = 6, 20
    if ax is None:
        fig, ax= plt.subplots()
    for crd in range(2):
        for i,fixed_coord in enumerate(np.linspace(*domain[not crd],grid)):
            base = [0,0]
            base[crd] = np.linspace(*domain[crd], curv)
            base[not crd] = np.array([fixed_coord]*curv)
            ax.plot(*base, alpha=0.5, color="gray")

            print(np.array([x.flatten()+u(x) for x in np.array(base).T]))
            #plt.plot(*np.array([[[5,1],[-1,0]]@x for x in np.array(base).T]), color="red")
            ax.plot(*np.array([x+u(x) for x in np.array(base).T]).T, color="red")
    ax.axis("equal")
    return ax


if __name__ == "__main__":

    # plotu(lambda x: print(x) or np.array([5*x[0]+x[1]**2, -x[0]]), ((0, 1), (0, 1)))
    plt.style.use("typewriter")
    nu = 0.3

    E  = 100
    h  = 1
    R  = (E*h**3)/12
    nu = 0.3
    plot_grid((0,5,9), (0., 1., 4), (-h/2,h/2,4), u=lambda x,y,z:
            (-x*y/R, y*z/R, (nu*x**2 + y**2 - z**2)/R)
    ).figure.savefig("img/beam.png")

    R /= -2
    ax = plotu(lambda x: ( -x[1]*x[0]/R, (x[0]**2 - x[1]**2)/R,), ((-0.5, 0.5), (-0.5, 0.5)))
    ax.set_xlabel("$x_2$")
    ax.set_ylabel("$x_3$")
    ax.set_title("Cross Section Deformation")
    ax.figure.savefig("img/cross.png")# , ax.figure.add_subplot(122))
    #plt.show()
    #plotu(lambda x: np.array([0.0, 1/2*(nu*x[1]**2 + 3**2 - 5**2)]), ((0,1),(0,1)))
    #plotu(((0.,5.),(0,1.)))
    #plotu(((0.,5.),(0,1.),(-1,1)))

    #plt.show()

