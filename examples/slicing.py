from ftis.analyser.audio import ExplodeAudio, CollapseAudio
from ftis.analyser.slicing import FluidNoveltyslice
from ftis.process import FTISProcess
from ftis.corpus import Corpus

src = Corpus("~/corpus-folder/corpus1")
out = "~/corpus-folder/slicing"

process = FTISProcess(source=src, folder=out)

process.add(
    FluidNoveltyslice(threshold=0.35, feature=1),
    ExplodeAudio()
)

process.run()
