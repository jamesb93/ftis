# ftis - finding things in stuff

`ftis` is a framework for data manipulation, management, creation and munging in Python 3.8+. It is designed for creative use, mainly for my own preoccupations with segmenting, analysing, organising, discovering structure within, and composing with audio corpora.

## Architecture
The overall architecture can be conceived in two parts; 'analysers' and 'processes'. A `ftis` 'process' can house any number of 'analysers' that can be chained and connected in different ways. A python script can house any number of processes and therefore you can compose multiple processes. Inside of a process, `ftis` makes connections between a source, the analysers and an output.

<!-- ### Analysers
Analysers are just classes, making the framework extensible and simple to develop for. Inside the class a number of prefabricated methods help implement core functionality and complicated processes can work around these obligatory bits of code. The obligatory components are inherited through a superclass so most of the code that you write is related to the design of the class or algorithm rather than dealing with `ftis` itself. With this in mind, an analyser might perform web scraping, audio descriptor analysis, offline DSP processing, segmentation, call another command line tool or anything!

`ftis` has a strong concept of metadata retention (in a good way! ) where logs are automatically generated when a chain is run as well as creating a trace of all the artefacts that are created in the process. When you come back to the results of a process in the future, its not mysterious what the source material was, or what kind of processing occurred along the way. -->

## Installation

You can install `ftis` using `pip install ftis`. This will pull down the necessary dependencies so that all of the analysers that ship with `ftis` work straight away.

You can also fork this repository and `clone` it to your machine.

## Workflow

The simplest setup is to have a virtual environment setup with ftis installed as a module. `cd` to the clone of your fork of `ftis` and enter the module (the directory containing `setup.py`). Once there run `pip install -e .` to install `ftis` to your activated virtual environment. Once you've designed your script you can easily run it with `python mycoolscript.py`. Of course if you have used `pip` to install `ftis` then none of the previous advice applies.

There are some good examples of scripts in the examples directory of this repository. Otherwise the basic structure looks like this:

```python

# import ftis modules that we need
from ftis.analyser.slicing import FluidNoveltyslice # novelty slicing
from ftis.process import FTISProcess # a ftis 'process'
from ftis.corpus import Corpus # a corpus object

src = Corpus("~/corpus-folder/corpus1") # corpus object collects audio files at this directory
out = "~/corpus-folder/slicing" # set an output folder

process = FTISProcess( # instantiate an instance of the process
    source=src, # provide the source and the output to the process
    folder=out
)

process.add( # now add different 'analysers' to the process
    FluidNoveltyslice(threshold=0.35, feature=1),
    ExplodeAudio()
)

if __name__ == "__main__":
    process.run() # and run (inside this block for multiprocessing to work)
```

and thats it! For more information read the full documentation.

## Contributing

If you feel up to contributing plumbing code or your own analysers please feel free to do via github.

1. Fork this repository
2. Checkout a branch with your new feature
3. Implement feature
4. Make a pull request!



