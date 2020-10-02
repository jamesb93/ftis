from ftis.analyser.meta import ClusteredNMF
from ftis.process import FTISProcess as Chain
from ftis.corpus import Corpus

src = Corpus("~/corpus-folder/corpus1")
out = "~/corpus-folder/batching"

process = Chain(source=src, folder=out)

process.add(
    ClusteredNMF(
        min_cluster_size=2,
        min_samples=1,
        cluster_selection_method="leaf",
        components=10,
    )
)

if __name__ == "__main__":
    process.run()
