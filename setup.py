import cx_Freeze
from setuptools import find_packages

executables = [cx_Freeze.Executable("main.py")]

cx_Freeze.setup(
    name="Mage Game",
    version="0.3.0",
    packages=find_packages(),
    options={
        "build_exe": {
            "packages":["pygame"],
            "include_files":["assets/"]
        }
    },
    executables = executables,
)
