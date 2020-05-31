import os
import umap
import numpy as np
import hdbscan
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import printp, read_json, write_json
from ftis.common.types import Ftypes
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.cluster import DBSCAN, AgglomerativeClustering


class CLUSTER(FTISAnalyser):
    def __init__(self, config):
        super().__init__(config)
        self.name = "cluster"
        self.input_type = Ftypes.json
        self.output_type = Ftypes.json
        self.validate_parameters()

    def run(self):

        feature = read_json(self.input)
        keys = [x for x in feature.keys()]
        values = [x for x in feature.values()]

        data = np.array(values)
        scaling = self.parameters["scaling"]
        if scaling:
            if scaling == 'normalisation':
                scaler = MinMaxScaler()
            if scaling == 'standardise':
                scaler = StandardScaler()
            scaler.fit(data)
            data = scaler.transform(data)

        algorithm = self.parameters["algorithm"]
        if algorithm == 'AgglomCluster':
            db = AgglomerativeClustering(
                n_clusters=self.parameters["numclusters"]
                ).fit(data)
        if algorithm == 'HDBSCAN':
            db = hdbscan.HDBSCAN().fit(data)

        cluster_dict = {}
        
        for audio, cluster in zip(keys, db.labels_):
            if str(cluster) in cluster_dict:
                cluster_dict[str(cluster)].append(audio)
            else:
                cluster_dict[str(cluster)] = [audio]

        write_json(self.output, cluster_dict)
        printp('Clustering Complete')
