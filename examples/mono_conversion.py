from ftis.analyser import CollapseAudio
from ftis.corpus import Corpus
from ftis.process import FTISProcess

folder = "~/Documents/analysis"

process = FTISProcess(
    source=Corpus("~/Documents/media"), 
    folder=folder
)

process.add(
    CollapseAudio()
)

process.run()
