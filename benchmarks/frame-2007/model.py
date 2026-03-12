
from xara import Section, Material


def create_section(shape, trace, shear_):

    def _create_material(model, material):
        material._mtag = 1
        m1 = {k: material[k] for k in {"E", "G", "Fy", "Hiso", "Hkin"} }
        if not shear_:
            model.uniaxialMaterial("Hardening", 1, **m1)
        else:
            model.material(material.type, 1, **m1)


    def section(model, tag, shape, material):
        # shape = shape.translate(-shape.centroid)
        _create_material(model, material)

        if not shear_:
            type = "AxialFiber"
        elif trace == "MS":
            type = "NDFiber"
        else:
            type = "ShearFiber"
        
        model.section(
            Section(
                type=type,
                shape=shape,
                mixed_type=trace,
                material=material,
                mixed=trace is not None
            ),
            tag
        )

    return section




def analyze(model, nn, shear=True, trace=None, plots=(), verbose=False):

    if verbose:
        progress = lambda x: x
    else:
        from tqdm import tqdm as progress

    # Loading
    step = 200 #if shear and trace else 1000
    a = 0.1# 2/step if shear and trace else 0.1

    model.system("BandGeneral")
    model.constraints("Transformation")
    model.analysis("Static")
    model.test("Energy", 1e-18, 50, 2 if verbose else 0)

    model.timeSeries("Path", 1,
                     values=[0,  0.05,   0.5, -0.5, 0.0],
                     time=  [0,   a,   1,    4,   5 ])

    try:
        model.pattern("Plain", 1, 1)
        model.sp(nn, 3, 1.0, pattern=1)
        model.integrator("LoadControl", 1/step)

        for _ in progress(range(step*5)):
            if model.state.time >= 5.0:
                break

            if model.analyze(1) != 0:
                print(f"Failed at time = {model.state.time}")
                return

            for plot in plots:
                plot.update()
        return

    except KeyboardInterrupt:
        pass

    return