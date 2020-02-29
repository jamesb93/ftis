import os
import umap
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import printp, read_json, write_json
from sklearn.preprocessing import MinMaxScaler, StandardScaler


class DR(FTISAnalyser):
    def __init__(self, config):
        super().__init__(config)
        self.name = "dimension_reduction"
        self.validate_parameters()

    def set_output(self, base_dir: str):
        self.output = os.path.join(base_dir, f"{self.name}.json")

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
        printp("Normalising for JSON output")
        post_normalisation = MinMaxScaler()
        data = post_normalisation.fit_transform(data)

        normalised_data_points = {}

        printp("Outputting JSON")
        for key, value in zip(keys, data):
            normalised_data_points[key] = value.tolist()

        write_json(self.output, normalised_data_points)
