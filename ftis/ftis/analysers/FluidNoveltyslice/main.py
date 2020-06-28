
import os

import flucoma
import tempfile
import subprocess
import numpy as np
from shutil import rmtree
from flucoma import fluid
from multiprocessing import Manager
from ftis.common.analyser import FTISAnalyser
from ftis.common.types import Ftypes
from ftis.common.utils import get_workables, write_json, filter_extensions
from ftis.common.proc import multiproc


class FluidNoveltyslice(FTISAnalyser):
    def __init__(self, parent_process):
        super().__init__(parent_process)
        self.input_type = Ftypes.folder
        self.output_type = Ftypes.json
        self.data_container = Manager().dict()
        
    def analyse(self, workable:str):
        src = workable
        noveltyslice = fluid.noveltyslice(
            src,
            feature = self.parameters["feature"],
            fftsettings = self.parameters["fftsettings"],
            filtersize = self.parameters["filtersize"],
            minslicelength = self.parameters["minslicelength"],
            threshold = self.parameters["threshold"]
        )
        self.data_container[str(workable)] = flucoma.utils.get_buffer(noveltyslice)

    def run(self):
        workables = get_workables(self.input)
        workables = filter_extensions(workables, [".wav"])
        multiproc(self.name, self.analyse, workables)
        write_json(self.output, dict(self.data_container))
