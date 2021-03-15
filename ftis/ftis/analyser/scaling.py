from ftis.common.analyser import FTISAnalyser
from ftis.common.io import write_json, read_json
from ftis.common.proc import staticproc
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from joblib import dump as jdump
import numpy as np


class Normalise(FTISAnalyser):
    def __init__(self, minimum=0, maximum=1, cache=False):
        super().__init__(cache=cache)
        self.min = minimum
        self.max = maximum

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def analyse(self):
        scaled_data = MinMaxScaler((self.min, self.max)).fit_transform(self.features)

        self.output = {}
        for k, v in zip(self.keys, scaled_data):
            self.output[k] = v.tolist()

    def run(self):
        self.keys = [x for x in self.input.keys()]
        self.features = [x for x in self.input.values()]
        staticproc(self.name, self.analyse)


class Standardise(FTISAnalyser):
    def __init__(self, cache=False):
        super().__init__(cache=cache)

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        jdump(self.model, self.model_dump)
        write_json(self.dump_path, self.output)

    def analyse(self):
        self.model = StandardScaler()
        self.model.fit(self.features)
        scaled_data = self.model.transform(self.features)
        self.output = {k: list(v) for k, v in zip(self.keys, scaled_data)}

    def run(self):
        self.keys = [k for k in self.input.keys()]
        self.features = [v for v in self.input.values()]
        staticproc(self.name, self.analyse)
