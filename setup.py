import cx_Freeze

executables = [cx_Freeze.Executable("main.py")]

cx_Freeze.setup(
    name="Mage Game",
    version="0.4.0",
    options={
        "build_exe": {
            "packages":["pygame"],
            "include_files":["assets/", "maps/"]
        }
    },
    executables = executables,
)
