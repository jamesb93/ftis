import numpy as np
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import read_json, write_json
from ftis.common.proc import multiproc
from ftis.common.types import Ftypes
from sklearn.cluster import AgglomerativeClustering
from flucoma import fluid
from flucoma.utils import get_buffer

class ClusteredNMF(FTISAnalyser):
    def __init__(self, config):
        super().__init__(config)
        self.name = "ClusteredNMF"
        self.input_type = Ftypes.folder
        self.output_type = Ftypes.folder

    def analyse(self, workable):
        print('doing nmf')
        nmf = fluid.nmf(
            workable, 
            iterations=self.parameters["iterations"], 
            components=self.parameters["components"],
            fftsettings=self.parameters["fftsettings"])
        bases = get_buffer(nmf.bases, "numpy")
        bases_smoothed = np.zeros_like(bases)
        
        print('Smoothing bases')
        for i, x in enumerate(bases):
            bases_smoothed[i] = savgol_filter(x, 
                self.parameters["smoothing"], 
                self.parameters["polynomial"])
            
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.parameters["clustersize"], 
            min_samples=self.parameters["samples"])

        print('Clustering')
        cluster_labels = clusterer.fit_predict(bases)
        unique_clusters = list(dict.fromkeys(cluster_labels))

        sound = get_buffer(resynth, "numpy")

        print('Amalgamating')
        for x in unique_clusters:
            summed = np.zeros_like(sound[0]) #make an empty numpy array of same size
            base = workable.name
            output = self.output / f"{base}_{x}.wav"
            for idx, cluster in enumerate(cluster_labels):
                if cluster == x:
                    summed += sound[idx]
            wavfile.write(output, 44100, summed)

    def run(self):
        workables = [str(k) for k in self.input.iterdir() if k.name != ".DS_Store"]
        # multiproc(self.name, self.analyse, workables)
        for x in workables:
            self.analyse(x)