import xara



def check_elastic(material, expected):
    data = material.asdict()
    for key, value in expected.items():
        assert data[key] == value, key

def test():

    expected = {
        "Epos": 200e9,
        "Eneg": 200e9,
        "density": 7850,
    }
    material = xara.UniaxialMaterial("Elastic", E=expected["Epos"], density=expected["density"])
    check_elastic(material, expected)
    # Pass E by position
    material = xara.UniaxialMaterial("Elastic", expected["Eneg"], density=expected["density"])
    check_elastic(material, expected)

if __name__ == "__main__":
    test()
