import numpy as np
import thesis
from itertools import cycle

class PlotResponse:
    def __init__(self, scale=1, ax=None, axs=None):
        self.scale = scale

        self.markers = cycle(["-","-.","--","-.", ":"])
        self.colors  = cycle(["gray", "r", "b", "g", "m", "c"])
        if ax is None:
            fig, ax = thesis.subplots()
        else:
            fig = ax.figure
        ax.axhline(0, color='k', lw=1)
        ax.axvline(0, color='k', lw=1)
        self.fig = fig
        self.ax = ax
        self._axs = axs
        self._cycle = None
        self.reset()
    
    def reset(self, model=None, node=None, dof=None, label=None, cycle=None):
        self.label = label
        self.model = model
        self.node = node
        self.dof = dof
        self._cycle = cycle
        self.x = [0]
        self.y = [0]

    def update(self, model):
        scale = self.scale
        self.x.append(model.state.u(self.node, self.dof))
        self.y.append(model.getTime()*scale)

    def draw(self):
        if self._axs is None:
            self.ax.plot(self.x,self.y,
                    next(self.markers), 
                    color=next(self.colors),
                    label=self.label)
        else:
            self.ax.plot(self.x,self.y,
                    cycle=self._cycle,
                    label=self.label)
        
    def save_data(self, filename):
        np.savetxt(filename, np.array([self.x, self.y]).T, header="Rotation Torque")
    
    def load_data(self, filename):
        self.x, self.y = np.loadtxt(filename, unpack=True)


    def finish(self):
        # h,l = self.ax.get_legend_handles_labels()
        # self.leg.legend(h,l,borderaxespad=0)
        # self.ax.set_xlim([0, None])
        # self.ax.set_ylim([0, None])
        # # plt.tight_layout()
        # thesis.legend(self.ax)
        pass

