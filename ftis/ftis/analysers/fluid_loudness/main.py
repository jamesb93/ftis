
import os
import sys
import shutil
import multiprocessing
import tempfile
import subprocess
from shutil import rmtree
from ftis.common.analyser import FTISAnalyser
from ftis.common.exceptions import BinError
from ftis.common.utils import bufspill, write_json, get_workables
from ftis.common.types import Ftypes
from ftis.common.proc import multiproc


class FLUID_LOUDNESS(FTISAnalyser):
    def __init__(self, parent_process):
        super().__init__(parent_process)
        self.logger.debug("Creating FLUID_LOUDNESS instance")
        self.name = "FLUID_LOUDNESS".lower()
        self.input_type = Ftypes["folder"]
        self.output_type = Ftypes["json"]
        self.data_container = multiprocessing.Manager().dict()
        self.TMP = tempfile.mkdtemp()
        self.validate_cli()

    @staticmethod
    def validate_cli():
        if not shutil.which("fluid-loudness"):
            raise BinError("fluid-loudness executable not found in PATH")

    def analyse(self, workable: str, task, progress_bar):
        src = workable
        base_name = os.path.basename(workable)
        features = os.path.join(self.TMP, f"{base_name}loudness.wav")
        subprocess.call([
                "fluid-loudness",
                "-maxwindowsize", str(self.parameters["windowsize"]),
                "-windowsize", str(self.parameters["windowsize"]),
                "-hopsize", str(self.parameters["hopsize"]),
                "-kweighting", str(self.parameters["kweighting"]),
                "-truepeak", str(self.parameters["truepeak"]),
                "-source", str(src),
                "-features", str(features)
            ])

        progress_bar.update(task, advance = 1)
        data = bufspill(features)[0]
        list_data = data.tolist()
        self.data_container[workable] = list_data

    def run(self):  
        """
        In this method you implement the functionality for the analyser
        """

        workables = get_workables(self.input, ('.wav'))
        
        multiproc(self.name, self.analyse, workables)

        write_json(self.output, dict(self.data_container))
        rmtree(self.TMP)
