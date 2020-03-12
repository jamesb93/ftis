import os
import umap
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import printp, read_json, write_json
from ftis.common.types import Ftypes
from sklearn.preprocessing import MinMaxScaler, StandardScaler


class DR(FTISAnalyser):
    def __init__(self, config):
        super().__init__(config)
        self.name = "dimension_reduction"
        self.input_type = Ftypes.json
        self.output_type = Ftypes.json
        self.validate_parameters()

    def run(self):

        analysis_data = read_json(self.input)

        # scrub that metadata boy!
        try:
            del analysis_data["meta"]
        except KeyError:
            print("No Metadata or failed deletion")

        data = [v for v in analysis_data.values()]
        keys = [k for k in analysis_data.keys()]

        if self.parameters["scaling"] == "normalise":
            printp("Normalising input data")
            scaler = MinMaxScaler()
        if self.parameters["scaling"] == "standardise":
            printp("Standardising input data")
            scaler = StandardScaler()
        # data = np.array(data)
        data = scaler.fit_transform(data)

        # Fit the transform
        printp("Performing UMAP reduction")
        reduction = umap.UMAP(
            n_components=self.parameters["components"],
            n_neighbors=self.parameters["neighbours"],
            min_dist=self.parameters["mindist"],
        )
        printp("Fitting Transform")
        data = reduction.fit_transform(data)

        # Normalisation
        if self.parameters["post_scaling"] == "normalise":
            printp("Normalising for JSON output")
            post_scaling = MinMaxScaler()
        if self.parameters["post_scaling"] == "standardise":
            printp("Standardising for JSON output")
            post_scaling = StandardScaler()
        if self.parameters["post_scaling"] != "none":
            data = post_scaling.fit_transform(data)

        dictionary_format_data = {}

        printp("Outputting JSON")
        for key, value in zip(keys, data):
            dictionary_format_data[key] = value.tolist()

        write_json(self.output, dictionary_format_data)
