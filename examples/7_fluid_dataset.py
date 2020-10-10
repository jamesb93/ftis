from ftis.analyser.descriptor import FluidMFCC
from ftis.analyser.audio import CollapseAudio
from ftis.analyser.stats import Stats
from ftis.corpus import Corpus
from ftis.process import FTISProcess
from ftis.common.io import write_json
from pathlib import Path

# import the necessary flucoma materials
from flucoma import dataset
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
    default="~/corpus-folder/fluid-dataset",
    type=str,
    help="Folder for output. This will be made if it doesnt exist.",
)
args = parser.parse_args()

"""
Using the python-flucoma package analyser outputs can be turned into datasets.
To do this we have to specifically create an instance of the analyser we are interested in.
After the FTISProcess has run we then extract the output from that instance.
"""

src = Corpus(args.input)
out = args.output

process = FTISProcess(source=src, sink=out)

stats = Stats(numderivs=2, spec=["stddev", "mean"])  # create an instance of the stats class
process.add(CollapseAudio(), FluidMFCC(), stats)

if __name__ == "__main__":
    process.run()

    # Now that ftis has completed lets pack the data into a fluid dataset
    dataset = dataset.pack(stats.output)  # use the pack function to marshall it to the right format
    dataset_path = Path(out) / "dataset.json"  # create an output path
    write_json(dataset_path.expanduser(), dataset)  # write to disk
