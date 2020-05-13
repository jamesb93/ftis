
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


class FLUID_TRANSIENTS(FTISAnalyser):
    def __init__(self, parent_process):
        """
        This is the bare minimum required to instantiate the object.
        """
        super().__init__(parent_process)
        self.logger.debug("Creating FLUID_TRANSIENTS instance")
        self.input_type = Ftypes["folder"]
        self.output_type = Ftypes["folder"]
        self.name = "FLUID_TRANSIENTS".lower()
        self.validate_cli()
        self.validate_parameters()

    @staticmethod
    def validate_cli():
        if not shutil.which("fluid-transients"):
            raise BinError("fluid-transients executable not found in PATH")

    def analyse(self, workable: str, task, progress_bar):
        # Setup paths/files etc
        src = workable
        base_name = os.path.basename(workable)
        residual = os.path.join(self.output, f"{base_name}_residual.wav")
        transients = os.path.join(self.output, f"{base_name}_transients.wav")
        subprocess.call([
                "fluid-transients",
                "-source", src,
                "-transients", transients,
                "-residual", residual,
                "-blocksize", str(self.parameters["blocksize"]),
                "-clumplength", str(self.parameters["clumplength"]),
                "-order", str(self.parameters["order"]),
                "-padsize", str(self.parameters["padsize"]),
                "-skew", str(self.parameters["skew"]),
                "-threshback", str(self.parameters["threshback"]),
                "-threshfwd", str(self.parameters["threshfwd"]),
                "-windowsize", str(self.parameters["windowsize"])
        ])
        progress_bar.update(task, advance = 1)


    def run(self):
        """
        In this method you implement the functionality for the analyser.
        Ideally, place the logic between the two loggers.
        """

        workables = get_workable(self.input, ('.wav'))

        multiproc(self.name, self.analyse, workables)
