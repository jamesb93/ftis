
import subprocess
import numpy as np
from pydub import AudioSegment
from pydub.utils import mediainfo
from ftis.common.analyser import FTISAnalyser
from ftis.common.types import Ftypes
from ftis.common.utils import samps2ms, bufspill, read_json
from ftis.common.proc import multiproc


class ExplodeAudio(FTISAnalyser):
    def __init__(self, parent_process):
        super().__init__(parent_process)
        self.input_type = Ftypes.json
        self.output_type = Ftypes.folder
    
    def segment(self, filename:str, task, progress_bar):
        """Receives a full path to an audio file"""
        basic_name = filename.name
        seg_folder = self.output / basic_name
        if not seg_folder.exists():
            seg_folder.mkdir()
        slices = self.slice_data[filename] 
        src = AudioSegment.from_file(filename, format="wav")
        sr = int(mediainfo(filename)["sample_rate"])
        
        for i, (start, end) in enumerate(zip(slices, slices[1:])):
            start = samps2ms(start, sr)
            end = samps2ms(end, sr)
            segment = src[start:end]
            
            segment.export(
                seg_folder / f"{i}_{basic_name}.wav",
                format="wav"
            )

        progress_bar.update(task, advance=1)

    def run(self):
        self.slice_data = read_json(self.input)
        workables = [Path(x) for x in self.slice_data.keys()]
        multiproc(self.name, self.segment, workables)
