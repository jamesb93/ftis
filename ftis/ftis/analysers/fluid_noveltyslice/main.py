
import os
import multiprocessing
import flucoma
import tempfile
import subprocess
import numpy as np
from shutil import rmtree
from flucoma import fluid
from ftis.common.analyser import FTISAnalyser
from ftis.common.types import Ftypes
from ftis.common.utils import nextpow, get_workables, write_json, bufspill
from ftis.common.proc import multiproc


class FLUID_NOVELTYSLICE(FTISAnalyser):
    def __init__(self, parent_process):
        """
        This is the bare minimum required to instantiate the object.
        """
        super().__init__(parent_process)
        self.input_type = Ftypes.folder
        self.output_type = Ftypes.json
        self.name = "FLUID_NOVELTYSLICE".lower()
        self.fftsettings = []
        self.data_container = multiprocessing.Manager().dict()
        self.TMP = tempfile.mkdtemp()
        
    def analyse(self, workable:str, task, progress_bar):
        src = workable
        base_name = os.path.basename(workable)
        indices = os.path.join(self.TMP, f"{base_name}_nsindices.wav")

        noveltyslice = fluid.noveltyslice(
                src
                feature = self.parameters["feature"],
                fftsettings = self.parameters["fftsettings"]
                filtersize = self.parameters["filtersize"],
                minslicelength = self.parameters["minslicelength"],
                threshold = self.parameters["threshold"],
        )

        self.data_container[workable] = flucoma.utils.get_buffer(noveltyslice)
        progress_bar.update(task, advance = 1)

    def run(self):
        """ In this method you implement the functionality for the analyser"""
        self.fftsettings = self.parameters["fftsettings"].split(" ")
        workables = get_workables(self.input, ['.wav'])
        multiproc(self.name, self.analyse, workables)
        write_json(self.output, dict(self.data_container))
        rmtree(self.TMP)
