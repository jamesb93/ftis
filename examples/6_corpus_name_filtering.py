from ftis.corpus import Corpus
import argparse


parser = argparse.ArgumentParser(description="Process input and output location")
parser.add_argument('-i', '--input',  default="~/Documents/Max 8/Packages/TB2-Alpha06-MacOS-Max/media", type=str, help="Folder for input. This should contain some audio files.")
args = parser.parse_args()

"""
You can also filter Corpus items by features of the individual items names.
This example is designed to run on the Fluid Corpus Manipulation example items
"""


# Corpora can be pre-processed to remove files that match certain patterns or constraints
# In thie case I am taking the top 10% of files by EBUR-128 loudness and filtering the corpus to that selection
corpus = Corpus(args.input)
corpus.has('Nico')
print("\n", corpus.items, "\n")

corpus = Corpus(args.input)
corpus.startswith('Nico')
print("\n", corpus.items, "\n")

corpus = Corpus(args.input)
corpus.endswith('641')
print("\n", corpus.items, "\n")

corpus = Corpus(args.input)
corpus.startswith('Tremblay').endswith('M').has('FMTri')
print("\n", corpus.items, "\n")
