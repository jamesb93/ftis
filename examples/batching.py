from ftis.analyser import FluidNoveltyslice, FluidMFCC, FluidLoudness
from ftis.corpus import Corpus
from ftis.process import FTISProcess


folder = "/home/james/Documents/analysis"

process = FTISProcess(
    source = Corpus("/home/james/Documents/media"), 
    folder = folder, 
    mode="batch" # set the mode to batch
    )

process.add(
    FluidNoveltyslice(),
    FluidMFCC(),
    FluidLoudness()
)

process.run()
