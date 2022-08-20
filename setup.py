import cx_Freeze

executables = [cx_Freeze.Executable("game/main.py")]

cx_Freeze.setup(
    name="Mage Game",
    version="0.1.0",
    options={"build_exe": {
        "packages":["pygame"],
        "include_files":["player.png"]
    }},
    executables = executables,
)
