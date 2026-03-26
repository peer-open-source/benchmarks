import numpy as np
import matplotlib.pyplot as plt

class PlotDisplacement:
    def __init__(self):
        self._fig, self._ax = plt.subplots(2)

    def draw(self, model):
        # x = []
        # x0 = 0.0
        # end = len(model.getNodeTags())
        # for tag in model.getEleTags():
        #     xg = model.eleResponse(tag, "integrationPoints")
        #     nodes = model.eleNodes(tag)
        #     x1 = model.nodeCoord(nodes[0])[0]
        #     L = model.nodeCoord(nodes[-1])[0]
        #     x.extend([x0 + xi for xi in xg])
        #     x0 += L - x1
        x = [model.nodeCoord(n)[0] for n in model.getNodeTags()]
        uz  = [model.state.u(n, 3) for n in model.getNodeTags()]
        uy  = [model.state.u(n, 2) for n in model.getNodeTags()]
        self._ax[0].plot(x, uz, marker="o", color="blue", linestyle='--', linewidth=1, label="FEM")
        self._ax[1].plot(x, uy, marker="o", color="blue", linestyle='--', linewidth=1, label="FEM")

    def finalize(self):
        self._ax[0].set_xlabel("X coordinate")
        self._ax[0].set_ylabel("Tip displacement Uz")
        self._ax[0].grid()
        self._ax[1].set_xlabel("X coordinate")
        self._ax[1].set_ylabel("Tip displacement Uy")
        self._ax[1].grid()
        self._ax[1].legend()
        self._ax[0].set_aspect('equal', 'box')
        self._ax[1].set_aspect('equal', 'box')




class PlotFiberStrain:
    def __init__(self, skip=False, ax=None):

        self._skip = skip
        if not skip and ax is None:
            fig, ax = plt.subplots(figsize=(6,6), tight_layout=True)
            self._ax = ax
        elif ax is not None:
            self._ax = ax
        else:
            self._ax = None

        self._markers = iter(["o", "x", "."])
        self._colors = iter(["r", "b", "g", "m", "c"])


    def draw(self,  model,  r: tuple[float,float], component: int):
        marker = next(self._markers)
        self._color = next(self._colors)
        if self._skip:
            return
        X = []
        e = []
        L = model.nodeCoord(len(model.getNodeTags()))[0]
        for element in model.getEleTags():
            xo = model.nodeCoord(model.eleNodes(element)[0])[0]/L
            x = [xo+x/L for x in model.eleResponse(element, "integrationPoints")]
            for i in range(len(x)):
                strain = model.eleResponse(element, 
                                        "section", i+1,
                                        "fiber", r,
                                        "strain")[component]
                e.append(strain)
                X.append(x[i])


        self._ax.plot(X, e, marker, 
                      color=self._color,
                      label=f'{component}')

    def finalize(self):
        if self._skip:
            return
        ax = self._ax
        ax.legend()
        ax.set_xlabel("$x/L$")
        ax.set_ylabel("Fiber Strain")
        ax.axhline(0, color='black', linestyle='-', linewidth=1)
        ax.axvline(0, color='black', linestyle='-', linewidth=1)
        ax.grid(True)

