from ftis.analyser import Flux, Stats
from ftis.process import FTISProcess

src = "/Users/james/dev/ftis_example_project/audio"
folder = "/Users/james/dev/ftis_example_project/cached_analysis"

process = FTISProcess(source=src,folder=folder)

f = Flux(cache=True)
g = Stats(numderivs=2)

process.add(f, g)

if __name__ == "__main__":
    process.run()
