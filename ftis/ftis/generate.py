import os


def new_analyser(name: str):
    here = os.path.abspath(os.path.dirname(__file__))
    analyser_folder = os.path.join(here, 'analysers')
