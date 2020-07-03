from ftis.analyser import FluidNoveltyslice, FluidMFCC, FluidLoudness
from ftis.process import FTISProcess

src = "/home/james/Documents/media"
folder = "/home/james/Documents/analysis"

process = FTISProcess(
    source=src, 
    folder=folder, 
    mode="batch" # set the mode to batch
    )

process.add(
    FluidNoveltyslice(),
    FluidMFCC(),
    FluidLoudness()
)

process.run()
