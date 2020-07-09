from ftis.analyser import Flux, FluidMFCC

f = Flux()
g = FluidMFCC()
h = Flux()
z = Flux()

# audio = Path("audio")
# some_files = [x for x in ]
# source = Source() # maybe does some extra file management in here or something
# world = FTISWorld() # a world in which objects are instantiated and then you connect them together
# overloaded methods would then take care of everything for you!

g.output = "audio/files"

idea1 = f >> g
idea1 >> z
z >> g
i >> a

ftis.run()

print(f.input)
print(h.input)
print(z.input)
