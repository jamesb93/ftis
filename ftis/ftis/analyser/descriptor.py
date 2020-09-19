from ftis.common.analyser import FTISAnalyser
from ftis.common.proc import staticproc, multiproc, singleproc
from ftis.common.io import write_json, read_json
from ftis.common.utils import create_hash
from flucoma.utils import get_buffer
from flucoma import fluid
from multiprocessing import Manager
import numpy as np
import librosa

class Flux(FTISAnalyser):
    def __init__(self, windowsize=1024, hopsize=512, cache=False):
        super().__init__(cache=cache)
        self.windowsize = windowsize
        self.hopsize = hopsize
        self.dump_type = ".json"

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def flux(self, workable):
        hsh = create_hash(workable, self.identity)
        cache = self.process.cache / f"{hsh}.npy"

        if not cache.exists():   
            y, _= librosa.load(workable)
            fft = librosa.stft(y, win_length=self.windowsize, hop_length=self.hopsize)
            flux = np.sum(np.abs(np.diff(np.abs(fft))), axis=0)
            np.save(cache, flux)
        else:
            flux = np.load(cache)
        self.buffer[str(workable)] = flux.tolist()
    
    def run(self):
        self.buffer = Manager().dict()
        multiproc(self.name, self.flux, self.input)
        self.output = dict(self.buffer)

class Chroma(FTISAnalyser):
    def __init__(self, 
    numchroma=12,
    numoctaves=7,
    bins_per_octave=12,
    hop_length=512,
    fmin=None,
    cache=False):
        super().__init__(cache=cache)
        self.numchroma = numchroma
        self.hopsize = hop_length
        self.fmin = fmin
        self.numoctaves = numoctaves
        self.bins_per_octave = bins_per_octave
        self.dump_type = ".json"

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def chroma(self, workable):
        hsh = create_hash(workable, self.identity)
        cache = self.process.cache / f"{hsh}.npy"

        if not cache.exists():
            y, sr = librosa.load(workable)
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            np.save(cache, chroma)
        else:
            chroma = np.load(cache)
        self.buffer[str(workable)] = chroma.tolist()

    def run(self):
        self.buffer = Manager().dict()
        multiproc(self.name, self.chroma, self.input)
        self.output = dict(self.buffer)

class FluidLoudness(FTISAnalyser):
    def __init__(self, windowsize=17640, hopsize=4410, kweighting=1, truepeak=1, cache=False):
        super().__init__(cache=cache)
        self.windowsize = windowsize
        self.hopsize = hopsize
        self.kweighting = kweighting
        self.truepeak = truepeak
        self.dump_type = ".json"

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def analyse(self, workable):
        hsh = create_hash(workable, self.identity)
        cache = self.process.cache / f"{hsh}.npy"

        if not cache.exists():
            loudness = get_buffer(
                fluid.loudness(
                    workable,
                    windowsize=self.windowsize,
                    hopsize=self.hopsize,
                    kweighting=self.kweighting,
                    truepeak=self.truepeak,
                ),
                "numpy",
            )
            np.save(cache, loudness)
        else:
            loudness = np.load(cache, allow_pickle=True)
        self.buffer[str(workable)] = loudness.tolist()

    def run(self):
        self.buffer = Manager().dict()
        workables = self.input
        multiproc(self.name, self.analyse, workables)
        self.output = dict(self.buffer)


class FluidMFCC(FTISAnalyser):
    def __init__(
        self,
        fftsettings=[1024, 512, 1024],
        numbands=40,
        numcoeffs=13,
        minfreq=80,
        maxfreq=20000,
        discard=False,
        cache=False,
    ):
        super().__init__(cache=cache)
        self.fftsettings = fftsettings
        self.numbands = numbands
        self.numcoeffs = numcoeffs
        self.minfreq = minfreq
        self.maxfreq = maxfreq
        self.discard = discard
        self.dump_type = ".json"

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def analyse(self, workable):
        hsh = create_hash(workable, self.identity)
        cache = self.process.cache / f"{hsh}.npy"
        if cache.exists():
            f = np.load(cache, allow_pickle=True)
        else:
            f = get_buffer(
                fluid.mfcc(
                    workable,
                    fftsettings=self.fftsettings,
                    numbands=self.numbands,
                    numcoeffs=self.numcoeffs,
                    minfreq=self.minfreq,
                    maxfreq=self.maxfreq,
                ),
                "numpy",
            )
            np.save(cache, f)
        if self.discard:
            self.buffer[str(workable)] = f.tolist()[1:]
        else:
            self.buffer[str(workable)] = f.tolist()

    def run(self):
        self.buffer = Manager().dict()
        multiproc(self.name, self.analyse, self.input)
        self.output = dict(self.buffer)


class LibroMFCC(FTISAnalyser):
    def __init__(
        self,
        numbands=40,
        numcoeffs=20,
        minfreq=80,
        maxfreq=20000,
        window=2048,
        hop=512,
        dct=2,
        discard=False,
        cache=False,
    ):
        super().__init__(cache=cache)
        self.numbands = numbands
        self.numcoeffs = numcoeffs
        self.minfreq = minfreq
        self.maxfreq = maxfreq
        self.window = window
        self.hop = hop
        self.dct = dct
        self.discard = discard
        self.dump_type = ".json"

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def analyse(self, workable):
        hsh = create_hash(workable, self.identity)
        cache = self.process.cache / f"{hsh}.npy"
        if cache.exists():
            feature = np.load(cache, allow_pickle=True)
            print("loaded cache")
        else:
            y, sr = librosa.load(workable, sr=None, mono=True)
            feature = librosa.feature.mfcc(
                y=y,
                sr=sr,
                n_mfcc=self.numcoeffs,
                dct_type=self.dct,
                n_mels=self.numbands,
                fmax=self.maxfreq,
                fmin=self.minfreq,
                hop_length=self.hop,
                n_fft=self.window,
            )
            np.save(cache, feature)

        if self.discard:
            self.buffer[str(workable)] = feature.tolist()[1:]
        else:
            self.buffer[str(workable)] = feature.tolist()

    def run(self):
        self.buffer = Manager().dict()
        singleproc(self.name, self.analyse, self.input)
        self.output = dict(self.buffer)


class LibroCQT(FTISAnalyser):
    def __init__(
        self,
        hop_length=512,
        minfreq=110,
        n_bins=84,
        bins_per_octave=12,
        tuning=0.0,
        filter_scale=1,
        norm=1,
        sparsity=0.01,
        window="hann",
        scale=True,
        pad_mode="reflect",
        cache=False,
    ):
        super().__init__(cache=cache)
        self.hop_length = hop_length
        self.minfreq = minfreq
        self.n_bins = n_bins
        self.bins_per_octave = bins_per_octave
        self.tuning = tuning
        self.filter_scale = filter_scale
        self.norm = norm
        self.sparsity = sparsity
        self.window = window
        self.scale = scale
        self.pad_mode = pad_mode
        self.dump_type = ".json"

    def load_cache(self):
        self.output = read_json(self.dump_path)

    def dump(self):
        write_json(self.dump_path, self.output)

    def analyse(self, workable):
        hsh = create_hash(workable, self.identity)
        cache = self.process.cache / f"{hsh}.npy"
        if cache.exists():
            cqt = np.load(cache, allow_pickle=True)
        else:
            y, sr = librosa.load(workable, sr=None, mono=True)
            cqt = librosa.cqt(y, sr,
                fmin=self.minfreq,
                n_bins=self.n_bins,
                bins_per_octave=self.bins_per_octave,
                tuning=self.tuning,
                filter_scale=self.filter_scale,
                norm=self.norm,
                sparsity=self.sparsity,
                window=self.window,
                scale=self.scale,
                pad_mode=self.pad_mode,
            )
            np.save(cache, cqt)

        self.buffer[str(workable)] = np.abs(cqt).tolist()

    def run(self):
        self.buffer = Manager().dict()
        singleproc(self.name, self.analyse, self.input)
        self.output = dict(self.buffer)
