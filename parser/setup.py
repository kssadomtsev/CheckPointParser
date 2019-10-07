from setuptools import setup
from setuptools.extension import Extension

from Cython.Build import cythonize
from Cython.Distutils import build_ext

setup(
    name="parser",
    ext_modules=cythonize(
        [
            Extension("database.*", ["database/*.py"]),
            Extension("importer.*", ["importer/*.py"]),
            Extension("model.*", ["model/*.py"]),
            Extension("xmlformat.*", ["xmlformat/*.py"])
        ],
        build_dir="build",
        compiler_directives=dict(
        always_allow_keywords=True
        )),
    cmdclass=dict(
        build_ext=build_ext
    ),
    packages=["database", "importer", "model", "xmlformat"]
)