from ftis.analyser import Flux, Stats
from ftis.corpus import CorpusLoader, Corpus
from ftis.process import FTISProcess

src = Corpus("~/dev/cqt/sounds")
folder = "/Users/james/dev/ftis_example_project/"

process = FTISProcess(
    source=src,
    folder=folder
)

f = Flux(cache=True)
g = Stats(numderivs=2, cache=True)

process.add(f, g)

if __name__ == "__main__":
    process.run()
