# Let's perform some analysis for creating datasets more easily!

# import analysers
from ftis.analyser.descriptors import Chroma
from ftis.analyser.audio import CollapseAudio
from ftis.analyser.stats import Stats

# import scaffolding
from ftis.corpus import Corpus
from ftis.process import FTISProcess
from ftis.common.io import write_json
from pathlib import Path
# import the necessary flucoma materials
from flucoma import dataset

src = Corpus("~/corpus-folder/corpus1")
out = "~/corpus-folder/chroma-dataset"

process = FTISProcess(source=src, folder=out)

chroma_data = Chroma(fmin=40) # use a non-anonymous class
process.add(
    CollapseAudio(),
    chroma_data
)

if __name__ == "__main__":
    process.run()

    # Now that ftis has completed lets pack the data into a fluid dataset
    dataset = dataset.pack(chroma_data.output) # use the pack function to marshall it to the right format
    dataset_path = Path(out) / "dataset.json" # create an output path
    write_json(dataset, dataset_path) # write to disk
