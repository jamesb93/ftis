from ftis.analyser.descriptor import FluidMFCC
from ftis.corpus import Corpus
from ftis.process import FTISProcess


folder = "~/corpus-folder/management"
em = Corpus("~/corpus-folder/corpus1") # corpus of electromagnetic samples
db = Corpus("~/corpus-folder/corpus2") #corpus of databending samples
corpus = em + db # compose a corpus of both sub-corpora

# adding two Corpus() objects together modifies their contents
# em + db is NOT the same as db + em, unless you are assigning the output
# If you want to add the contents of db to em, you would need to structure it...
# ```em + db```
# and use em as the 'source' for the FTISProcess

process = FTISProcess(
    source = corpus,
    folder = folder
)

process.add(
    FluidMFCC(numcoeffs=3, fftsettings=[128, 64, 128])
)

if __name__ == "__main__":
    process.run()
