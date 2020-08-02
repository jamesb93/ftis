from ftis.analyser import (
    CollapseAudio,
    FluidMFCC,
    Stats, 
    Standardise, 
    Normalise 
)
from ftis.corpus import CorpusLoader
from ftis.visualisation import Visualiser
from ftis.process import FTISProcess as Chain

src = "~/Documents/Max 8/Packages/TB2-Alpha04c-Max/media"
folder = "~/visualiser"

process = Chain(source=src, folder=folder)

process.add(
    CorpusLoader(cache=1),
    CollapseAudio(),
    FluidMFCC(cache=1),
    Stats(flatten=1, numderivs=1, cache=1),
    Standardise(cache=1),
    Normalise(cache=1),
    Visualiser()
)

if __name__ == "__main__":
    process.run()
