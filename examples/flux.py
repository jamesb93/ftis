from ftis.analyser.descriptor import Flux
from ftis.analyser.audio import CollapseAudio
from ftis.process import FTISProcess
from ftis.corpus import Corpus

src = Corpus("~/corpus-folder/corpus1")
out = "~/corpus-folder/flux"

process = FTISProcess(source=src, folder=out)

process.add(
    CollapseAudio(),
    Flux()
)

if __name__ == "__main__":
    process.run()
