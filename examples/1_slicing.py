from ftis.process import FTISProcess
from ftis.corpus import Corpus
from ftis.analyser.audio import ExplodeAudio, CollapseAudio
from ftis.analyser.slicing import FluidNoveltyslice
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
    default="~/corpus-folder/slicing",
    type=str,
    help="Folder for output. This will be made if it doesnt exist.",
)
args = parser.parse_args()

"""
I'm going to take an example of slicing a Corpus to introduce you to the fundamentals of FTIS.
FTIS always starts with the creation of a "Corpus" and a "Process"
You will always import at the ftis.process.FTISProcess and ftis.corpus.Corpus to get these
Follow along with  the comments to see how this works.
"""

# We make a 'Corpus' object below by creating an instance of that object with a string to the location of our corpus
src = Corpus(args.input)
out = args.output  # we also set an output path, in FTIS speak a 'sink'.

# Now we make an instance of a FTIS process.
# This is where we set up the inputs and outputs of that FTISProcess, known as a 'source' and a 'sink'
process = FTISProcess(source=src, sink=out)

# Once we have a FTISProcess (process is the variable name here) we add 'analysers' to that process
# You can see the various analysers imported at the top of the page under the module space...
# ...ftis.analyser followed by .category.

# To find other analysers see the complete list in the documentation.

# To add analysers, we simply pass the class along with its parameters to the process.add() function.
# This will connect those process in series, passing their outputs to the next analyser in the chain.
process.add(FluidNoveltyslice(), ExplodeAudio())

# Lastly we call process.run(). We should always call it inside the __name__ == "__main__" block
# Why? We use multiprocessing to speed things up under the hood and running outside this results in errors.
if __name__ == "__main__":
    process.run()
