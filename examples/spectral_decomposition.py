from ftis.analyser import ClusteredNMF
from ftis.process import FTISProcess as Chain
from ftis.corpus import Corpus

src = Corpus("~/Documents/media")
folder = "~/Documents/analysis"

process = Chain(source=src, folder=folder)

process.add(
    ClusteredNMF(
        min_cluster_size=2,
        min_samples=1,
        cluster_selection_method="leaf",
        components=10,
    )
)

process.run()
