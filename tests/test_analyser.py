from ftis.common.analyser import FTISAnalyser
from ftis.process import FTISProcess
import os

test_path = os.path.dirname(os.path.abspath(__file__))
test_yaml = os.path.join(
    test_path,
    "cfgtest.yaml"
)


def test_instantiation():
    process = FTISProcess(test_yaml)
    process.initial_parse()
    analyser = FTISAnalyser(process)

