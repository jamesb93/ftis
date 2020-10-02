from ftis.analyser.meta import ClusteredNMF
from ftis.process import FTISProcess as Chain
from ftis.corpus import Corpus
import argparse

parser = argparse.ArgumentParser(description="Process input and output location")
parser.add_argument('-i', '--input',  default="~/corpus-folder/corpus1", type=str, help="Folder for input. This should contain some audio files.")
parser.add_argument('-o', '--output', default="~/corpus-folder/spec-decomposition", type=str, help='Folder for output. This will be made if it doesnt exist.')
args = parser.parse_args()

src = Corpus(args.input)
out = args.output

process = Chain(
    source=src, 
    folder=out
)

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
