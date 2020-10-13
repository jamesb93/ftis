from ftis.corpus import Corpus
from ftis.process import FTISProcess
from ftis.analyser.audio import CollapseAudio
from ftis.analyser.descriptor import FluidLoudness, FluidPitch

from pathlib import Path

corpus = Corpus("~/corpus-folder/corpus")

chain1 = CollapseAudio() >> FluidLoudness()
chain2 =  CollapseAudio() >> FluidPitch()

world = World(
    source = corpus
)

world.add_nodes(
    chain1,
    chain2
)`