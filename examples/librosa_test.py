from ftis.analyser import LibroCQT
from ftis.corpus import CorpusLoader
from ftis.process import FTISProcess

src = "~/dev/cqt/sounds"

folder = "/Users/james/dev/ftis_example_project/"

process = FTISProcess(source=src,folder=folder)

process.add(
    CorpusLoader(cache=1),
    LibroCQT()
)

if __name__ == "__main__":
    process.run()
