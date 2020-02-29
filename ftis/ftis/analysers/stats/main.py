import os
import math
import numpy as np
from scipy import stats
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import printp, write_json, read_json


class STATS(FTISAnalyser):
    def __init__(self, config):
        super().__init__(config)
        self.name = "stats" #TODO: grab this from the parent folder to only have to change one place
        self.validate_parameters()

    def set_output(self, base_dir: str):
        self.output = os.path.join(base_dir, f"{self.name}.json")

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

    def get_stats(self, base_data, num_derivs) -> list:
        """
        Given stats on n number derivatives from initial data
        """
        container = []
        for i in range(num_derivs):
            deriv = np.diff(base_data, i + 1)
            stats = self.calc_stats(deriv)
            container.append(stats)
        return container



    def run(self):
        data = read_json(self.input)
        stats_dict = {}
        try:
            del data["meta"]
        except KeyError:
            print("No metadata to delete")

        for element in data:  # for key (audio file ) in dict
            element_container = []
            print(element)
            for row in data[element]:  # for mfcc band in mfcc
                row_stats = self.get_stats(row, self.parameters["numderivs"]) # get the stats for each mfcc band
                element_container.append(row_stats) # 

            if self.parameters["flatten"]:
                element_container = np.array(element_container) # Convert to numpy array
                element_container = element_container.flatten()
                element_container = element_container.tolist()
            stats_dict[element] = element_container
        
        write_json(self.output, stats_dict)

        printp("Finished getting stats")