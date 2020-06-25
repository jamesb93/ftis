from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import import_analyser
from ftis.process import FTISProcess
from pathlib import Path


def test_analyser_import():
    analysers = Path("../ftis/ftis/analysers")
    print(analysers.glob("**/*"))

    invalid_folders = ("__pycache__",".DS_Store")

    for x in analysers.iterdir():
        if x.stem not in invalid_folders:
            import_analyser(x.stem)