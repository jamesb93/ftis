import numpy as np
from pathlib import Path
from pydub import AudioSegment
from pydub.utils import mediainfo
from ftis.common.analyser import FTISAnalyser
from ftis.common.types import Ftypes
from ftis.common.utils import samps2ms, bufspill, read_json
from ftis.common.proc import multiproc, singleproc


class ExplodeAudio(FTISAnalyser):
    def __init__(self, parent_process):
        super().__init__(parent_process)
        self.input_type = Ftypes.json
        self.output_type = Ftypes.folder

    def segment(self, workable):
        """Receives a full path to an audio file"""
        slices = self.slice_data[str(workable)]
        src = AudioSegment.from_file(workable, format="wav")
        sr = int(mediainfo(workable)["sample_rate"])

        for i, (start, end) in enumerate(zip(slices, slices[1:])):
            start = samps2ms(start, sr)
            end = samps2ms(end, sr)
            segment = src[start:end]
            segment.export(self.output / f"{i}_{workable.name}", format="wav")

    def run(self):
        self.slice_data = read_json(self.input)
        workables = [Path(x) for x in self.slice_data.keys()]
        singleproc(self.name, self.segment, workables)
