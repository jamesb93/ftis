from ftis.analyser.descriptor import FluidMFCC, FluidLoudness
from ftis.analyser.slicing import FluidNoveltyslice
from ftis.corpus import Corpus
from ftis.process import FTISProcess
import argparse


parser = argparse.ArgumentParser(description="Process input and output location")
parser.add_argument('-i', '--input',  default="~/corpus-folder/corpus1", type=str, help="Folder for input. This should contain some audio files.")
parser.add_argument('-o', '--output', default="~/corpus-folder/batching", type=str, help='Folder for output. This will be made if it doesnt exist.')
args = parser.parse_args()

src = Corpus(args.input)
out = args.output

process = FTISProcess(
    source = src,
    sink = out,
    mode="batch" # set the mode to batch
)

# The process will now run the Corpus input to each of the analysers in parallel
process.add(
    FluidNoveltyslice(),
    FluidMFCC(),
    FluidLoudness()
)

if __name__ == "__main__":
    process.run()
