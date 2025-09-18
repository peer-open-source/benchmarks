import sympy

# --- 1) Define symbols ---
x = sympy.Symbol('x', real=True, nonnegative=True)
L = sympy.Symbol('L', positive=True)       # beam length
q = sympy.Symbol('q', real=True)           # uniform load (force/length)
E = sympy.Symbol('E', positive=True)
I = sympy.Symbol('I', positive=True)
k = sympy.Symbol('k', positive=True)       # shear correction factor
G = sympy.Symbol('G', positive=True)
A = sympy.Symbol('A', positive=True)

# We'll also define a convenient parameter mu = sqrt(k*G*A / (E*I)):
mu = sympy.sqrt(k*G*A/(E*I))

# --- 2) Unknown integration constants ---
C1, C2, C3, C4 = sympy.symbols('C1 C2 C3 C4', real=True)

# --- 3) Shear and moment from equilibrium ---
#   V'(x) = -q  =>  V(x) = -q*x + C1
#   M'(x) =  V  =>  M(x) = ∫ V(x) dx = -q*x^2/2 + C1*x + C2
V_expr = -q*x + C1
M_expr = -q*x**2/sympy.Integer(2) + C1*x + C2

# --- 4) Timoshenko kinematics:
#   phi(x) = M(x)/(E I)
#   w'(x) = phi(x) - V(x)/(k G A)
phi_expr = M_expr/(E*I)

wprime_expr = phi_expr - V_expr/(k*G*A)

# --- 5) Integrate w'(x) to get w(x) ---
# We'll do an indefinite integral w.r.t. x and add a constant C3:
w_expr_indef = sympy.integrate(wprime_expr, (x,))
# That indefinite integral has its own "+ constant". We'll call that C4:
# but to match typical usage, we'll incorporate *two* constants, e.g.:
w_expr = w_expr_indef + C3  # We'll let the solver handle C3 as "the integration constant."
# Actually we won't even need a separate C4 if we do indefinite. 
# We'll see that the solver might rename things. We'll just keep C3 in there.

# So w(x) = \int w'(x) dx + C3. 
# We now have 4 unknowns: C1, C2, C3, and (any constant from indefinite integration).
# Sympy's indefinite integral includes one arbitrary constant; we rename that to C4:
w_expr = w_expr.subs(sympy.Symbol('C1', real=True, positive=None), C4)  # This might be confusing
# Actually let's do it more systematically: we want to control our constants.

# Let's re-do that step more carefully, capturing the integration constant ourselves:
dummy = sympy.integrate(wprime_expr, (x,))
# 'dummy' will look like something + "Constant"
# We'll replace that "Constant" with our own, say "C4", then add C3 was extraneous. 
# To avoid confusion, let's define:

w_expr_general = sympy.Function('w')(x)  # just a placeholder
# Instead, let's do a manual indefinite integral with Sympy's "symbolic constant" approach:

# Actually let's do a definite integral from 0..x, plus w(0)=C3:
#   w(x) = w(0) + ∫[0..x] w'(ξ) dξ
# Then we can interpret w(0) as one of the boundary conditions. That is simpler.

w_expr_definite = sympy.integrate(wprime_expr, (x, 0, x)) + C3
# so w_expr_definite(0) = C3. 
# We'll let the solver figure out C3 from "w(0)=0 => C3=0" or something.

w_expr = w_expr_definite

# --- 6) Now apply the boundary conditions: 
# Classical fix--fix =>  w(0)=0, w'(0)=0, w(L)=0, w'(L)=0.

eqs = []
eqs.append(sympy.Eq(w_expr.subs(x, 0), 0))       # w(0) = 0
eqs.append(sympy.Eq(wprime_expr.subs(x, 0), 0))  # w'(0)=0
eqs.append(sympy.Eq(w_expr.subs(x, L), 0))       # w(L)=0
eqs.append(sympy.Eq(wprime_expr.subs(x, L), 0))  # w'(L)=0

# We have 4 unknowns: C1, C2, C3, and ??? Wait, we only see C1, C2, C3 in the expression so far.
# Actually the indefinite integral for M gave us C1, C2. The definite integral for w gave us C3.
# That is 3 unknowns. 
# Where is C4? 
# Let's see if Sympy automatically introduces it. 
# Actually from "sympy.integrate(wprime_expr,(x,0,x))" there's no new symbolic constant. 
# Because we used definite integral with lower limit 0. The boundary condition w(0)=0 sets C3=0 or not. 
# So we do indeed have 3 unknowns total: C1, C2, C3.

# But we want 4 unknowns for a 4th-order system. 
# The catch: The expression phi_expr = M_expr/(E*I) might also have 2 unknowns (C1, C2),
# and V_expr has 1 unknown. That's 3 total. Maybe we are short by 1. 
#
# Let's see if the system has a consistent solution. We'll let Sympy handle it:

sol = sympy.solve(eqs, [C1, C2, C3], dict=True)
print("Solution(s) for [C1, C2, C3]:", sol)

# Then we'll define w(x) with that solution substituted in:

if len(sol) > 0:
    w_solution = w_expr.subs(sol[0])
    w_solution_simpl = sympy.simplify(w_solution)
    print("\nFinal w(x) =\n", w_solution_simpl)
else:
    print("No solutions found?!")

# Suppose you have these numeric values:
vals = {
    E: 4e3,         # Pa
    I: 24**3/12,    # m^4
    G: 4e3/(2*(1+0.25)),
    A: 24.0,        # m^2
    k: 5/sympy.Integer(6),  # rectangular cross-section approx
    L: 240.0,       # m
    q: 1000.0       # N/m
}

# Solve the system symbolically:
solution = sympy.solve(eqs, [C1, C2, C3], dict=True)
w_of_x = w_expr.subs(solution[0])

# Now w_of_x is a symbolic expression. Evaluate at numeric x in [0..L]:
w_fun = sympy.lambdify(x, w_of_x.subs(vals), 'numpy')

import numpy as np
xx = np.linspace(0, vals[L], 51)
yy = [w_fun(xxi) for xxi in xx]

# Compare or plot (matplotlib) vs. your FEA nodal results
import matplotlib.pyplot as plt
plt.plot(xx, yy, label="Timoshenko fix–fix (analytic)")
plt.title("Deflection of Timoshenko Beam with Uniform Load")
plt.xlabel("x (m)")
plt.ylabel("w(x) (m)")
plt.legend()
plt.show()

