from ftis.analyser.flucoma import MFCC
from ftis.corpus import Corpus
from ftis.world import World
import argparse


parser = argparse.ArgumentParser(description="Process input and output location")
parser.add_argument(
    "--corpusone",
    default="~/corpus-folder/corpus1",
    type=str,
    help="Folder for input. This should contain some audio files.",
)
parser.add_argument(
    "--corpustwo",
    default="~/corpus-folder/corpus2",
    type=str,
    help="Folder for input. This should contain some audio files.",
)
parser.add_argument(
    "-o",
    "--output",
    default="~/corpus-folder/corpus-management",
    type=str,
    help="Folder for output. This will be made if it doesnt exist.",
)
args = parser.parse_args()

"""
Corpus objects overload the addition operator.
This allows you to add Corpus objects together to create a new Corpus from their materials.
"""

em = Corpus(args.corpusone)  # first corpus
db = Corpus(args.corpustwo)  # second corpus
corpus = em + db  # compose a corpus of both sub-corpora

# adding two Corpus() objects together modifies their contents
# em + db is NOT the same as db + em, unless you are assigning the output
# If you want to add the contents of db to em, you would need to structure it...
# ```em + db```
# and use em as the 'source' for the FTISProcess

world = World(sink=args.output)
corpus >> MFCC()
world.build(corpus)

if __name__ == "__main__":
    world.run()
