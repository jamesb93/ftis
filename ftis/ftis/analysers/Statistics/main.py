import math
import numpy as np
from multiprocessing import Manager
from scipy import stats
from ftis.common.proc import multiproc
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import write_json, read_json
from ftis.common.types import Ftypes


class Statistics(FTISAnalyser):
    def __init__(self, config):
        super().__init__(config)
        self.input_type = Ftypes.json
        self.output_type = Ftypes.json
        self.stats_dict = Manager().dict()

    @staticmethod
    def calc_stats(data):
        """Given a time series calculate statistics"""
        describe = stats.describe(data)
        mean = describe.mean
        stddev = math.sqrt(describe.variance)
        skewness = describe.skewness
        kurtosis = describe.kurtosis
        minimum = describe.minmax[0]
        median = np.median(data)
        maximum = describe.minmax[1]
        return [mean, stddev, skewness, kurtosis, minimum, median, maximum]

    def get_stats(self, base_data, num_derivs: int) -> list:
        """
        Given stats on n number derivatives from initial data
        """
        container = []
        if num_derivs > 0:
            for i in range(num_derivs):
                deriv = np.diff(base_data, i + 1)
                stats = self.calc_stats(deriv)
                container.append(stats)

        elif num_derivs <= 0:
            container = self.calc_stats(base_data)

        return container

    def analyse(self, workable):
        # TODO: any dimensionality input
        element_container = []
        for row in self.data[workable]:  # for mfcc band in mfcc
            row_stats = self.get_stats(row, self.parameters["numderivs"])
            element_container.append(row_stats)

        if self.parameters["flatten"]:
            element_container = np.array(element_container)
            element_container = element_container.flatten()
            element_container = element_container.tolist()
        self.stats_dict[workable] = element_container

    def run(self):
        self.data = read_json(self.input)
        workables = [x for x in self.data.keys()]
        multiproc(self.name, self.analyse, workables)
        write_json(self.output, dict(self.stats_dict))


