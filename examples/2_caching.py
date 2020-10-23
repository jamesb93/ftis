from ftis.analyser.descriptor import Flux
from ftis.analyser.stats import Stats
from ftis.corpus import Corpus
from ftis.world import World
import argparse


parser = argparse.ArgumentParser(description="Process input and output location")
parser.add_argument(
    "-i",
    "--input",
    default="~/corpus-folder/corpus1",
    type=str,
    help="Folder for input. This should contain some audio files.",
)
parser.add_argument(
    "-o",
    "--output",
    default="~/corpus-folder/caching",
    type=str,
    help="Folder for output. This will be made if it doesnt exist.",
)
args = parser.parse_args()

"""
FTIS implements sink level caching when you run processes.
FTIS always makes files in the output folder containing data such as slices, descriptors etc. 
If the order of analysers doesnt change in a process and the inputs haven't been modified in anyway...
...repeated runs can be sped up by simply reading the files from disk rather than re-running analysis
Caching by default is set to true and is specified at the analyser level.
This means you can switch it off for specific processes which you need to run from scratch.
Try running this script twice in your terminal to watch the speed increase.
"""

src = Corpus(args.input)
out = args.output

process = World(sink=out)

# we can also instantiate analysers as instances of their classes
# In this scenario using an anonymous class isn't very different but we might want to access the outputs of each analyser after the process has finished

flux = Flux(
    cache=1, windowsize=2048
)  # rerunning the script will load flux from cache where the parameters are the same between runs
stats = Stats(numderivs=1, cache=True)

src >> flux >> stats 

process.build(src)

if __name__ == "__main__":
    process.run()
