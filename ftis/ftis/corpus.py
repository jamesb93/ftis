from ftis.common.analyser import FTISAnalyser
from ftis.common.io import get_duration
from ftis.common.proc import staticproc
from pathlib import Path
from pydub.utils import mediainfo
import pickle
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
        self.dump_type = ".pkl"

    def get_items(self):
        self.output = [x for x in self.input.iterdir()]

    def filter_duration(self, x):
        dur = get_duration(x)
        return dur < self.max_dur and dur > self.min_dur

    #TODO maybe make this a csv so its readable.
    def load_cache(self):
        # self.output = read_json(self.dump_path)
        with open(self.dump_path, "rb") as f:
            self.output = pickle.load(f)

    def dump(self):
        with open(self.dump_path, "wb") as f:
            pickle.dump(self.output, f)

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
        
