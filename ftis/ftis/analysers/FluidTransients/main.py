from flucoma import fluid
from flucoma.utils import cleanup
from ftis.common.analyser import FTISAnalyser
from ftis.common.proc import multiproc
from ftis.common.types import Ftypes


class FluidTransients(FTISAnalyser):
    def __init__(self, parent_process):
        super().__init__(parent_process)
        self.input_type = Ftypes.folder
        self.output_type = Ftypes.folder

    def analyse(self, workable):
        out_folder = self.output / workable.name
        out_folder.mkdir(exist_ok=True)

        transients = out_folder / f"transients_{workable.name}"
        residual = out_folder / f"residual_{workable.name}"

        fluid.transients(
            workable,
            transients=transients,
            residual=residual,
            blocksize=self.parameters["blocksize"],
            clumplength=self.parameters["clumplength"],
            order=self.parameters["order"],
            padsize=self.parameters["padsize"],
            skew=self.parameters["skew"],
            threshback=self.parameters["threshback"],
            threshfwd=self.parameters["threshfwd"],
            windowsize=self.parameters["windowsize"],
        )

    def run(self):
        workables = [x for x in self.input.iterdir() if x.suffix == ".wav"]
        multiproc(self.name, self.analyse, workables)
        cleanup()
