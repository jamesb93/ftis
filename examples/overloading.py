from ftis.corpus import Corpus
from ftis.process import FTISProcess
from ftis.analyser.audio import CollapseAudio
from ftis.analyser.descriptor import FluidLoudness, FluidPitch, FluidMFCC
from pathlib import Path

corpus = Corpus("~/corpus-folder/corpus1")
f = CollapseAudio()
corpus >> f >> FluidPitch()

def get_children(obj):
    print(f'***{obj} children***')
    for x in obj.chain:
        print(x)
        get_children(x)

# get_children(corpus)
# get_children(corpus)
# chain1 = f >> FluidLoudness()
# chain2 = f >> FluidPitch()
# chain3 = f >> FluidMFCC()
# print(chain1.chain[f])
# print(chain1.chain)