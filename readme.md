# ftis - finding things in stuff

`ftis` is a framework for data manipulation, management, creation and munging in Python 3.8+. It is designed for creative use, mainly for my own preoccupations with segmenting, analysing, organising, discovering structure within, and composing with audio corpora.

The overall architecture can be conceived in two parts; 'analysers' and 'processes'. `ftis` generates connections between a source, the chains and a sink and ships with two behaviours for connectivity. In "chain" mode (the default) each analyser's output is connected to the input of the next one in the chain so data is transformed in a typical processing pipeline. In "batch" mode every analyser takes the source as its input and it applies each process to the same source.

Analysers are classes making the framework extensible and simple to develop for. Inside the class a number of prefab methods help implement core functionality and complicated processes can work around these obligatory bits of code quite easily. The obligatory components are inherited through a superclass so most of the code that you write is related to the design of the class or algorithm rather than dealing with `ftis` itself. With this in mind, an analyser might perform web scraping, audio descriptor analysis, offline DSP processing, segmentation, call another command line tool or anything!

`ftis` has a strong concept of metadata retention (in a good way! ) where logs are automatically generated when a chain is run as well as creating a trace of all the artefacts that are created in the process. When you come back to the results of a process in the future, its not mysterious what the source material was, or what kind of processing occurred along the way.

## Installation

Right now, the best way to use `ftis` is to fork this repository and to `clone` it to your machine. Refer to the "Workflow" section on how to use it.

## Workflow

The simplest setup is to have a virtual environment setup with ftis installed as a module. `cd` to the clone of your fork of `ftis` and enter the module (the directory containing `setup.py`). Once there run `pip install -e .` to install `ftis` to your activated virtual environment. Once you've designed your script you can easily run it with `python mycoolscript.py`.

There are some good examples of scripts in the examples directory of this repository. Otherwise the basic structure looks like this:

```python

from ftis.analyser import (
    FluidNoveltyslice, 
    ExplodeAudio, 
    CollapseAudio
) # import the analysers that you want to use from ftis.analyser
from ftis.process import FTISProcess # import the FTISProcess class

src = "/home/james/Documents/media" # set up the source 
folder = "/home/james/Documents/analysis" # set up the output folder

process = FTISProcess(source=src, folder=folder) # create an instance of the FTISProcess

process.add(
    FluidNoveltyslice(threshold=0.35, feature=1),
    ExplodeAudio()
) # Add some analysers to your process (the order of the args is the order of the chain)

process.run() # call the run() method

```

and thats it!

## Contributing

If you feel up to contributing plumbing code or your own analysers please feel free to do via github.

1. Fork this repository
2. Checkout a branch with your new feature
3. Implement feature
4. Make a pull request!



