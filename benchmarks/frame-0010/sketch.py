import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def draw_beam(ax, label, left_support, right_support):
    ax.set_xlim(0, 10)
    ax.set_ylim(-2, 2)
    ax.axis('off')
    ax.set_aspect('equal')
    ax.plot([2, 8], [0, 0], 'k', lw=2)  # beam line

    def fixed(x):
        ax.add_patch(patches.Rectangle((x-0.1, -0.5), 0.2, 1.0, fc='gray', hatch='///', zorder=10))

    def pin(x):
        ax.plot([x-0.2, x, x+0.2], [-0.5, 0, -0.5], 'k', lw=1)
        ax.plot([x-0.2, x+0.2], [-0.5, -0.5], 'k')

    def roller(x):
        circle = patches.Circle((x, -0.4), 0.15, fill=False)
        ax.add_patch(circle)
        ax.plot([x-0.3, x+0.3], [-0.65, -0.65], 'k')

    def orthoroller(x):
        ax.plot([x, x], [-0.3, 0.3], 'k')
        # ax.plot([x-0.3, x-0.3], [-0.15, 0.15], 'k')
        ax.plot([x+0.4, x+0.4], [-0.3, 0.3], 'k')
        circle = patches.Circle((x+0.2, 0), 0.15, fill=False)
        ax.add_patch(circle)

    # draw supports
    support_funcs = {
        'free':   lambda x: None,
        'fixed':  fixed,
        'pin':    pin,
        'roller': roller,
        'orthoroller': orthoroller
    }

    support_funcs[left_support](2)
    support_funcs[right_support](8)
    ax.text(5, -1.5, label, ha='center', fontsize=10)

if __name__ == "__main__":
    cases = [
        ('encastre',       'fixed',       'fixed'),
        ('propped',        'fixed',       'roller'),
        ('simple',         'pin',         'roller'),
        ('guided',         'fixed',       'orthoroller'),
        ('cantilever',     'fixed',       'free'),
    ]

    # Plotting
    fig, axes = plt.subplots(len(cases), 1, figsize=(6, 8))
    for ax, (label, left, right) in zip(axes, cases):
        draw_beam(ax, label, left, right)

    plt.tight_layout()
    plt.show()
