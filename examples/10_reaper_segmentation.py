from ftis.adapter.reaper import render_tracks
from ftis.analyser.slicing import FluidNoveltyslice
from ftis.world import World
from ftis.corpus import Corpus
from ftis.common.io import get_sr
from pathlib import Path

# instantiate
sink = "~/reaperising-ftis"
c = Corpus("~/Documents/Max 8/Packages/TB2-Alpha06-MacOS-Max/media")
slicing = FluidNoveltyslice()

# script connection
c >> slicing

if __name__ == "__main__":
    w = World(sink = sink).add(c)

    #---------- Data for render_tracks would look something like this ----------#
    # data = {
    #    "track1" : [
    #        {"file" : None, "length": 1.0, "start": 0.0, "position": 0.0}
    #    ],
    #    "track2" : [
    #        {"file" : None, "length": 1.0, "start": 0.0, "position": 0.0}
    #    ]
    # }
    #---------------------------------------------------------------------------#

    tracks = {}

    for media, slices in slicing.output.items(): # iterate as a pair the item and its slices
        # iterate the slices for each media item as a pair
        # so [0, 1, 2, 3, 4] goes [0, 1], [1, 2], [2, 3]
        pos = 0 # establish that we start each track at 0.0 seconds on timeline
        sr = get_sr(media) # also keep the sample rate for later conversions to seconds
        for start, end in zip(slices, slices[1:]):
            # convert to seconds for reaper
            start /= sr
            end /= sr

            item = {
                "file" : media, # provide the file name (can be absolute or relative actually...)
                "length" : end - start, # provide the length of the item
                "start" : start, # provide the start of the item
                "position" : pos # this item is at the position stored in 'pos'
            }

            pos += end - start # increment pos by the length of this item
            # this way we get the items nicely lined up like:
            # |item|item|item|item|
            # in the reaper session

            if media not in tracks: # if this is the first item
                tracks[media] = [item] # create a new list at that key containing the item
            else:
                tracks[media].append(item) # otherwise append it

    render_tracks(
        (Path(sink) / "reaper_segmentation.rpp").expanduser(),
        data = tracks
    )
