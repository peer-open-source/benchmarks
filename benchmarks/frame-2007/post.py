import numpy as np


def FiberStress(model, 
                 shape,
                 section: int,
                 stress : str, 
                 element: int=1):

    nen = 3
    def f(fiber):
        s = model.eleResponse(element, "section", section, "fiber", fiber, "stress")
        return [s]*nen

    return NodalAverage(shape.model, f, stress)

class NodalAverage:
    def __init__(self, model, response: callable, component):
        """
        """
        ndm = 2
        self._component = component

        if isinstance(response, str):

            resp_func = lambda elem: model.eleResponse(elem, response)
        elif callable(response):
            resp_func = response
        else:
            raise ValueError("response must be a string or callable")

        # For a typical 2D element with 3 stress components: sxx, syy, sxy
        if ndm == 2:
            keys = "sxx", "sxy", "sxz"
        else:
            # For a typical 3D element with 6 stress components: sxx, syy, szz, sxy, syz, sxz
            keys = "sxx", "syy", "szz", "sxy", "syz", "sxz"

        nrc = len(keys)

        output = {
            node: {
                "_count": 0,
                **{key: 0.0 for key in keys}
            } for node in range(len(model.nodes))
        }

        # Assume each element’s response yields a flat array 
        # with length = nen * nrc.
        # Then we reshape it to (nen, nrc).
        for elem, elem_nodes in enumerate(model.cells()):
            nen = len(elem_nodes)

            se = resp_func(elem)
            assert not (len(se) % nen), f"Element {elem} response length mismatch: {len(se)} != {nen * nrc}"
            se = np.reshape(se, (nen, nrc))

            # Accumulate at element's nodes
            for i, node in enumerate(elem_nodes):
                for j, key in enumerate(keys):
                    output[node][key] += se[i][j]

                output[node]["_count"] += 1


        # Now do averaging (if a node belongs to multiple elements).
        for node in output:
            c = output[node]["_count"] or 1.0

            for key in keys:
                output[node][key] /= c


        # Clean up
        for node in output:
            output[node].pop("_count", None)


        self._values = output

    def __call__(self, node):
        return self._values[node][self._component]