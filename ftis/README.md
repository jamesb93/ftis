# ftis - finding things in stuff

`ftis` is a framework for data manipulation, management, creation and munging in Python 3.8+. It is designed for creative use, mainly for my own preoccupations with segmenting, analysing, organising, discovering structure within, and composing with audio corpora.

## Architecture
The overall architecture can be conceived in two parts; 'analysers' and 'worlds'. A `ftis` 'world' can house any number of 'analysers' that can be chained and connected in different ways. A python script can house any number of worlds and therefore you can compose multiple processes. Inside of a world, `ftis` makes connections between a source, the analysers and an output (known as the _sink_).

## Installation
You can install `ftis` using `pip install ftis`. This will pull down the necessary dependencies so that all of the analysers that ship with `ftis` work straight away.

You can also fork this repository and `clone` it to your machine.

## Workflow
The simplest setup is to have a virtual environment setup with ftis installed as a module. `cd` to the clone of your fork of `ftis` and enter the module (the directory containing `setup.py`). Once there run `pip install -e .` to install `ftis` to your activated virtual environment. Once you've designed your script you can easily run it with `python mycoolscript.py`. Of course if you have used `pip` to install `ftis` then none of the previous advice applies.

There are some good examples of scripts in the examples directory of this repository. Otherwise the basic structure looks like this:

```python

# import ftis modules that we need
from ftis.analyser.slicing import FluidNoveltyslice # novelty slicing
from ftis.world import World # a ftis 'world'
from ftis.corpus import Corpus # a corpus object

src = Corpus("~/corpus-folder/corpus1") # corpus object collects audio files at this directory
out = "~/corpus-folder/slicing" # set an output folder

# instantiate an instance of the process
world = World(sink=out)

# Connect together processes using >>
src >> FluidNoveltySlice(threshold=0.35, feature=1) >> ExplodeAudio()

# now add a Corpus node to our world
world.build(src)

if __name__ == "__main__":
    world.run() # finally run the chain of connected analysers
```

and thats it! For more information read the full documentation.

## Contributing

If you feel up to contributing plumbing code or your own analysers please feel free to do via github.

1. Fork this repository
2. Checkout a branch with your new feature
3. Implement feature
4. Make a pull request!
