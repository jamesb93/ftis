from ftis.common.analyser import FTISAnalyser
from ftis.common.io import write_json, read_json
from ftis.common.proc import singleproc
from multiprocessing import Manager
from scipy.stats import describe
from math import sqrt
import numpy as np


class Stats(FTISAnalyser):
    """Get various statistics and derivatives of those"""

    def __init__(
        self,
        numderivs=0,
        flatten=True,
        spec=["mean", "stddev", "skewness", "kurtosis", "min", "median", "max"],
        cache=False,
    ):

        super().__init__(cache=cache)
        self.numderivs = numderivs
        self.flatten = flatten
        self.spec = spec
        self.dump_type = ".json"

    def dump(self):
        write_json(self.dump_path, self.output)

    def load_cache(self):
        self.output = read_json(self.dump_path)

    @staticmethod
    def calc_stats(data, spec):
        description = describe(data)
        output = []
        if "mean" in spec:
            output.append(description.mean)
        if "stddev" in spec:
            output.append(sqrt(description.variance))
        if "skewness" in spec:
            output.append(description.skewness)
        if "kurtosis" in spec:
            output.append(description.kurtosis)
        if "minimum" in spec:
            output.append(description.minmax[0])
        if "median" in spec:
            output.append(np.median(data))
        if "maximum" in spec:
            output.append(description.minmax[1])
        return output

    def get_stats(self, base_data, num_derivs: int) -> list:
        """Given stats on n number derivatives from initial data"""
        container = []
        if num_derivs > 0:
            for i in range(num_derivs):
                deriv = np.diff(base_data, i + 1)
                container.append(self.calc_stats(deriv, self.spec))

        elif num_derivs <= 0:
            container = self.calc_stats(base_data, self.spec)
        return container

    def analyse(self, workable):
        # TODO: any dimensionality input
        element_container = []
        values = np.array(self.input[workable])
        if len(values.shape) < 2:  # single row we run the stats on that
            element_container.append(self.get_stats(values, self.numderivs))
        else:
            for row in values:  # for mfcc band in mfcc
                element_container.append(self.get_stats(row, self.numderivs))

        if self.flatten:
            element_container = np.array(element_container)
            element_container = element_container.flatten()
            element_container = element_container.tolist()
        self.buffer[workable] = element_container

    def run(self):
        self.buffer = Manager().dict()
        workables = [x for x in self.input.keys()]
        singleproc(self.name, self.analyse, workables)
        self.output = dict(self.buffer)
