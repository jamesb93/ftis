from ftis.analyser.descriptor import Flux
from ftis.analyser.audio import CollapseAudio
from ftis.process import FTISProcess
from ftis.corpus import Corpus
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
    default="~/corpus-folder/flux",
    type=str,
    help="Folder for output. This will be made if it doesnt exist.",
)
args = parser.parse_args()

src = Corpus(args.input)
out = args.output

process = FTISProcess(source=src, sink=out)

process.add(CollapseAudio(), Flux())

if __name__ == "__main__":
    process.run()
