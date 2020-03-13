import os
import math
import numpy as np
from scipy import stats
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import printp, write_json, read_json
from ftis.common.types import Ftypes


class STATS(FTISAnalyser):
    def __init__(self, config):
        super().__init__(config)
        self.name = "stats"
        self.stats_dict = {}
        self.input_type = Ftypes["json"]
        self.output_type = Ftypes["json"]
        self.validate_parameters()

    @staticmethod
    def calc_stats(data: np.array):
        """
        Given a time series calculate statistics
        """
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

    def run(self):
        data = read_json(self.input)
        try:
            del data["meta"]
        except KeyError:
            print("\nNo metadata to delete")

        #TODO: serialise and kind of dimension input
        for element in data:  # for key (audio file ) in dict
            element_container = []
            for row in data[element]:  # for mfcc band in mfcc
                row_stats = self.get_stats(row, self.parameters["numderivs"])
                element_container.append(row_stats)

            if self.parameters["flatten"]:
                element_container = np.array(element_container)
                element_container = element_container.flatten()
                element_container = element_container.tolist()
            self.stats_dict[element] = element_container

        write_json(self.output, dict(self.stats_dict))

        printp("Finished getting stats")
