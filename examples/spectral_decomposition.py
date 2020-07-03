from ftis.analyser import ClusteredNMF
from ftis.process import FTISProcess as Chain

src = "/home/james/Documents/media"
folder = "/home/james/Documents/analysis"

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
