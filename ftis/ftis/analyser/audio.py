from ftis.common.analyser import FTISAnalyser
from ftis.common.io import write_json, read_json, peek, get_sr
from ftis.common.proc import multiproc, singleproc
from ftis.common.conversion import samps2ms
from shutil import copyfile
from pathlib import Path
from ftis.common.types import AudioFiles, Indices
import soundfile as sf

class CollapseAudio(FTISAnalyser):
    def __init__(self, cache=False):
        super().__init__(cache=cache)

    def collapse(self, workable):
        out = self.outfolder / Path(workable).name
        raw, sr = sf.read(workable, dtype="float32")
        audio = None
        if raw.ndim == 1:
            audio = raw
        else:
            audio = raw.transpose().sum(axis=0) / raw.ndim
        sf.write(out, audio, sr, "PCM_32")

    def run(self):
        self.outfolder = (
            self.process.sink / 
            f"{self.order}.{self.suborder}-{self.parent_string}"
        )
        self.outfolder.mkdir(exist_ok=True)
        multiproc(self.name, self.collapse, self.input)
        self.output = AudioFiles([x for x in self.outfolder.iterdir()])


class ExplodeAudio(FTISAnalyser):
    def __init__(self, cache=False):
        super().__init__(cache=cache)
        self.dump_type = ".json"

    def load_cache(self):
        d = read_json(self.dump_path)
        self.output = [x for x in d["corpus_items"]]

    def dump(self):
        d = {"corpus_items": [str(x) for x in self.output]}
        write_json(self.dump_path, d)

    def segment(self, workable):
        slices = [int(x) for x in self.input[workable]] # explicitly convert to integers
        stem = Path(workable).stem
        if len(slices) == 1:
            output_location = self.outfolder / f"{stem}_0.wav"
            copyfile(workable, output_location)
        else:
            data, sr = sf.read(workable, dtype="float32")
            # Append the right boundary if it isnt already there
            if data.shape[0] != slices[-1]:
                 slices.append(data.shape[0])

            for i, (start, end) in enumerate(zip(slices, slices[1:])):
                segment = data[start:end]
                output_location = self.outfolder / f"{stem}_{i}.wav"
                sf.write(output_location, segment, sr, "PCM_32")

    def run(self):
        self.outfolder = (
            self.process.sink / 
            f"{self.order}.{self.suborder}-{self.parent_string}"
        )
        self.outfolder.mkdir(exist_ok=True)
        singleproc(self.name, self.segment, self.input)
        self.output = [str(x) for x in self.outfolder.iterdir()]
