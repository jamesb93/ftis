import numpy as np
from pathlib import Path
from ftis.common.analyser import FTISAnalyser
from ftis.common.types import Ftypes
from ftis.common.utils import write_json
from ftis.common.proc import multiproc
from untwist import transforms
from untwist import data
from multiprocessing import Manager

class Flux(FTISAnalyser):
    def __init__(self, parent_process):
        super().__init__(parent_process)
        self.input_type = Ftypes.folder
        self.output_type = Ftypes.json

    def flux(self, workable):
        audio = data.Wave.read(str(workable))
        if audio.is_stereo():
            audio = np.sum(audio, axis=1)
        fft = transforms.STFT(
            fft_size=self.parameters["windowsize"],
            hop_size=self.parameters["hopsize"]
            ).process(audio)
        
        self.data[str(workable)] = list(
            np.sum(np.abs(np.diff(np.abs(fft))),
            axis=0)) #this is the flux calculation here

    def run(self):
        self.data = Manager().dict()
        workables = [x for x in self.input.iterdir() if x.suffix == ".wav"]
        multiproc(self.name, self.flux, workables)
        write_json(self.output, dict(self.data))

