from flucoma import fluid
from flucoma.utils import cleanup
from ftis.common.analyser import FTISAnalyser
from ftis.common.proc import multiproc, singleproc
from ftis.common.types import Ftypes


class FluidSines(FTISAnalyser):
    def __init__(self, parent_process):
        super().__init__(parent_process)
        self.input_type = Ftypes.folder
        self.output_type = Ftypes.folder

    def analyse(self, workable):
        out_folder = self.output / workable.name
        out_folder.mkdir(exist_ok=True)

        sines = out_folder / f"sines_{workable.name}"
        residual = out_folder / f"residual_{workable.name}"

        fluid.sines(workable,
            sines=sines,
            residual=residual,
            bandwidth = self.parameters["bandwidth"],
            birthhighthreshold = self.parameters["birthhighthreshold"],
            birthlowthreshold = self.parameters["birthlowthreshold"],
            detectionthreshold = self.parameters["detectionthreshold"],
            fftsettings = self.parameters["fftsettings"],
            mintracklen = self.parameters["mintracklen"],
            trackingmethod = self.parameters["trackmethod"],
            trackfreqrange = self.parameters["trackfreqrange"],
            trackmagrange = self.parameters["trackmagrange"],
            trackprob = self.parameters["trackprob"])
        
    def run(self):
        workables = [x for x in self.input.iterdir() if x.suffix == ".wav"]
        singleproc(self.name, self.analyse, workables)
        cleanup()

