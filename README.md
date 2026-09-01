
Inside `benchmarks/` directories are named with the convention:
```
<category>-<group>/
```

The `<group>` is identified by a four-digit number:

- Numbers 0000-0999 are linear
- Numbers 1000-1999 are nonlinear geometry, linear material
- Numbers 2000-2999 are linear geometry, nonlinear material
- Numbers 3000-3999 are nonlinear geometry and material


Within each `<category>-<group>` directory, files are named as follows:

- `o-*.tcl` are Tcl test files that are compatible with both the OpenSees and Xara Tcl interpreters.
- `x-*.tcl` are Tcl test files that are compatible with Xara's superset of OpenSees Tcl
- `test_o_*.py` are Python test files compatible with both OpenSeesPy and [Xara's backwards compatible `opensees` Python interface](https://xara.so/user/manual/interpreter/openseespy.html).
- `test_x_*.py` are Python files compatible with [Xara's standard Python interface](https://xara.so/user/manual/interpreter/python.html)
