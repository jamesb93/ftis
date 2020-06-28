from flucoma import fluid
from flucoma.utils import get_buffer
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import write_json, get_workables, filter_extensions
from ftis.common.types import Ftypes
from ftis.common.proc import multiproc, singleproc
from multiprocessing import Manager


class FluidMFCC(FTISAnalyser):
    def __init__(self, parent_process):
        super().__init__(parent_process)
        self.input_type = Ftypes.folder
        self.output_type = Ftypes.json
        self.data_container = Manager().dict()

    def analyse(self, workable):
        mfcc = fluid.mfcc(workable,
            fftsettings = self.parameters["fftsettings"],
            numbands = self.parameters["numbands"],
            numcoeffs = self.parameters["numcoeffs"])
        self.data_container[str(workable)] = get_buffer(mfcc)

    def run(self):
        workables = [x for x in self.input.iterdir() if x.suffix == ".wav"]
        multiproc(self.name, self.analyse, workables)
        write_json(self.output, dict(self.data_container))
