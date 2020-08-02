from ftis.common.analyser import FTISAnalyser
from ftis.common.io import get_duration
from pathlib import Path
from pydub.utils import mediainfo
# The corpusloader will be a special kind of analyser used for preparing sound file batches

class CorpusLoader(FTISAnalyser):

    def __init__(self, 
        min_dur=0, 
        max_dur=0, 
        file_type=[".wav"], 
        cache=False
    ):
        super().__init__(cache=cache)
        self.output = []
        self.min_dur:int = min_dur
        self.max_dur:int = max_dur
        self.file_type = file_type

    def get_items(self):
        self.output = [x for x in self.input.iterdir()]

    def filter_items(self):
        # Filter by the extension
        self.output = [x for x in self.output if x.suffix in self.file_type]
        #TODO optimise this part to be one big ol' filter
        if self.min_dur:
            self.output = [x for x in self.output if get_duration(x) > self.min_dur]
        if self.max_dur:
            self.output = [x for x in self.output if get_duration(x) < self.max_dur]

    def run(self):
        self.get_items()
        self.filter_items()
        
