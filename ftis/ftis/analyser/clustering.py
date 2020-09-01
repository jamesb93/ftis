from ftis.common.analyser import FTISAnalyser
from ftis.common.proc import staticproc
from ftis.common.io import write_json, read_json
from sklearn.neighbors import KDTree as SKKDTree
from sklearn.cluster import AgglomerativeClustering as AggCluster
from joblib import dump as jdump
import numpy as np


class AgglomerativeClustering(FTISAnalyser):
    def __init__(self, numclusters=3, cache=False):
        super().__init__(cache=cache)
        self.numclusters = numclusters
        self.dump_type = ".json"

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def analyse(self):
        keys = [x for x in self.input.keys()]
        values = [x for x in self.input.values()]

        data = np.array(values)

        db = AggCluster(n_clusters=self.numclusters).fit(data)

        self.output = {}

        for audio, cluster in zip(keys, db.labels_):
            if str(cluster) in self.output:
                self.output[str(cluster)].append(audio)
            else:
                self.output[str(cluster)] = [audio]

    def run(self):
        staticproc(self.name, self.analyse)


class HDBSCAN(FTISAnalyser):
    def __init__(self, minclustersize=2, minsamples=1, cache=False):
        super().__init__(cache=cache)
        self.minclustersize = minclustersize
        self.minsamples = minsamples
        self.dump_type = ".json"

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def analyse(self):
        keys = [x for x in self.input.keys()]
        values = [x for x in self.input.values()]

        data = np.array(values)

        db = HdbscanClustering(min_cluster_size=self.minclustersize, min_samples=self.minsamples,).fit(data)

        self.output = {}

        for audio, cluster in zip(keys, db.labels_):
            if str(cluster) in self.output:
                self.output[str(cluster)].append(audio)
            else:
                self.output[str(cluster)] = [audio]

    def run(self):
        staticproc(self.name, self.analyse)


class KDTree(FTISAnalyser):
    def __init__(self, cache=False):
        super().__init__(cache=cache)

    def dump(self):
        jdump(self.model, self.model_dump)

    def analyse(self):
        data = [v for v in self.input.values()]
        keys = [k for k in self.input.keys()]
        data = np.array(data)
        self.model = SKKDTree(data)

    def run(self):
        staticproc(self.name, self.analyse)
        self.output = self.model_dump
