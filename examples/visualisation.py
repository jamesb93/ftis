print('Sorry, this example is currently a bit broken!')
# from ftis.analyser import (
#     CollapseAudio,
#     FluidMFCC,
#     Stats, 
#     Standardise, 
#     Normalise 
# )
# from ftis.corpus import Corpus
# from ftis.visualisation import Visualiser
# from ftis.process import FTISProcess as Chain

# src = Corpus("~/Documents/Max 8/Packages/TB2-Alpha04c-Max/media")
# folder = "~/visualiser"

# process = Chain(source=src, folder=folder)

# process.add(
#     CollapseAudio(),
#     FluidMFCC(cache=1),
#     Stats(flatten=1, numderivs=1, cache=1),
#     Standardise(cache=1),
#     Normalise(cache=1),
#     Visualiser()
# )

# if __name__ == "__main__":
#     process.run()
