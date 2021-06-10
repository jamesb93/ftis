from ftis.world import World
from ftis.corpus import Corpus

# Import analysers
from ftis.analyser.dr import UMAP
from ftis.analsyer.flucoma import MFCC
from ftis.analyser.stats import Stats
from ftis.analyser.scaling import Standardise, Normalise
from ftis.analyser.cluster import AgglomerativeClustering

corpus = Corpus("~/sounds")
world = World("~/fits-output")

(
    corpus >> MFCC >> 
    Stats >> Standardise >> 
    UMAP >> AgglomerativeClustering
)


world.build(corpus)

if __name__ == "__main__":
    world.run()