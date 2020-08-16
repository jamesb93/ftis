from ftis.analyser import LibroCQT
from ftis.corpus import Corpus
from ftis.analyser import LibroCQT
from ftis.process import FTISProcess


folder = "/Users/james/dev/ftis_example_project/"

process = FTISProcess(
    source=Corpus("~/dev/cqt/sounds"),
    folder=folder
)

process.add(
    LibroCQT()
)

if __name__ == "__main__":
    process.run()
