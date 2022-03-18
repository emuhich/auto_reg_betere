from cx_Freeze import setup, Executable

executables = [
    Executable('main.py'),
    Executable('league_spacer.py'),
    Executable('exeptions.py'),
    Executable('ProcessPool.py'),
    Executable('auto_wheel.py'),
]
setup(name='hello_world',
      version='0.0.1',
      description='My Hello World App!',
      executables=executables)