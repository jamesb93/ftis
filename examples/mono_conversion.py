from ftis.analyser.audio import CollapseAudio
from ftis.corpus import Corpus
from ftis.process import FTISProcess



process = FTISProcess(
    source = Corpus("~/corpus-folder/corpus1"), 
    folder = "~/corpus-folder/collapse"
)

process.add(
    CollapseAudio()
)

process.run()
