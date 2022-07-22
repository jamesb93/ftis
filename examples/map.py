from ftis.world import World
from ftis.corpus import Corpus

# Import analysers
from ftis.analyser.dr import UMAP
from ftis.analyser.flucoma import MFCC
from ftis.analyser.stats import Stats
from ftis.analyser.scaling import Standardise, Normalise
from ftis.analyser.clustering import AgglomerativeClustering

corpus = Corpus("~/corpus-folder/corpus1")
world = World("~/ftis-output")

(
    corpus >> MFCC() >> 
    Stats() >> Standardise() >> 
    UMAP() >> AgglomerativeClustering()
)

world.build(corpus)

if __name__ == "__main__":
    world.run()