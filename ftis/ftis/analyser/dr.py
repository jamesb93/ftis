from ftis.common.analyser import FTISAnalyser
from ftis.common.io import write_json, read_json
from ftis.common.proc import staticproc
from umap import UMAP as umapdr
from sklearn.neural_network import MLPRegressor
from joblib import dump as jdump
import numpy as np


class UMAP(FTISAnalyser):
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

class AutoEncoder(FTISAnalyser):
    def __init__(self, 
        activation = "relu",
        learning_rate=0.001, 
        max_iter=200, 
        random_state=None,
        momentum=0.9
        n_iter_no_change=10,
        tapout=0,
        hidden_layer_sizes=(100)
        cache=False):
        super().__init__(cache=cache)
        self.activation = activation
        self.learning_rate = learning_rate
        self.max_iter= max_iter
        self.random_state = random_state
        self.momentum = momentum
        self.n_iter_no_change = n_iter_no_change
        self.tapout = tapout
        self.hidden_layer_sizes = hidden_layer_sizes
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

        self.model = MLPRegressor(
            activation= self.activation,
            learning_rate= self.learning_rate,
            max_iter = self.max_iter,
            random_state = self.random_state,
            momentum= self.momentum,
            n_iter_no_change = self.n_iter_no_change,
            hidden_layer_sizes = self.hidden_layer_sizes
        )
        self.model.fit(data, data)

        


        self.output = {k: v.tolist() for k, v in zip(keys, transformed_data)}

    def run(self):
        staticproc(self.name, self.analyse)
