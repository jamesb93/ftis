from ftis.corpus import Corpus
import argparse


parser = argparse.ArgumentParser(description="Process input and output location")
parser.add_argument('-i', '--input',  default="~/corpus-folder/corpus1", type=str, help="Folder for input. This should contain some audio files.")
args = parser.parse_args()


# Corpora can be pre-processed to remove files that match certain patterns or constraints
# In thie case I am taking the top 10% of files by EBUR-128 loudness and filtering the corpus to that selection
corpus = Corpus("~/corpus-folder/corpus1")
corpus.has('Nico')
print(corpus.items)

corpus = Corpus("~/corpus-folder/corpus1")
corpus.startswith('Nico')
print(corpus.items)

corpus = Corpus("~/corpus-folder/corpus1")
corpus.endswith('641')
print(corpus.items)

corpus = Corpus("~/corpus-folder/corpus1")
corpus.startswith('Tremblay').endswith('M').has('FMTri')
print(corpus.items)

