from ftis.analyser import CollapseAudio
from ftis.process import FTISProcess

src = "/home/james/Documents/media"
folder = "/home/james/Documents/analysis"

process = FTISProcess(source=src, folder=folder)

process.add(
    CollapseAudio()
)

process.run()
