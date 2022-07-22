import numpy as np
from pathlib import Path
from ftis.common.exceptions import NoCorpusSource, InvalidSource
from ftis.common.analyser import FTISAnalyser
from ftis.common.proc import singleproc
from ftis.common.io import write_json, read_json, get_duration
from ftis.common.utils import create_hash
from ftis.common.types import AudioFiles
from flucoma.utils import get_buffer
from flucoma.fluid import stats, loudness
from rich.progress import Progress
from typing import List


class Corpus:
    def __init__(self, path: str = "", file_type: List[str] = [".wav", ".aiff", ".aif"]):
        self.path = path
        self.name = self.__class__.__name__
        self.file_type: List[str] = file_type
        self.items: List = []
        self.is_filtering: bool = False
        self.chain = {}
        self.identity = {}
        if path != "":
            self.get_items()

    def create_identity(self):
        self.identity["hash"] = create_hash(self.items, self.is_filtering, self.path, self.file_type)

    def set_dump(self):
        # FIXME this is called in build_connections but we dont need it
        pass

    def __len__(self):
        return len(self.items)

    def __add__(self, right):
        try:
            self.items += right.items  # this is the fastest way to merge in place
        except AttributeError:
            raise
        return self

    def __rshift__(self, right):
        self.chain[right] = None
        return right

    def walk_chain(self) -> None:
        # Pass output to the input of all of connected things
        for forward_connection in self.chain:
            forward_connection.input = self.items
            forward_connection.walk_chain()

    def get_items(self) -> None:
        if self.path == "":
            raise NoCorpusSource("Please provide a valid path for the corpus")

        self.path = Path(self.path).expanduser().resolve()

        if not self.path.exists():
            raise InvalidSource(self.path)

        if self.path.is_dir():
            # self.items = [str(x) for x in self.path.iterdir() if x.suffix in self.file_type]
            self.items = [str(x) for x in self.path.rglob('*.wav')]
        else:
            self.items = [self.path]

    def load_items(self, items:List[Path]) -> None: 
        # Manually load items into FTIS when you're a baller
        for item in items:
            if not item.exists():
                raise InvalidSource(str.item)
        self.items = [str(x) for x in items if x.suffix in self.file_type]    

    def startswith(self, prefix: str):
        with Progress() as progress:
            task = progress.add_task("[cyan]Corpus Filtering: Name (startswith)", total=len(self.items))
            temp = []
            for x in self.items:
                if str(x.stem).startswith(prefix):
                    temp.append(x)
                progress.update(task, advance=1)
            self.items = temp
        return self

    def endswith(self, suffix: str):
        with Progress() as progress:
            task = progress.add_task("[cyan]Corpus Filtering: Name (endswith)", total=len(self.items))
            temp = []
            for x in self.items:
                if str(x.stem).endswith(suffix):
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

    def loudness(self, min_loudness: int = 0, max_loudness: int = 100):
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
                    med_loudness = get_buffer(
                        stats(loudness(x, hopsize=hopsize, windowsize=windowsize)), "numpy"
                    )
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
    def filter_duration(x, low, high, units:str) -> bool:
        hsh = create_hash(x, low, high)
        tmp = Path("/tmp") / "ftis_cache"
        tmp.mkdir(exist_ok=True)

        cache = tmp / f"{hsh}.npy"
        if not cache.exists():
            dur = get_duration(x, units)
            np.save(cache, dur)
        else:
            dur = np.load(cache)

        # Logic for returning the truth
        if low != None and high != None:
            return dur <= high and dur >= low
        if low == None:
            return dur <= high
        if high == None:
            return dur >= low
        if low == None and high == None:
            return False

    def duration(self, 
        min_duration = None, 
        max_duration = None, 
        units: str = 'samples'
    ):
        self.is_filtering = True
        self.items = [
            x 
            for x in self.items 
            if self.filter_duration(
                x, 
                min_duration, 
                max_duration,
                units
            )]
        return self
