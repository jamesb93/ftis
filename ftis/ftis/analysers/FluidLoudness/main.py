
from flucoma.utils import get_buffer, cleanup
from flucoma import fluid
from multiprocessing import Manager
from ftis.common.analyser import FTISAnalyser
from ftis.common.exceptions import BinError
from ftis.common.utils import write_json, get_workables, filter_extensions
from ftis.common.types import Ftypes
from ftis.common.proc import multiproc


class FluidLoudness(FTISAnalyser):
    def __init__(self, parent_process):
        super().__init__(parent_process)
        self.input_type = Ftypes.folder
        self.output_type = Ftypes.json
        self.data_container = Manager().dict()

    def analyse(self, workable: str):
        loudness = fluid.loudness(workable,
            windowsize = self.parameters["windowsize"],
            hopsize = self.parameters["hopsize"],
            kweighting = self.parameters["kweighting"],
            truepeak = self.parameters["truepeak"])
    
        self.data_container[str(workable)] = get_buffer(loudness)

    def run(self):  
        workables = [x for x in self.input.iterdir() if x.suffix == ".wav"]
        multiproc(self.name, self.analyse, workables)
        write_json(self.output, dict(self.data_container))
        cleanup()