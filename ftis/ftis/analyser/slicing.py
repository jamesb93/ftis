from ftis.common.analyser import FTISAnalyser
from ftis.common.io import write_json, read_json
from ftis.common.proc import multiproc, singleproc
from ftis.common.utils import create_hash
from multiprocessing import Manager
from flucoma.utils import get_buffer
from flucoma import fluid


class FluidOnsetslice(FTISAnalyser):
    def __init__(
        self,
        fftsettings=[1024, 512, 1024],
        filtersize=5,
        framedelta=0,
        metric=0,
        minslicelength=2,
        threshold=0.5,
        cache=False,
    ):
        super().__init__(cache=cache)
        self.fftsettings = fftsettings
        self.filtersize = filtersize
        self.framedelta = framedelta
        self.metric = metric
        self.minslicelength = minslicelength
        self.threshold = threshold
        self.dump_type = ".json"

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def analyse(self, workable):
        hsh = create_hash(workable, self.identity)
        cache = self.process.cache / f"{hsh}.wav"
        if not cache.exists():
            slice_output = get_buffer(
                fluid.onsetslice(
                    workable,
                    indices=cache,
                    fftsettings=self.fftsettings,
                    filtersize=self.filtersize,
                    framedelta=self.framedelta,
                    metric=self.metric,
                    minslicelength=self.minslicelength,
                    threshold=self.threshold,
                ),
                "numpy",
            )
        else:
            slice_output = get_buffer(cache, "numpy")

        self.buffer[str(workable)] = slice_output.tolist()

    def run(self):
        self.buffer = Manager().dict()
        singleproc(self.name, self.analyse, self.input)
        self.output = dict(self.buffer)


class FluidNoveltyslice(FTISAnalyser):
    def __init__(
        self,
        feature=0,
        fftsettings=[1024, 512, 1024],
        filtersize=1,
        minslicelength=2048,
        threshold=0.5,
        cache=False,
    ):
        super().__init__(cache=cache)
        self.feature = feature
        self.fftsettings = fftsettings
        self.filtersize = filtersize
        self.minslicelength = minslicelength
        self.threshold = threshold
        self.dump_type = ".json"

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def analyse(self, workable):
        noveltyslice = fluid.noveltyslice(
            workable,
            feature=self.feature,
            fftsettings=self.fftsettings,
            filtersize=self.filtersize,
            minslicelength=self.minslicelength,
            threshold=self.threshold,
        )

        self.buffer[str(workable)] = get_buffer(noveltyslice)

    def run(self):
        self.buffer = Manager().dict()
        multiproc(self.name, self.analyse, self.input)
        self.output = dict(self.buffer)
