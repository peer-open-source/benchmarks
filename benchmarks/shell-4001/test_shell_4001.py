import xara 

def test_LMS():

    # ========================================================================================
    # RW-A20-P10-S38 (Tran, 2012) - Definition of properties and creation of materials
    # Basic units: N, mm
    # ========================================================================================
    
    model = xara.Model(ndm=3, ndf=6)
    #
    # Create uniaxial steel materials
    #
    # steel x
    fyX = 469.93             # fy
    bx = 0.02                # strain hardening

    # steel Y web
    fyYw = 409.71            # fy
    byw = 0.02               # strain hardening

    # steel Y boundary
    fyYb = 429.78            # fy
    byb = 0.01               # strain hardening

    # steel misc
    Es = 200000.0            # Young's modulus
    R0 = 20.0                # initial value of curvature parameter
    A1 = 0.925               # curvature degradation parameter
    A2 = 0.15                # curvature degradation parameter

    # build steel materials
    model.uniaxialMaterial('Steel02', 1, fyX,  Es, bx,  R0, A1, A2)  # steel X
    model.uniaxialMaterial('Steel02', 2, fyYw, Es, byw, R0, A1, A2)  # steel Y web
    model.uniaxialMaterial('Steel02', 3, fyYb, Es, byb, R0, A1, A2)  # steel Y boundary

    # ----------------------------------------------------------------------------------------
    # Create uniaxial concrete materials
    # ----------------------------------------------------------------------------------------
    # unconfined
    fpc = -47.09             # peak compressive stress
    ec0 = -0.00232           # strain at peak compressive stress
    ft = 2.13                # peak tensile stress
    et = 0.00008             # strain at peak tensile stress
    Ec = 34766.59            # Young's modulus

    # confined
    fpcc = -53.78            # peak compressive stress
    ec0c = -0.00397          # strain at peak compressive stress
    Ecc = 36542.37           # Young's modulus

    # build concrete materials
    model.uniaxialMaterial('ConcreteCM', 4, fpc,  ec0, Ec, 7.16, 1.016, ft, et, 1.2, 10000)      # unconfined concrete
    model.uniaxialMaterial('ConcreteCM', 5, fpcc, ec0c, Ecc, 8.44, 1.023, ft, et, 1.2, 10000)    # confined concrete

    # define reinforcing ratios   
    rouXw = 0.0027         # X web 
    rouXb = 0.0082         # X boundary 
    rouYw = 0.0027         # Y web
    rouYb = 0.0323         # Y boundary

    # shear resisting mechanism parameters 
    nu = 0.35                           # friction coefficient
    alfadow = 0.005                     # dowel action stiffness parameter
    
    #
    # Create FSAM nDMaterial
    #
    
    model.nDMaterial('FSAM', 6, 0.0, 1, 2, 4, rouXw, rouYw, nu, alfadow)           # Web (unconfined concrete)
    model.nDMaterial('FSAM', 7, 0.0, 1, 3, 5, rouXb, rouYb, nu, alfadow)           # Boundary (confined concrete)

    # ----------------------------------------------------------------------------------------
    # Create LayeredMembraneSection section
    # ----------------------------------------------------------------------------------------

    tw = 152.4    # Wall thickness

    model.section('LMS', 10, tw, 1, mat=6, thick=tw)    # Section type b (wall web)
    model.section('LMS', 11, tw, 1, mat=7, thick=tw)    # Section type a (wall boundary)

    assert True 


def test_RCLMS():

    # ========================================================================================
    # RW-A20-P10-S38 (Tran, 2012) - Definition of properties and creation of materials
    # Basic units: N, mm
    # ========================================================================================
    ops = xara.Model(ndm=2, ndf=3)

    # ----------------------------------------------------------------------------------------
    # Create uniaxial steel materials
    # ----------------------------------------------------------------------------------------
    # steel x
    fyX = 469.93             # fy
    bx = 0.02                # strain hardening

    # steel Y web
    fyYw = 409.71            # fy
    byw = 0.02               # strain hardening

    # steel Y boundary
    fyYb = 429.78            # fy
    byb = 0.01               # strain hardening

    # steel misc
    Es = 200000.0            # Young's modulus
    R0 = 20.0                # initial value of curvature parameter
    A1 = 0.925               # curvature degradation parameter
    A2 = 0.15                # curvature degradation parameter

    # build steel materials
    ops.uniaxialMaterial('Steel02', 1, fyX,  Es, bx,  R0, A1, A2)  # steel X
    ops.uniaxialMaterial('Steel02', 2, fyYw, Es, byw, R0, A1, A2)  # steel Y web
    ops.uniaxialMaterial('Steel02', 3, fyYb, Es, byb, R0, A1, A2)  # steel Y boundary

    # ----------------------------------------------------------------------------------------
    # Create uniaxial concrete materials
    # ----------------------------------------------------------------------------------------
    # unconfined
    fpc = -47.09             # peak compressive stress
    ec0 = -0.00232           # strain at peak compressive stress
    ft = 2.13                # peak tensile stress
    et = 0.00008             # strain at peak tensile stress
    Ec = 34766.59            # Young's modulus

    # confined
    fpcc = -53.78            # peak compressive stress
    ec0c = -0.00397          # strain at peak compressive stress
    Ecc = 36542.37           # Young's modulus

    # build concrete materials
    ops.uniaxialMaterial('Concrete02', 4, fpc,  ec0,  0.0, -0.037, 0.1, ft, 1738.33)    # unconfined concrete
    ops.uniaxialMaterial('Concrete02', 5, fpcc, ec0c, -9.42, -0.047, 0.1, ft, 1827.12)  # confined concrete

    # define reinforcing ratios   
    rouXw = 0.0027         # X web 
    rouXb = 0.0082         # X boundary 
    rouYw = 0.0027         # Y web
    rouYb = 0.0323         # Y boundary

    # ----------------------------------------------------------------------------------------
    # Create orthotropic concrete layers to represent unconfined and confined concrete
    # ----------------------------------------------------------------------------------------

    ops.nDMaterial('OrthotropicRAConcrete', 6, 4, et, ec0,  0.0, '-damageCte1', 0.175, '-damageCte2', 0.5)   # unconfined concrete
    ops.nDMaterial('OrthotropicRAConcrete', 7, 5, et, ec0c, 0.0, '-damageCte1', 0.175, '-damageCte2', 0.5)   # confined concrete

    # ----------------------------------------------------------------------------------------
    # Create smeared steel layers to represent boundary and web reinforment
    # ----------------------------------------------------------------------------------------

    ops.nDMaterial('SmearedSteelDoubleLayer', 8, 1, 2, rouXw, rouYw, 0.0)       # steel web
    ops.nDMaterial('SmearedSteelDoubleLayer', 9, 1, 3, rouXb, rouYb, 0.0)       # steel boundary

    # ----------------------------------------------------------------------------------------  
    # Create ReinforcedConcreteLayeredMembraneSection sections composed of concrete and steel layers
    # ----------------------------------------------------------------------------------------
    tw  = 152.4     # wall thickness
    tnc = 50.8      # unconfined concrete wall layer thickness
    tc  = 101.6     # confined concrete wall layer thickness   

    ops.section('RCLMS', 10, 1, 1, '-reinfSteel', 8, '-conc', 6,    '-concThick', tw)      # Section type b (wall web)
    ops.section('RCLMS', 11, 1, 2, '-reinfSteel', 9, '-conc', 6, 7, '-concThick', tnc, tc)      # Section type a (wall boundary)   

    assert True

if __name__ == "__main__":
    test_RCLMS()
    test_LMS()
