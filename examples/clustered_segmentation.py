from ftis.world import World
from ftis.corpus import Corpus
from ftis.analyser.meta import ClusteredSegmentation
from ftis.analyser.slicing import FluidNoveltyslice
from ftis.adapter.reaper import render_tracks
from ftis.common.io import get_sr
from pathlib import Path


c = Corpus("~/corpus-folder/corpus2")
nov = FluidNoveltyslice(threshold=0.2, minslicelength=2, cache=True)
# if we dont set the minslicelength to 2 then we might generate slices too short for the analysis 
seg = ClusteredSegmentation(cache=True)

c >> nov >> seg

w = World(sink="~/clustered_segmentation")
w.build(c)

if __name__ == "__main__":
    w.run()

    tracks = {}
    for media, slices in seg.output.items():
        pos = 0
        sr = get_sr(media)
        items = []
        for start, end in zip(slices, slices[1:]):
            start /= sr
            end /= sr

            item = {
                "file" : media,
                "length" : end - start,
                "start" : start,
                "position" : pos
            }

            pos += end - start

            items.append(item)
        
        tracks[media] = items

    render_tracks(
        Path("~/clustered_segmentation/clustered_slices.rpp").expanduser(), 
        data = tracks
    )