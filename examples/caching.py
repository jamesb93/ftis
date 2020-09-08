from ftis.analyser.descriptor import Flux
from ftis.analyser.stats import Stats
from ftis.corpus import  Corpus
from ftis.process import FTISProcess

src = Corpus("~/corpus-folder/corpus1")
out = "~/corpus-folder/caching"

process = FTISProcess(
    source=src,
    folder=out
)

# we can also instantiate analysers as instances of their classes
# In this scenario using an anonymous class isn't very different but we might want to access the outputs of each analyser after the process has finished

flux = Flux(cache=1, windowsize=1024) # rerunning the script will load flux from cache where the parameters are the same between runs
stats = Stats(numderivs=2)

process.add(flux, stats)

if __name__ == "__main__":
    process.run()
