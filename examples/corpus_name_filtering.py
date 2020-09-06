from ftis.corpus import Corpus


# Corpora can be pre-processed to remove files that match certain patterns or constraints
# In thie case I am taking the top 10% of files by EBUR-128 loudness and filtering the corpus to that selection
corpus = Corpus("~/Documents/Max 8/Packages/TB2-Alpha04c-Max/media")
corpus.has('Nico')
print(corpus.items)

corpus = Corpus("~/Documents/Max 8/Packages/TB2-Alpha04c-Max/media")
corpus.startswith('Nico')
print(corpus.items)

corpus = Corpus("~/Documents/Max 8/Packages/TB2-Alpha04c-Max/media")
corpus.endswith('641')
print(corpus.items)

corpus = Corpus("~/Documents/Max 8/Packages/TB2-Alpha04c-Max/media")
corpus.startswith('Tremblay').endswith('M').has('FMTri')
print(corpus.items)

