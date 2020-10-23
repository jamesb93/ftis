from ftis.adapter.reaper import render_tracks
from ftis.analyser.slicing import FluidNoveltyslice
from ftis.analyser.descriptor import FluidMFCC
from ftis.analyser.stats import Stats
from ftis.analyser.clustering import AgglomerativeClustering
from ftis.analyser.audio import CollapseAudio
from ftis.world import World
from ftis.corpus import Corpus
from ftis.common.io import get_sr, get_duration
from pathlib import Path

# instantiate
sink = "~/reaperising-ftis-2"
c = Corpus("~/Documents/Max 8/Packages/TB2-Alpha06-MacOS-Max/media")
clustering = AgglomerativeClustering(numclusters=3)

# script connection
c >> CollapseAudio() >> FluidMFCC() >> Stats() >> clustering
w = World(sink = sink)
w.build(c)
if __name__ == "__main__":
    w.run()

    # #---------- Data for render_tracks would look something like this ----------#
    # # data = {
    # #    "track1" : [
    # #        {"file" : None, "length": 1.0, "start": 0.0, "position": 0.0}
    # #    ],
    # #    "track2" : [
    # #        {"file" : None, "length": 1.0, "start": 0.0, "position": 0.0}
    # #    ]
    # # }
    # #---------------------------------------------------------------------------#

    tracks = {}

    for cluster, members in clustering.output.items(): # iterate as a pair the item and its slices
        # iterate cluster number and its members as a pair
        pos = 0 # establish that we start each track at 0.0 seconds on timeline
        for media in members: # iterate each media item for that cluster
            # convert to seconds for reaper
            sr = get_sr(media) # get the sample rate (for conversion2)
            duration = get_duration(media) # get the duration 
            item = {
                "file" : media, # provide the file name (can be absolute or relative actually...)
                "length" :  duration, # provide the length of the item
                "start" : 0.0, # provide the start of the item
                "position" : pos # this item is at the position stored in 'pos'
            }

            pos += duration # increment pos by the length of this item
            # this way we get the items nicely lined up like:
            # |item|item|item|item|
            # in the reaper session

            if cluster not in tracks: # if this is the first item
                tracks[cluster] = [item] # create a new list at that key containing the item
            else:
                tracks[cluster].append(item) # otherwise append it

    render_tracks(
        (Path(sink) / "reaper_clustering.rpp").expanduser(),
        data = tracks
    )
