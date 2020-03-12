import os
from ftis.templates import init, main, parameters
from ftis.common.exceptions import AnalyserExists
from ftis.common.utils import printp


def new_analyser(name: str):
    here = os.path.abspath(os.path.dirname(__file__))
    analyser_folder = os.path.join(here, 'analysers')
    new_analyser = os.path.join(analyser_folder, name)
    if os.path.exists(new_analyser):
        raise AnalyserExists()
    else:
        os.makedirs(new_analyser.lower())

    # Now fill the new directory with the right stuff.

    new_init = init.replace("@NAME@", name.upper())
    new_main = main.replace("@NAME@", name.upper())

    new_init_path = os.path.join(new_analyser, '__init__.py')
    new_main_path = os.path.join(new_analyser, 'main.py')
    new_para_path = os.path.join(new_analyser, 'parameters.yaml')

    printp(f"Generating new analyser: {name.upper()}")
    with open(new_init_path, "w") as f:
        f.write(new_init)
        f.close()

    with open(new_main_path, "a") as f:
        f.write(new_main)
        f.close()

    with open(new_para_path, "a") as f:
        f.write(parameters)
        f.close()
