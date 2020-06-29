import numpy as np
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import read_json, write_json
from ftis.common.types import Ftypes
from ftis.common.proc import staticproc
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.cluster import AgglomerativeClustering as ag


class AgglomerativeClustering(FTISAnalyser):
    def __init__(self, config):
        super().__init__(config)
        self.input_type = Ftypes.json
        self.output_type = Ftypes.json

    def analyse(self):
        feature = read_json(self.input)
        keys = [x for x in feature.keys()]
        values = [x for x in feature.values()]

        data = np.array(values)
        scaling = self.parameters["input_scaling"]
        if scaling:
            if scaling == "normalise":
                scaler = MinMaxScaler()
            if scaling == "standardise":
                scaler = StandardScaler()
            scaler.fit(data)
            data = scaler.transform(data)

        db = ag(n_clusters=self.parameters["numclusters"]).fit(data)

        cluster_dict = {}

        for audio, cluster in zip(keys, db.labels_):
            if str(cluster) in cluster_dict:
                cluster_dict[str(cluster)].append(audio)
            else:
                cluster_dict[str(cluster)] = [audio]

        write_json(self.output, cluster_dict)

    def run(self):
        staticproc(self.name, self.analyse)
