
import os
import subprocess
import numpy as np
from pydub import AudioSegment
from pydub.utils import mediainfo
from ftis.common.analyser import FTISAnalyser
from ftis.common.types import Ftypes
from ftis.common.utils import samps2ms, bufspill, check_make, read_json
from ftis.common.proc import multiproc


class AUDIO_EXPLODE(FTISAnalyser):
    def __init__(self, parent_process):
        super().__init__(parent_process)
        self.input_type = Ftypes.json
        self.output_type = Ftypes.folder
        self.name = "AUDIO_EXPLODE".lower()
    
    def segment(self, filename:str, task, progress_bar):
        basic_name = os.path.splitext(os.path.basename(filename))[0]
        seg_folder = os.path.join(self.output, basic_name)
        check_make(seg_folder)
        slices = self.slice_data[filename] 
        src = AudioSegment.from_file(filename, format="wav")
        sr = mediainfo(filename)["sample_rate"]
        for i in range(len(slices) - 1):
            start = samps2ms(slices[i], int(sr))
            end = samps2ms(slices[i+1], int(sr))
            segment = src[start:end]
            segment.export(
                os.path.join(seg_folder, f"{i}_{basic_name}.wav"), 
                format="wav")
        progress_bar.update(task, advance=1)

    def run(self):
        self.slice_data = read_json(self.input)
        workables = [x for x in self.slice_data.keys()]
        multiproc(self.name, self.segment, workables)
