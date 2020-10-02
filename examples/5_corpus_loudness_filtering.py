from ftis.corpus import Corpus
from ftis.process import FTISProcess
import argparse


parser = argparse.ArgumentParser(description="Process input and output location")
parser.add_argument('-i', '--input',  default="~/corpus-folder/corpus1", type=str, help="Folder for input. This should contain some audio files.")
parser.add_argument('-o', '--output', default="~/corpus-folder/corpus-management", type=str, help='Folder for output. This will be made if it doesnt exist.')
args = parser.parse_args()
 
"""
Corpus objects come bundled with some filtering processes to remove items that you don't want or need.
This example demonstrates filtering a corpus so only the top ten percent of samples by loudness are let through.
"""


# Corpora can be pre-processed to remove files that match certain patterns or constraints
# In thie case I am taking the top 10% of files by EBUR-128 loudness and filtering the corpus to that selection
corpus = Corpus(args.input)
print(f"Corpus began with {len(corpus.items)} items")
corpus.loudness(min_loudness=90)
print(f"Corpus filtered to {len(corpus.items)} items")

# You can also use a more declarative syntax like so:
# new_corpus = (
#     Corpus("~/corpus-folder/corpus1")
#     .loudness(max_loudness=10) #filter to bottom 10%
# )
# This becomes more clear when you use multiple filters
