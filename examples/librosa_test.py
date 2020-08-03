from ftis.analyser import FluidMFCC
from ftis.process import FTISProcess

src = "/Users/james/dev/ftis_example_project/audio"
folder = "/Users/james/dev/ftis_example_project/cached_analysis"

process = FTISProcess(source=src,folder=folder)

process.add(
    FluidMFCC()
)

if __name__ == "__main__":
    process.run()
