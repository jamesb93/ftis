import numpy as np
from flucoma.fluid import loudness, stats
from flucoma.utils import get_buffer
from ftis.common.proc import staticproc
from ftis.common.utils import create_hash
from ftis.common.io import get_duration, write_json, read_json
from ftis.common.analyser import FTISAnalyser
from pathlib import Path


class Duration(FTISAnalyser):
    def __init__(self, min_dur=0, max_dur=36000, cache=False):  # 10 hours of audio
        super().__init__(cache=cache)
        self.output = []
        self.min_dur: int = min_dur
        self.max_dur: int = max_dur
        self.dump_type = ".json"

    def load_cache(self):
        d = read_json(self.dump_path)
        self.output = [Path(x) for x in d["corpus_items"]]

    def dump(self):
        d = {"corpus_items": [str(x) for x in self.output]}
        write_json(self.dump_path, d)

    def filter_duration(self, x):
        dur = get_duration(x)
        return dur < self.max_dur and dur > self.min_dur

    def filter_items(self):
        self.output = [x for x in self.input if self.filter_duration(x)]

    def run(self):
        staticproc(self.name, self.filter_items)


class Loudness(FTISAnalyser):
    """A way to filter corpus items after they have been loaded by the corpus loader"""

    def __init__(self, min_loudness=0, max_loudness=100, cache=False):
        super().__init__(cache=cache)
        self.min_loudness: float = min_loudness
        self.max_loudness: float = max_loudness
        self.dump_type = ".json"

    def load_cache(self):
        d = read_json(self.dump_path)
        self.output = [Path(x) for x in d["corpus_items"]]

    def dump(self):
        d = {"corpus_items": [str(x) for x in self.output]}
        write_json(self.dump_path, d)

    def analyse_items(self):
        # TODO import this function from a global place that can be used in CORPUS too
        median_loudness = {}
        for x in self.input:
            hsh = create_hash(x, self.min_loudness, self.max_loudness)
            cache = self.process.cache / f"{hsh}.npy"
            if not cache.exists():
                med_loudness = get_buffer(stats(loudness(x, hopsize=4410, windowsize=17640)), "numpy")
                np.save(cache, med_loudness)
            else:
                med_loudness = np.load(cache, allow_pickle=True)

            median_loudness[str(x)] = med_loudness[0][5]
        vals = np.array([x for x in median_loudness.values()])
        min_perc = np.percentile(vals, self.min_loudness)
        max_perc = np.percentile(vals, self.max_loudness)
        self.output = [k for k, v in median_loudness.items() if v <= max_perc and v >= min_perc]

    def run(self):
        staticproc(self.name, self.analyse_items)
