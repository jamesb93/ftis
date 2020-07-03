import numpy as np
import hdbscan, math, umap
from ftis.common.analyser import FTISAnalyser
from ftis.common.io import write_json, peek
from ftis.common.conversion import samps2ms, ms2samps
from ftis.common.proc import staticproc, multiproc, singleproc
from ftis.common.exceptions import NotYetImplemented
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.cluster import AgglomerativeClustering
from multiprocessing import Manager
from pathlib import Path
from untwist import transforms, data
from flucoma import fluid
from flucoma.utils import get_buffer, cleanup
from pydub import AudioSegment
from pydub.utils import mediainfo
from scipy.io import wavfile
from scipy import stats
from scipy.signal import savgol_filter


class Stats(FTISAnalyser):
    """Get various statistics and derivatives of those"""

    def __init__(self):
        super().__init__(numdervs=0, flatten=True)
        self.numderivs = numderivs
        self.flatten = flatten

    def dump(self):
        write_json(self.dump_path, dict(self.buffer))

    @staticmethod
    def calc_stats(data):
        """Given a time series calculate statistics"""
        describe = stats.describe(data)
        mean = describe.mean
        stddev = math.sqrt(describe.variance)
        skewness = describe.skewness
        kurtosis = describe.kurtosis
        minimum = describe.minmax[0]
        median = np.median(data)
        maximum = describe.minmax[1]
        return [mean, stddev, skewness, kurtosis, minimum, median, maximum]

    def get_stats(self, base_data, num_derivs: int) -> list:
        """
        Given stats on n number derivatives from initial data
        """
        container = []
        if num_derivs > 0:
            for i in range(num_derivs):
                deriv = np.diff(base_data, i + 1)
                stats = self.calc_stats(deriv)
                container.append(stats)

        elif num_derivs <= 0:
            container = self.calc_stats(base_data)

        return container

    def analyse(self, workable):
        # TODO: any dimensionality input
        element_container = []
        values = np.array(self.input[workable])
        if len(values.shape) < 2:  # single row we run the stats on that
            element_container.append(self.get_stats(values, self.numderivs))
        else:
            for row in values:  # for mfcc band in mfcc
                element_container.append(self.get_stats(row, self.numderivs))

        if self.flatten:
            element_container = np.array(element_container)
            element_container = element_container.flatten()
            element_container = element_container.tolist()
        self.buffer[workable] = element_container

    def run(self):
        self.buffer = Manager().dict()
        workables = [x for x in self.input.keys()]
        singleproc(self.name, self.analyse, workables)
        self.output = dict(self.buffer)


class Flux(FTISAnalyser):
    """Computes spectral flux of an audio file"""

    def __init__(self, windowsize, hopsize):
        super().__init__()
        self.windowsize = windowsize
        self.hopsize = hopsize

    def flux(self, workable):
        audio = data.Wave.read(str(workable))
        if audio.is_stereo():
            audio = np.sum(audio, axis=1)

        fft = transforms.STFT(fft_size=self.windowsize, hop_size=self.hopsize).process(
            audio
        )

        self.data[str(workable)] = list(
            np.sum(np.abs(np.diff(np.abs(fft))), axis=0)
        )  # this is the flux calculation here

    def dump(self):
        write_json(self.dump_path, dict(self.data))

    def run(self):
        self.data = Manager().dict()
        workables = [x for x in self.input.iterdir() if x.suffix == ".wav"]
        multiproc(self.name, self.flux, workables)
        self.output = dict(self.data)


class Normalise(FTISAnalyser):
    def __init__(self, minimum=0, maximum=1):
        super().__init__()
        self.min = minimum
        self.max = maximum

    def analyse(self):
        scaled_data = MinMaxScaler((self.min, self.max)).fit_transform(self.features)

        self.output = {}
        for k, v in zip(self.keys, scaled_data):
            self.output[k] = list(v)

    def dump(self):
        write_json(self.dump_path, self.output)

    def run(self):
        self.keys = [x for x in self.input.keys()]
        self.features = [x for x in self.input.values()]
        staticproc(self.name, self.analyse)


class Standardise(FTISAnalyser):
    def __init__(self):
        super().__init__()

    def analyse(self):
        scaled_data = StandardScaler().fit_transform(self.features)

        self.output = {}
        for k, v in zip(self.keys, scaled_data):
            self.output[k] = list(v)

    def dump(self):
        write_json(self.dump_path, self.output)

    def run(self):
        self.keys = [x for x in self.input.keys()]
        self.features = [x for x in self.input.values()]
        staticproc(self.name, self.analyse)


class ClusteredSegmentation(FTISAnalyser):
    def __init__(self, numclusters=2, windowsize=4):
        super().__init__()
        self.numclusters = numclusters
        self.windowsize = windowsize

    def analyse(self, workable):
        slices = self.input[workable]
        slices = [int(x) for x in slices]  # lets test this out later
        count = 0
        standardise = StandardScaler()
        model = AgglomerativeClustering(n_clusters=self.numclusters)

        while (count + self.windowsize) <= len(slices):
            indices = slices[
                count : count + self.windowsize
            ]  # create a section of the indices in question
            data = []
            for i, (start, end) in enumerate(zip(indices, indices[1:])):

                mfcc = fluid.mfcc(
                    workable,
                    fftsettings=[2048, -1, -1],
                    startframe=start,
                    numframes=end - start,
                )

                stats = get_buffer(fluid.stats(mfcc, numderivs=1), "numpy")

                data.append(stats.flatten())

            data = standardise.fit_transform(data)

            cluster = model.fit(data)
            cur = -2
            for j, c in enumerate(cluster.labels_):
                prev = cur
                cur = c
                if cur == prev:
                    try:
                        slices.pop(j + count)
                    except IndexError:
                        pass  # TODO fix later
            count += 1
            self.buffer[workable] = slices

    def dump(self):
        write_json(self.dump_path, dict(self.buffer))

    def run(self):
        self.buffer = Manager().dict()
        workables = [x for x in self.input]
        singleproc(self.name, self.analyse, workables)
        self.output = dict(self.buffer)


class UMAPDR(FTISAnalyser):
    """Dimension reduction with UMAP algorithm"""

    def __init__(self, mindist=0.01, neighbours=7, components=2):
        super().__init__()
        self.mindist = mindist
        self.neighbours = neighbours
        self.components = components

    def analyse(self):
        self.output = {}
        data = [v for v in self.input.values()]
        keys = [k for k in self.input.keys()]

        data = np.array(data)

        reduction = umap.UMAP(
            n_components=self.components,
            n_neighbors=self.neighbours,
            min_dist=self.mindist,
        )
        data = reduction.fit_transform(data)

        for key, value in zip(keys, data):
            self.output[key] = value.tolist()

    def dump(self):
        write_json(self.dump_path, self.output)

    def run(self):
        staticproc(self.name, self.analyse)


class CollapseAudio(FTISAnalyser):
    def __init__(self):
        super().__init__()

    def collapse(self, workable):
        out = self.output / workable.name
        raw, sr = peek(workable)
        audio = None
        if raw.ndim == 1:
            audio = raw
        else:
            audio = raw.sum(axis=0) / raw.ndim
        wavfile.write(out, sr, audio)
        
    def run(self):
        self.output = self.process.folder / f"{self.order}_{self.__class__.__name__}"
        self.output.mkdir(exist_ok=True)
        workables = [
            Path(x)
            for x in self.input.iterdir()
            if x != ".DS_Store" and x.suffix == ".wav"
        ]
        multiproc(self.name, self.collapse, workables)


class ExplodeAudio(FTISAnalyser):
    def __init__(self):
        super().__init__()

    def segment(self, workable):
        slices = self.input[str(workable)]
        src = AudioSegment.from_file(workable, format="wav")
        sr = int(mediainfo(workable)["sample_rate"])
        
        for i, (start, end) in enumerate(zip(slices, slices[1:])):
            start = samps2ms(start, sr)
            end = samps2ms(end, sr)
            segment = src[start:end]
            segment.export(self.output / f"{workable.stem}_{i}.wav", format="wav")

    def run(self):
        self.output = self.process.folder / f"{self.order}_{self.__class__.__name__}"
        self.output.mkdir(exist_ok=True)
        workables = [Path(x) for x in self.input.keys()]
        multiproc(self.name, self.segment, workables)


class FluidLoudness(FTISAnalyser):
    def __init__(self, windowsize=17640, hopsize=4410, kweighting=1, truepeak=1):
        super().__init__()
        self.windowsize = windowsize
        self.hopsize = hopsize
        self.kweighting = kweighting
        self.truepeak = truepeak

    def analyse(self, workable):
        loudness = fluid.loudness(
            workable,
            windowsize=self.windowsize,
            hopsize=self.hopsize,
            kweighting=self.kweighting,
            truepeak=self.truepeak,
        )

        self.buffer[str(workable)] = get_buffer(loudness)

    def dump(self):
        write_json(self.dump_path, self.output)

    def run(self):
        self.buffer = Manager().dict()
        workables = [x for x in self.input.iterdir() if x.suffix == ".wav"]
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
    ):
        super().__init__()
        self.fftsettings = fftsettings
        self.numbands = numbands
        self.numcoeffs = numcoeffs
        self.minfreq = minfreq
        self.maxfreq = maxfreq

    def analyse(self, workable):
        mfcc = fluid.mfcc(
            workable,
            fftsettings=self.fftsettings,
            numbands=self.numbands,
            numcoeffs=self.numcoeffs,
            minfreq=self.minfreq,
            maxfreq=self.maxfreq,
        )

        self.data_container[str(workable)] = get_buffer(mfcc)

    def dump(self):
        write_json(self.dump_path, self.output)

    def run(self):
        self.buffer = Manager().dict()
        workables = [x for x in self.input.iterdir() if x.suffix == ".wav"]
        multiproc(self.name, self.analyse, workables)
        self.output = dict(self.buffer)


class FluidNoveltyslice(FTISAnalyser):
    def __init__(
        self,
        feature=0,
        fftsettings=[1024, 512, 1024],
        filtersize=1,
        minslicelength=2048,
        threshold=0.5,
    ):
        super().__init__()
        self.feature = feature
        self.fftsettings = fftsettings
        self.filtersize = filtersize
        self.minslicelength = minslicelength
        self.threshold = threshold

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

    def dump(self):
        write_json(self.dump_path, self.output)

    def run(self):
        self.buffer = Manager().dict()
        workables = [x for x in self.input.iterdir() if x.suffix == ".wav"]
        multiproc(self.name, self.analyse, workables)
        self.output = dict(self.buffer)


class HDBSClustering(FTISAnalyser):
    def __init__(self, minclustersize=2, minsamples=1):
        super().__init__()
        self.minclustersize = minclustersize
        self.minsamples = minsamples

    def analyse(self):
        keys = [x for x in self.input.keys()]
        values = [x for x in self.input.values()]

        data = np.array(values)

        db = hdbscan.HDBSCAN(
            min_cluster_size=self.minclustersize, min_samples=self.minsamples,
        ).fit(data)

        self.output = {}

        for audio, cluster in zip(keys, db.labels_):
            if str(cluster) in self.output:
                self.output[str(cluster)].append(audio)
            else:
                self.output[str(cluster)] = [audio]

    def dump(self):
        write_json(self.dump_path, self.output)

    def run(self):
        staticproc(self.name, self.analyse)


class AGCluster(FTISAnalyser):
    def __init__(self, numclusters=3):
        super().__init__()
        self.numclusters = numclusters

    def analyse(self):
        keys = [x for x in self.input.keys()]
        values = [x for x in self.input.values()]

        data = np.array(values)

        db = AgglomerativeClustering(n_clusters=self.numclusters).fit(data)

        self.output = {}

        for audio, cluster in zip(keys, db.labels_):
            if str(cluster) in self.output:
                self.output[str(cluster)].append(audio)
            else:
                self.output[str(cluster)] = [audio]

    def dump(self):
        write_json(self.dump_path, self.output)

    def run(self):
        staticproc(self.name, self.analyse)

import numpy as np
import hdbscan
from ftis.common.analyser import FTISAnalyser
from ftis.common.utils import read_json, write_json
from ftis.common.proc import singleproc
from ftis.common.types import Ftypes
from sklearn.cluster import AgglomerativeClustering
from flucoma import fluid
from flucoma.utils import get_buffer, cleanup
from scipy.io import wavfile
from scipy.signal import savgol_filter


class ClusteredNMF(FTISAnalyser):
    def __init__(self, 
        iterations=100, 
        components=10, 
        fftsettings=[4096, 1024, 4096],
        smoothing=11,
        polynomial=2,
        min_cluster_size=2,
        min_samples=2,
        cluster_selection_method="eom"
    ):
        super().__init__()
        self.components = components
        self.iterations = iterations
        self.fftsettings = fftsettings
        self.smoothing = smoothing
        self.polynomial = polynomial
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.cluster_selection_method= cluster_selection_method

    def analyse(self, workable):
        nmf = fluid.nmf(
            workable,
            iterations=self.iterations,
            components=self.components,
            fftsettings=self.fftsettings,
        )
        bases = get_buffer(nmf.bases, "numpy")
        bases_smoothed = np.zeros_like(bases)
        
        for i, x in enumerate(bases):
            bases_smoothed[i] = savgol_filter(
                x, self.smoothing, self.polynomial
            )

        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size, 
            min_samples=self.min_samples,
            cluster_selection_method=self.cluster_selection_method
        )

        cluster_labels = clusterer.fit_predict(bases_smoothed)
        unique_clusters = list(dict.fromkeys(cluster_labels))

        sound = get_buffer(nmf.resynth, "numpy")

        for x in unique_clusters:
            summed = np.zeros_like(sound[0])  # make an empty numpy array of same size
            base = workable.name
            output = self.output / f"{base}_{x}.wav"
            for idx, cluster in enumerate(cluster_labels):
                if cluster == x:
                    summed += sound[idx]
            wavfile.write(output, 44100, summed)

    def run(self):
        self.output = self.process.folder / f"{self.order}_{self.__class__.__name__}"
        self.output.mkdir(exist_ok=True)
        workables = [k for k in self.input.iterdir() if k.name != ".DS_Store" and k.is_file() and k.suffix == ".wav"]
        singleproc(self.name, self.analyse, workables)



# class FluidSines(FTISAnalyser):
#     def __init__(self,
#     bandwidth=76,
#     birthhighthreshold=-60,
#     birthlowthreshold=-24,
#     detectionthreshold=-96,
#     fftsettings=[1024, 512, 1024],
#     mintracklen=15,
#     trackingmethod=0,
#     trackfreqrange=50.0,
#     trackmagrange=15.0,
#     trackprob=0.5
#     ):
#         super().__init__()
#         self.bandwidth = bandwidth,
#         self.birthhighthreshold,
#         self.birthlowthreshold,
#         self.detectionthreshold,
#         self.fftsettings,
#         self.mintracklen

#     def analyse(self, workable):
#         out_folder = self.output / workable.name
#         out_folder.mkdir(exist_ok=True)

#         sines = out_folder / f"sines_{workable.name}"
#         residual = out_folder / f"residual_{workable.name}"

#         fluid.sines(
#             workable,
#             sines=sines,
#             residual=residual,
#             bandwidth=self.parameters["bandwidth"],
#             birthhighthreshold=self.parameters["birthhighthreshold"],
#             birthlowthreshold=self.parameters["birthlowthreshold"],
#             detectionthreshold=self.parameters["detectionthreshold"],
#             fftsettings=self.parameters["fftsettings"],
#             mintracklen=self.parameters["mintracklen"],
#             trackingmethod=self.parameters["trackmethod"],
#             trackfreqrange=self.parameters["trackfreqrange"],
#             trackmagrange=self.parameters["trackmagrange"],
#             trackprob=self.parameters["trackprob"],
#         )

#     def run(self):
#         workables = [x for x in self.input.iterdir() if x.suffix == ".wav"]
#         singleproc(self.name, self.analyse, workables)
#         self.output

# class FluidTransients(FTISAnalyser):
#     def __init__(self):
#         super().__init__(parent_process)
#         self.input_type = Ftypes.folder
#         self.output_type = Ftypes.folder

#     def analyse(self, workable):
#         out_folder = self.output / workable.name
#         out_folder.mkdir(exist_ok=True)

#         transients = out_folder / f"transients_{workable.name}"
#         residual = out_folder / f"residual_{workable.name}"

#         fluid.transients(
#             workable,
#             transients=transients,
#             residual=residual,
#             blocksize=self.parameters["blocksize"],
#             clumplength=self.parameters["clumplength"],
#             order=self.parameters["order"],
#             padsize=self.parameters["padsize"],
#             skew=self.parameters["skew"],
#             threshback=self.parameters["threshback"],
#             threshfwd=self.parameters["threshfwd"],
#             windowsize=self.parameters["windowsize"],
#         )

#     def run(self):
#         workables = [x for x in self.input.iterdir() if x.suffix == ".wav"]
#         multiproc(self.name, self.analyse, workables)
#         cleanup()
