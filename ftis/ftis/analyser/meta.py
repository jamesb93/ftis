from ftis.common.analyser import FTISAnalyser
from ftis.common.io import write_json, read_json
from ftis.common.proc import singleproc, multiproc
from multiprocessing import Manager
from scipy.signal import savgol_filter
from scipy.io import wavfile
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from flucoma import fluid
from flucoma.utils import get_buffer
import numpy as np
from ftis.common.types import Indices
import hdbscan
from pathlib import Path


class ClusteredNMF(FTISAnalyser):
    def __init__(
        self,
        iterations=100,
        components=10,
        fftsettings=[4096, 1024, 4096],
        smoothing=11,
        polynomial=2,
        min_cluster_size=2,
        min_samples=2,
        cluster_selection_method="eom",
        cache=False,
    ):
        super().__init__(cache=cache)
        self.components = components
        self.iterations = iterations
        self.fftsettings = fftsettings
        self.smoothing = smoothing
        self.polynomial = polynomial
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.cluster_selection_method = cluster_selection_method
        self.dump_type = ".json"

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def analyse(self, workable):
        nmf = fluid.nmf(
            workable,
            iterations=self.iterations,
            components=self.components,
            fftsettings=self.fftsettings,
        )
        bases = get_buffer(nmf.bases, "numpy")
        bases_smoothed = np.zeros_like(bases)

        for i, x in enumerate(bases):
            bases_smoothed[i] = savgol_filter(x, self.smoothing, self.polynomial)

        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            cluster_selection_method=self.cluster_selection_method,
        )

        cluster_labels = clusterer.fit_predict(bases_smoothed)
        unique_clusters = list(dict.fromkeys(cluster_labels))

        sound = get_buffer(nmf.resynth, "numpy")

        for x in unique_clusters:
            summed = np.zeros_like(sound[0])  # make an empty numpy array of same size
            base = Path(workable).name
            output = self.output / f"{base}_{x}.wav"
            for idx, cluster in enumerate(cluster_labels):
                if cluster == x:
                    summed += sound[idx]
            wavfile.write(output, 44100, summed)

    def run(self):
        self.output = self.process.sink / f"{self.order}_{self.__class__.__name__}"
        self.output.mkdir(exist_ok=True)
        singleproc(self.name, self.analyse, self.input)


class ClusteredSegmentation(FTISAnalyser):
    def __init__(self, numclusters=2, windowsize=4, numderivs=0, fftsettings=[1024, -1, -1], cache=False):
        super().__init__(cache=cache)
        self.input_type = (Indices, )
        self.output_type = Indices
        self.numclusters = numclusters
        self.windowsize = windowsize
        self.numderivs = numderivs
        self.fftsettings = fftsettings 

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def analyse(self, workable):
        slices = self.input[workable]
        if len(slices) == 1:
            self.buffer[workable] = slices
            return
        count = 0
        standardise = StandardScaler()
        model = AgglomerativeClustering(n_clusters=self.numclusters)

        while (count + self.windowsize) <= len(slices):
            indices = slices[count : count + self.windowsize]  # create a section of the indices in question
            data = []
            for _, (start, end) in enumerate(zip(indices, indices[1:])):

                mfccs = fluid.mfcc(
                    workable,
                    fftsettings=self.fftsettings,
                    startframe=int(start),
                    numframes=int(end - start),
                )

                stats = get_buffer(fluid.stats(mfccs, numderivs=self.numderivs), "numpy")

                data.append(stats.flatten())

            data = standardise.fit_transform(data)

            cluster = model.fit(data)
            cur = -2
            for j, c in enumerate(cluster.labels_):
                prev = cur
                cur = c
                if cur == prev:
                    try:
                        slices.pop(j + count)
                    except IndexError:
                        pass  # FIXME why are some indices erroring?
            count += 1
        self.buffer[workable] = slices

    def run(self):
        self.buffer = Manager().dict()
        multiproc(self.name, self.analyse, self.input)
        self.output = dict(self.buffer)