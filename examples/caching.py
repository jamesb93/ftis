from ftis.analyser.descriptor import Flux
from ftis.analyser.stats import Stats
from ftis.corpus import  Corpus
from ftis.process import FTISProcess
import argparse


parser = argparse.ArgumentParser(description="Process input and output location")
parser.add_argument('-i', '--input',  default="~/corpus-folder/corpus1", type=str, help="Folder for input. This should contain some audio files.")
parser.add_argument('-o', '--output', default="~/corpus-folder/caching", type=str, help='Folder for output. This will be made if it doesnt exist.')
args = parser.parse_args()

src = Corpus(args.input)
out = args.output

process = FTISProcess(
    source=src,
    sink=out
)

# we can also instantiate analysers as instances of their classes
# In this scenario using an anonymous class isn't very different but we might want to access the outputs of each analyser after the process has finished

flux = Flux(cache=1, windowsize=1024) # rerunning the script will load flux from cache where the parameters are the same between runs
stats = Stats(numderivs=2)

process.add(flux, stats)

if __name__ == "__main__":
    process.run()
