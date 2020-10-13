from ftis.analyser.descriptor import FluidLoudness
from ftis.analyser.audio import CollapseAudio
from ftis.analyser.stats import Stats
from ftis.corpus import Corpus
from ftis.process import FTISProcess
from ftis.common.io import write_json
from pathlib import Path

import argparse


parser = argparse.ArgumentParser(description="Process input and output location")
parser.add_argument('-i', '--input',  default="~/corpus-folder/corpus1", type=str, help="Folder for input. This should contain some audio files.")
parser.add_argument('-o', '--output', default="~/corpus-folder/lambdas", type=str, help='Folder for output. This will be made if it doesnt exist.')
args = parser.parse_args()

"""
We can pre and process data in place, rather than having to create new analysers to process input and output data.
This functionality is inherited from the base analyser class, so everything can do it, you just need to implement what you want to do.
In this example, I simply reset the values in the output of the FluidLoudness() class after processing
"""

out = args.output
process = FTISProcess(
    source = Corpus(args.input),
    sink = out
)

def remove_truepeak(self):
    self.output = {
        k: v[0]
        for k, v in self.output.items()
    }


process.add(
    CollapseAudio(),
    FluidLoudness(
        post = remove_truepeak
    )
)

if __name__ == "__main__":
    process.run()