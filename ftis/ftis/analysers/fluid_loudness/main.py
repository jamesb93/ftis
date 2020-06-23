
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
from ftis.common.utils import bufspill, write_json, get_workables, filter_extensions
from ftis.common.types import Ftypes
from ftis.common.proc import multiproc


class FLUID_LOUDNESS(FTISAnalyser):
    def __init__(self, parent_process):
        super().__init__(parent_process)
        self.name = "FLUID_LOUDNESS".lower()
        self.input_type = Ftypes.folder
        self.output_type = Ftypes.json
        self.data_container = multiprocessing.Manager().dict()

    def analyse(self, workable: str, task, progress_bar):

        loudness = fluid.loudness(
                workable,
                windowsize = self.parameters["windowsize"],
                hopsize = self.parameters["hopsize"],
                kweighting = self.parameters["kweighting"],
                truepeak = self.parameters["truepeak"])
        
        self.data_container[str(workable)] = flucoma.utils.get_buffer(loudness)
        progress_bar.update(task, advance = 1)

    def run(self):  
        """
        In this method you implement the functionality for the analyser
        """
        workables = filter_extensions(
            get_workables(self.input), [".wav"])

        multiproc(self.name, self.analyse, workables)
        write_json(self.output, dict(self.data_container))