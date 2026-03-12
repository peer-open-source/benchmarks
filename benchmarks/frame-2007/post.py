import numpy as np
import matplotlib.pyplot as plt
from xara.post import FiberStress, NodalAverage



class PlotResponse:
    def __init__(self):
        self.node = None
        self.dof = None 
        self.model = None
        self.u = [0]
        self.V = [0]

        self.markers = iter(["-","-.","--","-.", ":", "-"])
        self.colors  = iter(["k", "r", "b", "g", "m", "r"])

        fig, (ax,leg) = plt.subplots(ncols=2,
                                     gridspec_kw={"width_ratios": [5, 2.5]})#, constrained_layout=True)
        leg.axis("off")
        ax.axhline(0, color='k', lw=0.5)
        ax.axvline(0, color='k', lw=0.5)
        ax.set_xlabel("Displacement (in)")
        ax.set_ylabel("Load (kips)")
        ax.grid(True)
        self.fig = fig
        self.leg = leg
        self.ax = ax
        from pathlib import Path
        for file in Path("out").glob("shell-2007-case1-pu.txt"):
            case = file.stem.split("-")[-2][4:]
            ps, uz, vs, uy = np.loadtxt(file, unpack=True)
            ax.plot(uz[::20], ps[::20], "x", label=f"Shells", 
                    color="gray",
                    # linestyle="-"
            )
    
    def reset(self, model, node, dof, label=None):
        self.label = label
        self.model = model
        self.node = node
        self.dof = dof
        self.u = [0]
        self.V = [0]

    def update(self):
        self.u.append(self.model.state.u(self.node, self.dof))
        self.model.reactions()
        self.V.append(self.model.nodeReaction(self.node, self.dof))

    def draw(self):
        self.ax.plot(self.u,self.V, 
                next(self.markers), 
                color=next(self.colors),
                label=self.label)

    def finish(self):
        h,l = self.ax.get_legend_handles_labels()
        self.leg.legend(h,l,borderaxespad=0)
        plt.tight_layout()

class PlotPlasticSpread:
    def __init__(self, model, elements):
        import matplotlib.pyplot as plt
        self._model = model
        self._elements = elements
        # 3d plot
        self._fig = plt.figure()
        self._ax = self._fig.add_subplot(111, projection='3d')
        self._ax.set_xlabel("$x/L$")
        self._ax.set_ylabel("Time")
        self._ax.set_zlabel("\\% Yield")

        self._last_ps = np.zeros(sum(len(e.plastic_spread()) for e in elements))


    def finish(self):
        pass 

    def update(self):
        ps = []
        for i,elem in enumerate(self._elements):
            ps.extend(elem.plastic_spread())

        n_sections = len(ps)
        X = np.array([i/(n_sections-1) for i in range(n_sections)])
        self._ax.scatter(X, [self._model.getTime()]*n_sections, ps,
                        depthshade=False,
                        c=ps, cmap='viridis', vmin=0, vmax=1)

class ElementFiberYieldMap:
    def __init__(self, model, shape, element: int=1, Fy: float=1.0, remember=True):
        self._model = model
        self._shape = shape
        self._element = element
        self._sections = []
        for i,section in enumerate(model.eleResponse(element, "integrationPoints")):
            self._sections.append(
                YieldMap(model, shape, section=i+1, element=element, Fy=Fy, remember=remember)
            )

    def plastic_spread(self):
        return [s.plastic_ratio() for s in self._sections]

    def summary(self):
        return " ".join(f"{s.plastic_ratio()*100:6.2f}" for s in self._sections)


class YieldMap:
    def __init__(self, model, shape, section: int, element: int=1, Fy: float=1.0, remember=True):
        self._model = model
        self._shape = shape
        self._section = section
        self._element = element
        self._remember = remember
        self._Fy = Fy
        self._stress = {
            i: 0.0 for i in range(len(shape.model.cells()))
        }
        self._update()

    def _update(self):
        for fiber in self._stress:
            s = self._model.eleResponse(self._element, "section", self._section, "fiber", fiber, "stress")
            sxx = s[0]
            sxy = s[1]
            txz = s[2]
            vm = np.sqrt(sxx**2 + 3*(sxy**2 + txz**2))
            if self._remember:
                self._stress[fiber] = max(self._stress[fiber], vm)
            else:
                self._stress[fiber] = vm

    def plastic_ratio(self):
        self._update()

        count = 0
        for fiber in self._stress:
            if self._stress[fiber] >= self._Fy:
                count += 1
        return count / len(self._stress)

# class NodalAverage:
#     def __init__(self, model, response: callable, component, form=None):
#         """
#         """
#         self._component = component

#         if isinstance(response, str):
#             resp_func = lambda elem: model.eleResponse(elem, response)
#         elif callable(response):
#             resp_func = response
#         else:
#             raise ValueError("response must be a string or callable")

#         ndm = 2
#         if form is None:
#             if ndm == 2:
#                 form = "plane"
#             elif ndm == 3:
#                 form = "solid"
#         self._form = form

#         if form == "frame":
#             keys = "sxx", "sxy", "sxz"
#         elif form == "plane":
#             keys = "sxx", "syy", "sxy"
#         elif form == "solid":
#             keys = "sxx", "syy", "szz", "sxy", "syz", "sxz"

#         nrc = len(keys)

#         output = {
#             node: {
#                 "_count": 0,
#                 **{key: 0.0 for key in keys}
#             } for node in range(len(model.nodes))
#         }

#         # Assume each element’s response yields a flat array 
#         # with length = nen * nrc.
#         # Then we reshape it to (nen, nrc).
#         for elem, elem_nodes in enumerate(model.cells()):
#             nen = len(elem_nodes)

#             se = resp_func(elem)
#             assert not (len(se) % nen), f"Element {elem} response length mismatch: {len(se)} != {nen * nrc}"
#             se = np.reshape(se, (nen, nrc))

#             # Accumulate at element's nodes
#             for i, node in enumerate(elem_nodes):
#                 for j, key in enumerate(keys):
#                     output[node][key] += se[i][j]

#                 output[node]["_count"] += 1


#         # Now do averaging (if a node belongs to multiple elements).
#         for node in output:
#             c = output[node]["_count"] or 1.0

#             for key in keys:
#                 output[node][key] /= c


#         # Clean up
#         for node in output:
#             output[node].pop("_count", None)


#         self._values = output

#     def __call__(self, node)->float:
#         if self._component == "svm":
#             if self._form == "frame":
#                 P = np.array([[1, 0, 0], [0, 3, 0], [0, 0, 3]], dtype=float)
#                 s = self._values[node]
#                 s = s["sxx"], s["sxy"], s["sxz"]
#             return np.sqrt(np.dot(s, P@s))
        
#         return self._values[node][self._component]



# def FiberStress(model,
#                  shape,
#                  section: int,
#                  stress : str,
#                  element: int=1):

#     nen = 3
#     def f(fiber):
#         s = model.eleResponse(element, "section", section, "fiber", fiber, "stress")
#         return [s]*nen

#     return NodalAverage(shape.model, f, stress, form="frame")