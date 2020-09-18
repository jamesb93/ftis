from ftis.analyser.descriptor import Chroma
from ftis.analyser.audio import CollapseAudio
from ftis.process import FTISProcess
from ftis.corpus import Corpus

src = Corpus("~/corpus-folder/corpus1")
out = "~/corpus-folder/chroma"

process = FTISProcess(source=src, folder=out)

process.add(
    CollapseAudio(),
    Chroma()
)

if __name__ == "__main__":
    process.run()
