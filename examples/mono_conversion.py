from ftis.analyser.audio import CollapseAudio
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
    default="~/corpus-folder/collapse",
    type=str,
    help="Folder for output. This will be made if it doesnt exist.",
)
args = parser.parse_args()

process = World(source=Corpus(args.input), sink=args.output)

process.add(CollapseAudio())

if __name__ == "__main__":
    process.run()
