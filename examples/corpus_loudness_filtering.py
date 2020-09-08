from ftis.corpus import Corpus
from ftis.process import FTISProcess


# Corpora can be pre-processed to remove files that match certain patterns or constraints
# In thie case I am taking the top 10% of files by EBUR-128 loudness and filtering the corpus to that selection
corpus = Corpus("~/corpus-folder/corpus1").loudness(min_loudness=90)

# You can also use a more declarative syntax like so:
new_corpus = (
    Corpus("~/corpus-folder")
    .loudness(max_loudness=10) #filter to bottom 10%
    .duration(min_duration=0.5, max_duration=1.0) #only sound files between 500ms and 1000ms
)
