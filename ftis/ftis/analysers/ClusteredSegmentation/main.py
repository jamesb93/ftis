import numpy as np
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import read_json, write_json
from ftis.common.proc import multiproc
from ftis.common.types import Ftypes
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.cluster import AgglomerativeClustering as ag
from flucoma import fluid
from flucoma.utils import get_buffer
from multiprocessing import Manager


class ClusteredSegmentation(FTISAnalyser):
    """https://github.com/jamesb93/emexperiments/blob/master/segmentation_scripts/clustered_segmentation.py"""
    def __init__(self, config):
        super().__init__(config)
        self.name = "ClusteredSegmentation"
        self.input_type = Ftypes.json
        self.output_type = Ftypes.json
        self.data_container = Manager().dict()

    def analyse(self, workable):
        slices = self.input_data[workable]
        slices = [int(x) for x in slices] # lets test this out later
        count = 0
        standardise = StandardScaler()
        model = ag(n_clusters=self.parameters["numclusters"])

        while (count + self.parameters["windowsize"]) <= len(slices):
            indices = slices[count:count + self.parameters["windowsize"]] #create a section of the indices in question
            data = []
            for i, (start, end) in enumerate(zip(indices, indices[1:])):

                mfcc = fluid.mfcc(
                    workable, 
                    fftsettings = [2048, -1, -1],
                    startframe = start,
                    numframes = end-start)

                stats = get_buffer(
                    fluid.stats(mfcc,
                        numderivs = 1
                    ), "numpy")

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
                        pass # TODO fix later
            count += 1
            self.data_container[workable] = slices\

    def run(self):
        self.input_data = read_json(self.input)
        workables = [str(k) for k in self.input_data]
        multiproc(self.name, self.analyse, workables)
        write_json(self.output, dict(self.data_container))

