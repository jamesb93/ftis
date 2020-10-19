from ftis.common.analyser import FTISAnalyser
from ftis.common.proc import singleproc
from ftis.common.io import write_json

class Dummy(FTISAnalyser):
    def __init__(self, cache=False):
        super().__init__(cache=cache)
        self.a = 1
        self.b = "foo"

    def dump(self):
        write_json(self.dump_path, self.output)

    def go(self, workable):
        self.output = {
            "1" : self.a,
            "2" : self.b
        }

    def run(self):
        singleproc(self.name, self.go, self.input)
