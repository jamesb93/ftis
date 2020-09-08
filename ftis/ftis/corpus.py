from pathlib import Path
import numpy as np
from ftis.common.exceptions import NoCorpusSource, InvalidSource
from ftis.common.analyser import FTISAnalyser
from ftis.common.proc import singleproc
from ftis.common.io import write_json, read_json, get_duration
from ftis.common.utils import create_hash
from flucoma.utils import get_buffer
from flucoma.fluid import stats, loudness
from rich.progress import Progress


class Corpus:
    def __init__(self, path="", file_type=[".wav", ".aiff", ".aif"]):
        self.path = path
        self.file_type = file_type
        self.items = []
        self.is_filtering = False
        self.get_items()

    def __add__(self, right):
        try:
            self.items += right.items  # this is the fastest way to merge in place
        except AttributeError:
            raise
        return self

    def get_items(self):
        if self.path == "":
            raise NoCorpusSource("Please provide a valid path for the corpus")

        self.path = Path(self.path).expanduser().resolve()

        if not self.path.exists():
            raise InvalidSource(self.path)

        if self.path.is_dir():
            self.items = [
                x for x in self.path.iterdir() if x.suffix in self.file_type
            ]
        else:
            self.items = [str(self.path)]
    
    def startswith(self, prefix: str):
        with Progress() as progress:
            task = progress.add_task("[cyan]Corpus Filtering: Name (startswith)", total=len(self.items))
            temp = []
            for x in self.items:
                if  str(x.stem).startswith(prefix):
                    temp.append(x)
                progress.update(task, advance=1)
            self.items = temp
        return self

    def endswith(self, suffix: str):
        with Progress() as progress:
            task = progress.add_task("[cyan]Corpus Filtering: Name (endswith)", total=len(self.items))
            temp = []
            for x in self.items:
                if  str(x.stem).endswith(suffix):
                    temp.append(x)
                progress.update(task, advance=1)
            self.items = temp
        return self

    def has(self, has: str):
        with Progress() as progress:
            task = progress.add_task("[cyan]Corpus Filtering: Name (has)", total=len(self.items))
            temp = []
            for x in self.items:
                if has in str(x):
                    temp.append(x)
                progress.update(task, advance=1)
            self.items = temp
        return self

    def loudness(self, min_loudness: int=0, max_loudness: int=100):
        hopsize = 4410
        windowsize = 17640
        with Progress() as progress:
            task = progress.add_task("[cyan]Corpus Filtering: Loudness", total=len(self.items))

            median_loudness = {}
            for x in self.items:
                hsh = create_hash(x, hopsize, windowsize)

                # Make sure a sane temporary path exists
                tmp = Path("/tmp") / "ftis_cache"
                tmp.mkdir(exist_ok=True)

                cache = tmp / f"{hsh}.npy"
                if not cache.exists():
                    med_loudness = get_buffer(stats(loudness(x, hopsize=hopsize, windowsize=windowsize)), "numpy")
                    np.save(cache, med_loudness)
                else:
                    med_loudness = np.load(cache, allow_pickle=True)

                median_loudness[str(x)] = med_loudness[0][5]
                progress.update(task, advance=1)

            # Get percentiles and filter
            vals = np.array([x for x in median_loudness.values()])
            min_perc = np.percentile(vals, min_loudness)
            max_perc = np.percentile(vals, max_loudness)
            self.items = [k for k, v in median_loudness.items() if v <= max_perc and v >= min_perc]
        return self

    @staticmethod
    def filter_duration(x, low: float, high: float) -> bool:
        hsh = create_hash(x, low, high)
        tmp = Path("/tmp") / "ftis_cache"
        tmp.mkdir(exist_ok=True)

        cache = tmp / f"{hsh}.npy"
        if not cache.exists():
            dur = get_duration(x)
            np.save(cache, dur)
        else:
            dur = np.load(cache)
        return dur < high and dur > low

    def duration(self, min_duration:int=0, max_duration:int=36000):
        # TODO handle min/max types that can come in so you can do percentages
        self.is_filtering = True
        self.items = [x for x in self.items if self.filter_duration(x, min_duration, max_duration)]
        return self


class Analysis:
    # TODO This could be merged directly into the corpus class where it would 
    # directly determine the type from the extension
    """This class lets you directly use analysis as an entry point to FTIS"""

    def __init__(self, path=""):
        self.path = path
        self.items = None
        self.get_items()

    def get_items(self):
        if self.path == "":
            raise NoCorpusSource("Please provide a valid path for the analysis")

        self.path = Path(self.path).expanduser().resolve()

        if not self.path.exists():
            raise InvalidSource(self.path)

        self.items = path


class PathLoader(FTISAnalyser):
    def __init__(self, file_type=[".wav", ".aiff", ".aif"], cache=False):
        super().__init__(cache=cache)
        self.output = []
        self.file_type = file_type
        self.dump_type = ".json"

    def load_cache(self):
        d = read_json(self.dump_path)
        self.output = [Path(x) for x in d["corpus_items"]]

    def dump(self):
        d = {"corpus_items": [str(x) for x in self.output]}
        write_json(self.dump_path, d)

    def collect_files(self):
        self.output = [x for x in self.input.iterdir() if x.suffix in self.file_type]

    def run(self):
        staticproc(self.name, self.collect_files)
