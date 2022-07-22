from ftis.common.analyser import FTISAnalyser
from ftis.common.io import write_json, read_json, get_sr
from ftis.common.proc import multiproc, singleproc
from ftis.common.utils import create_hash
from ftis.common.types import Indices, AudioFiles, Data
from multiprocessing import Manager
from flucoma.utils import get_buffer
from flucoma import fluid
import numpy as np

class Loudness(FTISAnalyser):
    def __init__(self, windowsize=17640, hopsize=4410, kweighting=1, truepeak=1, 
        cache=False,
        pre=None,
        post=None
     ):
        super().__init__(cache=cache, pre=pre, post=post)
        self.input_type = (AudioFiles, Indices)
        self.output_type = Data
        self.windowsize = windowsize
        self.hopsize = hopsize
        self.kweighting = kweighting
        self.truepeak = truepeak

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def analyse(self, workable):
        print(workable)
        hsh = create_hash(workable, self.identity)
        cache = self.process.cache / f"{hsh}.npy"

        if cache.exists():
            loudness = np.load(cache, allow_pickle=True)
        else:
            loudness = get_buffer(
                fluid.loudness(
                    str(workable),
                    windowsize=self.windowsize,
                    hopsize=self.hopsize,
                    kweighting=self.kweighting,
                    truepeak=self.truepeak,
                ), "numpy",
            )
            np.save(cache, loudness)
        self.buffer[str(workable)] = loudness.tolist()

    def run(self):
        self.buffer = Manager().dict()
        singleproc(self.name, self.analyse, self.input)
        self.output = dict(self.buffer)


class Pitch(FTISAnalyser):
    def __init__(self, 
        algorithm=2,
        minfreq=20,
        maxfreq=10000.0,
        unit=0,
        fftsettings=[1024, -1, -1],
        cache=False,
        pre=None,
        post=None
    ):
        super().__init__(cache=cache, pre=pre, post=post)
        self.input_type = (AudioFiles, Indices)
        self.output_type = Data
        self.algorithm=algorithm
        self.minfreq=minfreq
        self.maxfreq=maxfreq
        self.unit=unit
        self.fftsettings=fftsettings

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def analyse(self, workable):
        hsh = create_hash(workable, self.identity)
        cache = self.process.cache / f"{hsh}.npy"

        if cache.exists():
            pitch = np.load(cache, allow_pickle=True)
        else:
            pitch = get_buffer(
                fluid.pitch(
                    str(workable),
                    algorithm=self.algorithm,
                    minfreq=self.minfreq,
                    maxfreq=self.maxfreq,
                    unit=self.unit,
                    fftsettings=self.fftsettings
                ), "numpy",
            )
            np.save(cache, pitch)
        self.buffer[str(workable)] = pitch.tolist()

    def run(self):
        self.buffer = Manager().dict()
        singleproc(self.name, self.analyse, self.input)
        self.output = dict(self.buffer)


class MFCC(FTISAnalyser):
    def __init__(self,
        fftsettings=[1024, 512, 1024],
        numbands=40,
        numcoeffs=13,
        minfreq=80,
        maxfreq=20000,
        cache=False,
    ):
        super().__init__(cache=cache)
        self.input_type = (AudioFiles, Indices)
        self.output_type = Data
        self.fftsettings = fftsettings
        self.numbands = numbands
        self.numcoeffs = numcoeffs
        self.minfreq = minfreq
        self.maxfreq = maxfreq

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def analyse(self, workable):
        hsh = create_hash(workable, self.identity)
        cache = self.process.cache / f"{hsh}.npy"
        if cache.exists():
            mfcc = np.load(cache, allow_pickle=True)
        else:
            mfcc = get_buffer(
                fluid.mfcc(
                    str(workable),
                    fftsettings=self.fftsettings,
                    numbands=self.numbands,
                    numcoeffs=self.numcoeffs,
                    minfreq=self.minfreq,
                    maxfreq=self.maxfreq,
                ), "numpy",
            )
            np.save(cache, mfcc)
        self.buffer[str(workable)] = mfcc.tolist()

    def run(self):
        self.buffer = Manager().dict()
        singleproc(self.name, self.analyse, self.input)
        self.output = dict(self.buffer)



# Slicing

class Onsetslice(FTISAnalyser):
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
                ), "numpy",
            )
        else:
            slice_output = get_buffer(cache)

        self.buffer[str(workable)] = slice_output.tolist()

    def run(self):
        self.buffer = Manager().dict()
        singleproc(self.name, self.analyse, self.input)
        self.output = dict(self.buffer)


class Noveltyslice(FTISAnalyser):
    def __init__(
        self,
        algorithm=0,
        fftsettings=[1024, 512, 1024],
        filtersize=1,
        minslicelength=2,
        threshold=0.5,
        kernelsize=3,
        cache=False,
    ):
        super().__init__(cache=cache)
        self.algorithm = algorithm
        self.fftsettings = fftsettings
        self.filtersize = filtersize
        self.minslicelength = minslicelength
        self.threshold = threshold
        self.kernelsize = 3

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def analyse(self, workable):
        noveltyslice = fluid.noveltyslice(
            workable,   
            algorithm=self.algorithm,
            fftsettings=self.fftsettings,
            filtersize=self.filtersize,
            minslicelength=self.minslicelength,
            threshold=self.threshold,
        )
        self.buffer[workable] = [int(x) for x in get_buffer(noveltyslice)]

    def run(self):
        self.buffer = Manager().dict()
        multiproc(self.name, self.analyse, self.input)
        self.output = dict(self.buffer)


