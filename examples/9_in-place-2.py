from ftis.analyser.descriptor import FluidLoudness, FluidPitch
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
This is a more complex example using the pre and post methods to transform data.
In this example, we take the loudness and pitcjof each sample.
We then discard any frames of pitch where the loudness frame has a mean below a certain threshold
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

def weight_pitch(self):
    pass


process.add(
    CollapseAudio(),
    FluidLoudness(post = remove_truepeak),
    FluidPitch(post = weight_pitch)
)



if __name__ == "__main__":
    process.run()
