from ftis.analyser.descriptor import FluidMFCC, FluidLoudness
from ftis.analyser.slicing import FluidNoveltyslice
from ftis.corpus import Corpus
from ftis.process import FTISProcess

src = Corpus("~/corpus-folder/corpus1")
out = "~/corpus-folder/batching"

process = FTISProcess(
    source = src,
    folder = out,
    mode="batch" # set the mode to batch
)

# The process will now run the Corpus input to each of the analysers in parallel
process.add(
    FluidNoveltyslice(),
    FluidMFCC(),
    FluidLoudness()
)

if __name__ == "__main__":
    process.run()
