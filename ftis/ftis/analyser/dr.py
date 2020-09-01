from ftis.common.analyser import FTISAnalyser
from ftis.common.io import write_json, read_json
from ftis.common.proc import staticproc
from umap import UMAP as umapdr
from joblib import dump as jdump

import numpy as np


class UMAP(FTISAnalyser):
    """Dimension reduction with UMAP algorithm"""

    def __init__(self, mindist=0.01, neighbours=7, components=2, cache=False):
        super().__init__(cache=cache)
        self.mindist = mindist
        self.neighbours = neighbours
        self.components = components
        self.output = {}
        self.dump_type = ".json"

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        jdump(self.model, self.model_dump)
        write_json(self.dump_path, self.output)

    def analyse(self):
        data = [v for v in self.input.values()]
        keys = [k for k in self.input.keys()]

        data = np.array(data)

        self.model = umapdr(n_components=self.components, n_neighbors=self.neighbours, min_dist=self.mindist, random_state=42)
        self.model.fit(data)
        transformed_data = self.model.transform(data)

        self.output = {k: v.tolist() for k, v in zip(keys, transformed_data)}

    def run(self):
        staticproc(self.name, self.analyse)
