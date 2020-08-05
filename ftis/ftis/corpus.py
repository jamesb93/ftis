from ftis.common.analyser import FTISAnalyser
from ftis.common.io import get_duration, write_json, read_json
from ftis.common.proc import staticproc
from pathlib import Path
from flucoma.fluid import loudness, stats
from flucoma.utils import get_buffer
from ftis.common.exceptions import AnalyserParameterInvalid
import numpy as np
# The corpusloader will be a special kind of analyser used for preparing sound file batches

class CorpusLoader(FTISAnalyser):
    def __init__(self, 
        min_dur=0, 
        max_dur=36000, # 10 hours of audio 
        file_type=[".wav"], 
        cache=False
    ):
        super().__init__(cache=cache)
        self.output = []
        self.min_dur:int = min_dur
        self.max_dur:int = max_dur
        self.file_type = file_type
        self.dump_type = ".json"

    def load_cache(self):
        d = read_json(self.dump_path)
        self.output = [Path(x) for x in d["corpus_items"]]

    def dump(self):
        d = {"corpus_items" : [str(x) for x in self.output]}
        write_json(self.dump_path, d)

    def get_items(self):
        self.output = [x for x in self.input.iterdir()]

    def filter_duration(self, x):
        dur = get_duration(x)
        return dur < self.max_dur and dur > self.min_dur

    def filter_items(self):
        # Filter by the extension
        self.output = [x for x in self.output if x.suffix in self.file_type]
        if self.min_dur != 0 or self.max_dur != 36000: # if not defaults
            self.output = [x for x in self.output if self.filter_duration(x)]
    
    def create_corpus(self):
        self.get_items()
        self.filter_items()

    def run(self):
        staticproc(self.name, self.create_corpus)

class CorpusFilter(FTISAnalyser):
    """A way to filter corpus items after they have been loaded by the corpus loader"""
    def __init__(self,
        min_loudness=0,
        max_loudness=100,
        cache=False
    ):
        super().__init__(cache=cache)
        self.min_loudness:float = min_loudness
        self.max_loudness:float = max_loudness
        self.dump_type = ".json"

    def load_cache(self):
        d = read_json(self.dump_path)
        self.output = [Path(x) for x in d["corpus_items"]]

    def dump(self):
        d = {"corpus_items" : [str(x) for x in self.output]}
        write_json(self.dump_path, d)

    def analyse_items(self):
        self.median_loudness = {}
        for x in self.input:
            med_loudness = get_buffer(
                stats(
                    loudness(x, hopsize=4410, windowsize=17640)
                ), 
                "numpy"
            )
            self.median_loudness[str(x)] = med_loudness[0][5]

    def filter_items(self):
        # get the required percentile
        vals = np.array([x for x in self.median_loudness.values()])
        self.min_perc = np.percentile(vals, self.min_loudness)
        self.max_perc = np.percentile(vals, self.max_loudness)
        self.output = [k for k, v in self.median_loudness.items() if v <= self.max_perc and v >= self.min_perc]

    def filter_corpus(self):
        self.analyse_items()
        self.filter_items()

    def run(self):
        # let's do an idiot check
        if self.min_loudness == 0 and self.max_loudness == 100:
            self.output = self.input # bypass
        else:
            staticproc(self.name, self.filter_corpus)
        
