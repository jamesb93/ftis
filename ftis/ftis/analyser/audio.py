from ftis.common.analyser import FTISAnalyser
from ftis.common.io import write_json, read_json, peek
from ftis.common.proc import singleproc
from ftis.common.conversion import samps2ms
from shutil import copyfile
from pydub import AudioSegment
from pydub.utils import mediainfo
from pathlib import Path
from scipy.io import wavfile


class CollapseAudio(FTISAnalyser):
    def __init__(self):
        super().__init__()

    def collapse(self, workable):
        out = self.outfolder / Path(workable).name
        raw, sr = peek(workable)
        audio = None
        if raw.ndim == 1:
            audio = raw
        else:
            audio = raw.sum(axis=0) / raw.ndim
        wavfile.write(out, sr, audio)

    def run(self):
        self.outfolder = self.process.folder / f"{self.order}_{self.__class__.__name__}"
        self.outfolder.mkdir(exist_ok=True)
        singleproc(self.name, self.collapse, self.input)
        self.output = [x for x in self.outfolder.iterdir() if x.suffix == ".wav"]

class ExplodeAudio(FTISAnalyser):
    def __init__(self, cache=False):
        super().__init__(cache=cache)
        self.dump_type = ".json"

    def segment(self, workable):
        # FIXME why do i need to mport here for it to not complain
        # FIXME Can maybe just move to the top if not a slow import

        self.output_folder = self.process.folder / f"{self.order}_{self.__class__.__name__}"
        self.output_folder.mkdir(exist_ok=True)

        slices = self.input[str(workable)]

        if len(slices) == 1:
            copyfile(workable, self.output_folder / f"{workable.stem}_0.wav")

        src = AudioSegment.from_file(workable, format="wav")
        sr = int(mediainfo(workable)["sample_rate"])

        for i, (start, end) in enumerate(zip(slices, slices[1:])):
            start = samps2ms(start, sr)
            end = samps2ms(end, sr)
            segment = src[start:end]
            segment.export(self.output_folder / f"{workable.stem}_{i}.wav", format="wav")

    def load_cache(self):
        d = read_json(self.dump_path)
        self.output = [Path(x) for x in d["corpus_items"]]

    def dump(self):
        d = {"corpus_items": [str(x) for x in self.output]}
        write_json(self.dump_path, d)

    def run(self):
        workables = [Path(x) for x in self.input.keys()]
        singleproc(self.name, self.segment, workables)
        self.output = [x for x in self.output_folder.iterdir() if x.suffix in [".wav", ".aiff", ".aif"]]
