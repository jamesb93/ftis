import numpy as np
from pathlib import Path
from ftis.common.analyser import FTISAnalyser
from ftis.common.types import Ftypes
from ftis.common.utils import write_json, read_json
from ftis.common.proc import staticproc
from sklearn.preprocessing import MinMaxScaler

class Normalise(FTISAnalyser):
    def __init__(self, parent_process):
        super().__init__(parent_process)
        self.input_type = Ftypes.json
        self.output_type = Ftypes.json

    def analyse(self):
        scaled_data = MinMaxScaler().fit_transform(self.features)
        
        self.stddata = {}
        for k, v in zip(self.keys, scaled_data):
            self.stddata[k] = list(v)

    def run(self):
        input_data = read_json(self.input)
        self.keys = [x for x in input_data.keys()]
        self.features = [x for x in input_data.values()]
        staticproc(self.name, self.analyse)
        write_json(self.output, self.stddata)

