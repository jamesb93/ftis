import os
from shutil import copytree, rmtree, copyfile
from pathlib import Path
from ftis.common.analyser import FTISAnalyser
from ftis.common.io import write_json
from subprocess import call


class Visualiser(FTISAnalyser):
    def __init__(self, cache=False):
        super().__init__(cache=cache)
        self.data: dict = {"data": []}

    def check_dimensions(self):
        self.vals = [v for v in self.input.values()]
        self.keys = [k for k in self.input.keys()]

    # def copy_audio(self):
    #     for k in self.keys:
    #         copyfile()

    def fmt(self):
        """Format JSON for threejs"""
        for k, v in zip(self.keys, self.vals):
            d = {"name": k, "x": v[0], "y": v[1], "z": v[2]}
            self.data["data"].append(d)

    def run(self):
        self.output = self.process.folder / f"{self.order}_{self.__class__.__name__}"
        self.output.mkdir(exist_ok=True)
        self.check_dimensions()
        # self.copy_audio()
        self.fmt()
        script = Path(__file__).resolve()
        # copy data and assets
        web_assets = script.parent / "web_assets"
        dest = self.output / "web_assets"
        if dest.exists():
            rmtree(dest)
        copytree(web_assets, self.output / "web_assets")
        write_json(self.output / "web_assets" / "plot.json", self.data)

        # cmd = [
        #     "cd",
        #     str(self.output / "web_assets" / "html"),
        #     "&&"
        #     "python",
        #     "-m",
        #     "http.server"
        # ]
        # f = call(cmd)
        # print(f)
