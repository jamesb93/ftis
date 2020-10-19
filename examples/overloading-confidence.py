from ftis.corpus import Corpus
from ftis.world import World
from ftis.process import FTISProcess
from ftis.analyser.audio import CollapseAudio
from ftis.analyser.descriptor import (
    FluidLoudness, 
    FluidPitch, 
    FluidMFCC
)
from ftis.analyser.stats import Stats
from pathlib import Path

corpus = Corpus("~/corpus-folder/corpus1")
collapse = CollapseAudio()
pitch = FluidPitch(fftsettings=[1024, 512, 1024])
stats = Stats()

def mask_by_confidence(self):
    for k, v in self.output.items():
        freq = v[0] # list of frequencies
        conf = v[1] # list of confidences
        for i, c in enumerate(conf):
            if c < 0.90:
                del self.output[k][0][i]
                del self.output[k][1][i]

pitch.post = mask_by_confidence

# script the connections
corpus >> collapse
collapse >> pitch >> stats

# setup the world
world = World(sink="~/corpus-folder/overloading2")

if __name__ == "__main__":
    # add our corpus node to the world
    world.build(corpus)