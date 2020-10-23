from ftis.corpus import Corpus
from ftis.world import World
from ftis.world import World
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
pitch_stats = Stats(spec=["median"])
loudness = FluidLoudness(windowsize=1024, hopsize=512)
loudness_stats = Stats(spec=["mean"])


def mask_with_loudness(self):
    for k, v in loudness_stats.output.items():
        mean = v[0]
        for i, (x, y) in enumerate(loudness.output.items()):
            dbfs = y[0]
            if sum(dbfs) / len(dbfs) < mean:
                del self.output[k][0][i]
                del self.output[k][1][i]

pitch.post = mask_with_loudness

# script the connections
corpus >> collapse
collapse >> loudness >> loudness_stats
collapse >> pitch >> pitch_stats

# setup the world
world = World(sink="~/corpus-folder/overloading")

if __name__ == "__main__":
    # add our corpus node to the world
    world.add(corpus)