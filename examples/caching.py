from ftis.analyser import Flux, Stats
from ftis.corpus import CorpusLoader
from ftis.process import FTISProcess

src = "~/dev/cqt/sounds"
folder = "/Users/james/dev/ftis_example_project/"

process = FTISProcess(source=src,folder=folder)

a = CorpusLoader(max_dur = 3)
f = Flux(cache=True)
g = Stats(numderivs=2, cache=True)

process.add(a, f, g)

if __name__ == "__main__":
    process.run()
