
import os
import sys
import shutil
import flucoma
import tempfile
import subprocess
import multiprocessing
from flucoma import fluid
from shutil import rmtree
from ftis.common.analyser import FTISAnalyser
from ftis.common.exceptions import BinError
from ftis.common.utils import bufspill, write_json, get_workables
from ftis.common.types import Ftypes
from ftis.common.proc import multiproc


class FLUID_LOUDNESS(FTISAnalyser):
    def __init__(self, parent_process):
        super().__init__(parent_process)
        self.name = "FLUID_LOUDNESS".lower()
        self.input_type = Ftypes.folder
        self.output_type = Ftypes.json
        self.data_container = multiprocessing.Manager().dict()
        self.validate_cli()

    @staticmethod
    def validate_cli():
        if not shutil.which("fluid-loudness"):
            raise BinError("fluid-loudness executable not found in PATH")

    def analyse(self, workable: str, task, progress_bar):
        src = workable
        base_name = os.path.basename(workable)
        features = os.path.join(self.TMP, f"{base_name}loudness.wav")

        loudness = fluid.loudness(
                "-source", src,
                "-windowsize", self.parameters["windowsize"],
                "-hopsize", self.parameters["hopsize"],
                "-kweighting", self.parameters["kweighting"],
                "-truepeak", self.parameters["truepeak"],
        )
        data = flucoma.utils.get_buffer(loudness)
        self.data_container[workable] = list_data

        progress_bar.update(task, advance = 1)

    def run(self):  
        """
        In this method you implement the functionality for the analyser
        """

        workables = get_workables(self.input, ('.wav'))
        
        multiproc(self.name, self.analyse, workables)

        write_json(self.output, dict(self.data_container))