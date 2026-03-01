
# OpenSees -- Open System for Earthquake Engineering Simulation
# Pacific Earthquake Engineering Research Center
# http://opensees.berkeley.edu/
#
# 
# Units: kips, in, sec
# Written: fmk
# Date: January 2011
#
from math import asin, sqrt
import xara

def test_ElasticFrame():
    #
    # some parameters
    #
    PI =  2.0 * asin(1.0)
    g =  386.4
    ft = 12.0
    Load1 = 1185.0
    Load2 = 1185.0
    Load3 = 970.0

    # floor masses
    m1 =  Load1/(4*g) # 4 nodes per floor
    m2 =  Load2/(4*g)
    m3 =  Load3/(4*g)

    # floor distributed loads
    w1 =  Load1/(90*ft)   # frame 90 ft long
    w2 =  Load2/(90*ft)
    w3 =  Load3/(90*ft)

    # ------------------------------
    # Start of model generation
    # ------------------------------

    # Create ModelBuilder (with two-dimensions and 2 DOF/node)
    model = xara.Model(ndm=2, ndf=3)

    # Create nodes
    # ------------

    # Create nodes & add to Domain - command: node nodeId xCrd yCrd <-mass massX massY massRz>
    model.node( 1,     0.0,   0.0)
    model.node( 2,   360.0,   0.0)
    model.node( 3,   720.0,   0.0)
    model.node( 4,  1080.0,   0.0)
    model.node( 5,    0.0,  162.0, '-mass', m1, m1, 0.0)
    model.node( 6,  360.0,  162.0, '-mass', m1, m1, 0.0)
    model.node( 7,  720.0,  162.0, '-mass', m1, m1, 0.0)
    model.node( 8, 1080.0,  162.0, '-mass', m1, m1, 0.0)
    model.node( 9,     0.0, 324.0, '-mass', m2, m2, 0.0)
    model.node( 10,  360.0, 324.0, '-mass', m2, m2, 0.0)
    model.node( 11,  720.0, 324.0, '-mass', m2, m2, 0.0)
    model.node( 12, 1080.0, 324.0, '-mass', m2, m2, 0.0)
    model.node( 13,    0.0, 486.0, '-mass', m3, m3, 0.0)
    model.node( 14,  360.0, 486.0, '-mass', m3, m3, 0.0)
    model.node( 15,  720.0, 486.0, '-mass', m3, m3, 0.0)
    model.node( 16, 1080.0, 486.0, '-mass', m3, m3, 0.0)

    # the boundary conditions - command: fix nodeID xResrnt? yRestrnt? rZRestrnt?
    model.fix( 1, 1, 1, 1)
    model.fix( 2, 1, 1, 1)
    model.fix( 3, 1, 1, 1)
    model.fix( 4, 1, 1, 1)

    # Define geometric transformations for beam-column elements
    model.geomTransf( 'Linear', 1) # beams
    model.geomTransf( 'PDelta', 2) # columns

    # Define elements
    # Create elastic beam-column - command: element elasticBeamColumn eleID node1 node2 A E Iz geomTransfTag

    # Define the Columns
    model.element( 'elasticBeamColumn',  1,  1,  5, 75.6, 29000.0, 3400.0, 2) # W14X257
    model.element( 'elasticBeamColumn',  2,  5,  9, 75.6, 29000.0, 3400.0, 2) # W14X257
    model.element( 'elasticBeamColumn',  3,  9, 13, 75.6, 29000.0, 3400.0, 2) # W14X257
    model.element( 'elasticBeamColumn',  4,  2,  6, 91.4, 29000.0, 4330.0, 2) # W14X311
    model.element( 'elasticBeamColumn',  5,  6, 10, 91.4, 29000.0, 4330.0, 2) # W14X311
    model.element( 'elasticBeamColumn',  6, 10, 14, 91.4, 29000.0, 4330.0, 2) # W14X311
    model.element( 'elasticBeamColumn',  7,  3,  7, 91.4, 29000.0, 4330.0, 2) # W14X311
    model.element( 'elasticBeamColumn',  8,  7, 11, 91.4, 29000.0, 4330.0, 2) # W14X311
    model.element( 'elasticBeamColumn',  9, 11, 15, 91.4, 29000.0, 4330.0, 2) # W14X311
    model.element( 'elasticBeamColumn', 10,  4,  8, 75.6, 29000.0, 3400.0, 2) # W14X257
    model.element( 'elasticBeamColumn', 11,  8, 12, 75.6, 29000.0, 3400.0, 2) # W14X257
    model.element( 'elasticBeamColumn', 12, 12, 16, 75.6, 29000.0, 3400.0, 2) # W14X257

    # Define the Beams
    model.element( 'elasticBeamColumn', 13,  5,  6, 34.7, 29000.0, 5900.0, 1) # W33X118
    model.element( 'elasticBeamColumn', 14,  6,  7, 34.7, 29000.0, 5900.0, 1) # W33X118
    model.element( 'elasticBeamColumn', 15,  7,  8, 34.7, 29000.0, 5900.0, 1) # W33X118
    model.element( 'elasticBeamColumn', 16,  9, 10, 34.2, 29000.0, 4930.0, 1) # W30X116
    model.element( 'elasticBeamColumn', 17, 10, 11, 34.2, 29000.0, 4930.0, 1) # W30X116
    model.element( 'elasticBeamColumn', 18, 11, 12, 34.2, 29000.0, 4930.0, 1) # W30X116
    model.element( 'elasticBeamColumn', 19, 13, 14, 20.1, 29000.0, 1830.0, 1) # W24X68
    model.element( 'elasticBeamColumn', 20, 14, 15, 20.1, 29000.0, 1830.0, 1) # W24X68
    model.element( 'elasticBeamColumn', 21, 15, 16, 20.1, 29000.0, 1830.0, 1) # W24X68


    # Define loads for Gravity Analysis
    # ---------------------------------


    # Create a Plain load pattern with a linear TimeSeries: 
    #  command pattern Plain tag timeSeriesTag { loads }
    model.pattern('Plain', 1, 'Linear')
    model.eleLoad( '-ele', 13, 14, 15, '-type', '-beamUniform', -w1)
    model.eleLoad( '-ele', 16, 17, 18, '-type', '-beamUniform', -w2)
    model.eleLoad( '-ele', 19, 20, 21, '-type', '-beamUniform', -w3)


    # ---------------------------------
    # Create Analysis for Gravity Loads
    # ---------------------------------

    # Create the system of equation, a SPD using a band storage scheme
    model.system('BandSPD')

    # Create the DOF numberer, the reverse Cuthill-McKee algorithm
    model.numberer('RCM')

    # Create the constraint handler, a Plain handler is used as homo constraints
    model.constraints('Plain')

    # Create the integration scheme, the LoadControl scheme using steps of 1.0
    model.integrator('LoadControl', 1.0)

    # Create the solution algorithm, a Linear algorithm is created
    model.test('NormDispIncr', 1.0e-10, 6)
    model.algorithm('Newton')



    # create the analysis object 
    model.analysis('Static')


    # ---------------------------------
    # Perform Gravity Analysis
    # ---------------------------------

    model.analyze(1)

    # ---------------------------------
    # Check Equilibrium
    # ---------------------------------

    # invoke command to determine nodal reactions 
    model.reactions()

    node1Rxn = model.nodeReaction( 1) # nodeReaction command returns nodal reactions for specified node in a list
    node2Rxn = model.nodeReaction( 2)
    node3Rxn = model.nodeReaction( 3)
    node4Rxn = model.nodeReaction( 4)

    inputedFy =  -Load1 - Load2 - Load3 # loads added negative Fy diren to ele
    computedFx = node1Rxn[0] + node2Rxn[0] + node3Rxn[0] + node4Rxn[0]
    computedFy = node1Rxn[1] + node2Rxn[1] + node3Rxn[1] + node4Rxn[1]

    print("\nEqilibrium Check After Gravity:")
    print("SumX: Inputed: 0.0 + Computed:", computedFx, " =  ", 0.0+computedFx)
    print("SumY: Inputed: ", inputedFy, " + Computed: ", computedFy, " =  ", inputedFy+computedFy)

    # ---------------------------------
    # Lateral Load
    # ---------------------------------

    # gravity loads constant and time in domain to e 0.0
    model.loadConst('-time', 0.0)

    model.pattern("Plain", 2, "Linear")
    model.load( 13, 220.0,0.0,0.0, pattern=2)
    model.load(  9, 180.0,0.0,0.0, pattern=2)
    model.load(  5,  90.0,0.0,0.0, pattern=2)

    # ---------------------------------
    # Perform Lateral Analysis
    # ---------------------------------

    model.analyze(1)
    # ---------------------------------
    # Check Equilibrium
    # ---------------------------------

    model.reactions()
    # return nodal reactions for specified node in a list
    node1Rxn = model.nodeReaction( 1)
    node2Rxn = model.nodeReaction( 2)
    node3Rxn = model.nodeReaction( 3)
    node4Rxn = model.nodeReaction( 4)

    inputedFx =  220.0 + 180.0 + 90.0
    computedFx = node1Rxn[0] + node2Rxn[0] + node3Rxn[0] + node4Rxn[0]
    computedFy = node1Rxn[1] + node2Rxn[1] + node3Rxn[1] + node4Rxn[1]

    print("\nEqilibrium Check After Lateral Loads:")
    print("SumX: Inputed: ", inputedFx, " + Computed: ", computedFx, " =  ",inputedFx+computedFx)
    print("SumY: Inputed: ", inputedFy, " + Computed: ", computedFy, " =  ",inputedFy+computedFy)

    # ---------------------------------
    # Check Eigenvalues
    # ---------------------------------

    eigenValues = model.eigen(5)

    print("\nEigenvalues:")
    eigenValue = eigenValues[0]
    T1 = 2*PI/sqrt(eigenValue)
    print("T1 = ", T1)

    eigenValue = eigenValues[1]
    T2 = 2*PI/sqrt(eigenValue)
    print("T2 = ", T2)

    eigenValue = eigenValues[2]
    T3 = 2*PI/sqrt(eigenValue)
    print("T3 = ", T3)

    eigenValue = eigenValues[3]
    T4 = 2*PI/sqrt(eigenValue)
    print("T4 = ", T4)

    eigenValue = eigenValues[4]
    T5 = 2*PI/sqrt(eigenValue)
    print("T5 = ", T5)

    assert abs(T1-1.0401120938612862)<1e-12 and \
           abs(T2-0.3526488583606463)<1e-12 and \
           abs(T3-0.1930409642350476)<1e-12 and \
           abs(T4-0.15628823050715784)<1e-12 and \
           abs(T5-0.13080166151268388)<1e-12


if __name__ == "__main__":
    test_ElasticFrame()
