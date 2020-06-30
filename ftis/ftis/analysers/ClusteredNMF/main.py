import numpy as np
import hdbscan
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import read_json, write_json
from ftis.common.proc import singleproc
from ftis.common.types import Ftypes
from sklearn.cluster import AgglomerativeClustering
from flucoma import fluid
from flucoma.utils import get_buffer, cleanup
from scipy.io import wavfile
from scipy.signal import savgol_filter


class ClusteredNMF(FTISAnalyser):
    def __init__(self, config):
        super().__init__(config)
        self.input_type = Ftypes.folder
        self.output_type = Ftypes.folder

    def analyse(self, workable):
        nmf = fluid.nmf(
            workable,
            iterations=self.parameters["iterations"],
            components=self.parameters["components"],
            fftsettings=self.parameters["fftsettings"],
        )
        bases = get_buffer(nmf.bases, "numpy")
        bases_smoothed = np.zeros_like(bases)

        for i, x in enumerate(bases):
            bases_smoothed[i] = savgol_filter(
                x, self.parameters["smoothing"], self.parameters["polynomial"]
            )

        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.parameters["clustersize"], min_samples=self.parameters["samples"],
        )

        cluster_labels = clusterer.fit_predict(bases)
        unique_clusters = list(dict.fromkeys(cluster_labels))

        sound = get_buffer(resynth, "numpy")

        for x in unique_clusters:
            summed = np.zeros_like(sound[0])  # make an empty numpy array of same size
            base = workable.name
            output = self.output / f"{base}_{x}.wav"
            for idx, cluster in enumerate(cluster_labels):
                if cluster == x:
                    summed += sound[idx]
            wavfile.write(output, 44100, summed)

    def run(self):
        workables = [k for k in self.input.iterdir() if k.name != ".DS_Store"]
        singleproc(self.name, self.analyse, workables)
        cleanup()
