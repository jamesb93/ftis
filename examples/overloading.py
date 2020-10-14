from ftis.corpus import Corpus
from ftis.process import FTISProcess
from ftis.analyser.audio import CollapseAudio
from ftis.analyser.descriptor import FluidLoudness, FluidPitch


corpus = Corpus("~/corpus-folder/corpus1")
f = CollapseAudio() 
chain1 = corpus >> f >> FluidLoudness()
chain2 = corpus >> f >> FluidPitch()

print(chain1.chain)



# world = World(
#     source = corpus
# )

# world.add_nodes(
#     chain1,
#     chain2
# )`