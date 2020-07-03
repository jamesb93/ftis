from ftis.analyser import FluidNoveltyslice, ExplodeAudio, CollapseAudio
from ftis.process import FTISProcess

src = "/home/james/Documents/media"
folder = "/home/james/Documents/analysis"

process = FTISProcess(source=src, folder=folder)

process.add(
    FluidNoveltyslice(threshold=0.35, feature=1),
    ExplodeAudio()
)

process.run()
