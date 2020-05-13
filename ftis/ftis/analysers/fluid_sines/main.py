
import os
import sys
import multiprocessing
import subprocess
import shutil
from ftis.common.analyser import FTISAnalyser
from ftis.common.proc import multiproc
from ftis.common.types import Ftypes
from ftis.common.exceptions import BinError
from ftis.common.utils import get_workables


class FLUID_SINES(FTISAnalyser):
    def __init__(self, parent_process):
        """
        This is the bare minimum required to instantiate the object.
        """
        super().__init__(parent_process)
        self.logger.debug("Creating FLUID_SINES instance")
        self.input_type = Ftypes["folder"]
        self.output_type = Ftypes["folder"]
        self.fftsettings = []
        self.name = "FLUID_SINES".lower()
        self.validate_cli()
        self.validate_parameters()

    @staticmethod
    def validate_cli():
        if not shutil.which("fluid-sines"):
            raise BinError("fluid-sines executable not found in PATH")

    def analyse(self, workable: str, task, progress_bar):
        # Setup paths/files etc
        src = workable
        base_name = os.path.basename(workable)
        sines = os.path.join(self.output, f"{base_name}_sines.wav")
        residual = os.path.join(self.output, f"{base_name}_residual.wav")
        params = [
                "fluid-sines",
                "-source", src,
                "-sines", sines,
                "-residual", residual,
                "-bandwidth", str(self.parameters["bandwidth"]),
                "-birthhighthreshold", str(self.parameters["birthhighthreshold"]),
                "-birthlowthreshold", str(self.parameters["birthlowthreshold"]),
                "-detectionthreshold", str(self.parameters["detectionthreshold"]),
                "-fftsettings",
                self.fftsettings[0], self.fftsettings[1], self.fftsettings[2],
                "-mintracklen", str(self.parameters["mintracklen"]),
                "-trackfreqrange", str(self.parameters["trackfreqrange"]),
                "-trackingmethod", str(self.parameters["trackingmethod"]),
                "-trackmagrange", str(self.parameters["trackmagrange"]),
                "-trackprob", str(self.parameters["trackprob"])
        ]
        subprocess.call(params)
        progress_bar.update(task, advance=1)

    def run(self):
        self.fftsettings = self.parameters["fftsettings"].split(" ")
        workables = get_workables(self.input, ('.wav'))
        multiproc(self.name, self.analyse, workables)
