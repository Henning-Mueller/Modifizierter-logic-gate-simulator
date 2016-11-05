def csetup(name, pyx=False):
    import os
    import sys
    from distutils.core import setup
    from Cython.Build import cythonize

    sys.argv.append("build_ext")
    sys.argv.append("--inplace")

    if pyx:
        setup(
            name=name,
            ext_modules = cythonize("../{}.pyx".format(name))
            )
    else:
        setup(
            name=name,
            ext_modules = cythonize("../{}.py".format(name))
            )

    try:
        os.remove("../{}.c".format(name))
    except OSError:
        pass
    try:
        os.remove("../{}.pyd".format(name))
    except OSError:
        pass
    
    os.rename("{}.pyd".format(name),
              "../{}.pyd".format(name))

csetup_files = ("alignment",
                "boolean",
                "gui",
                "interfaces",
                "logic_circuit",
                "logic_circuit_gui",
                "text")
for file in csetup_files:
    csetup(file)
    print()
