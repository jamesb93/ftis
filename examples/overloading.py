from ftis.analyser import Flux, FluidMFCC
from ftis.
# from ftis.process import World

audio = "/Users/james/dev/ftis_example/project/audio"
# some_files = [x for x in ]
# source = Source() # maybe does some extra file management in here or something
# world = FTISWorld() # a world in which objects are instantiated and then you connect them together
# overloaded methods would then take care of everything for you!
# world = World()
# TODO Find a way to absorb inputs that are not FTISAnalysers.
# One solution will be a special analyer that sets inputs.
f = Flux()
g = FluidMFCC()

# world.add(f, g)
f.set_input(audio)
f >> g

# world.execute()

print(f.input)
print(g.input)
