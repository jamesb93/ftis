import numpy as np
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import read_json, write_json
from ftis.common.proc import multiproc
from ftis.common.types import Ftypes
from sklearn.cluster import AgglomerativeClustering
from flucoma import fluid
from flucoma.utils import get_buffer
from multiprocessing import Manager


class ClusteredNMF(FTISAnalyser):
    """https://github.com/jamesb93/emexperiments/blob/master/segmentation_scripts/clustered_segmentation.py"""
    def __init__(self, config):
        super().__init__(config)
        self.name = "ClusteredNMF"
        self.input_type = Ftypes.json
        self.output_type = Ftypes.json
        self.data_container = Manager().dict()

    def analyse(self, workable):
        print(workable)
        # nmf = fluid.nmf(workable)

    def run(self):
        self.input_data = read_json(self.input)
        workables = [str(k) for k in self.input_data]
        print(workables)
        # multiproc(self.name, self.analyse, workables)
        # write_json(self.output, dict(self.data_container))

