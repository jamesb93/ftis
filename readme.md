# ftis - finding things in stuff

**`ftis`**, (finding things in stuff) is a framework for data manipulation, management, creation and munging in Python 3.8+. It is designed for creative use, mainly for my own preoccupations with scraping audio and then analysing, segmenting and tagging this to create labelled corpuses. The framework however, is fairly generic in structure and could be extended to fit individual needs such as investigative journalism or more stock standard data processing.

 The overall architecture can be conceived in two parts; 'analysers' and 'chains'. `ftis` constructs series of connected 'analysers' in 'chains' which allows sequential stages to transmit their outputs to the following inputs. Analysers are represented as a single class making the framework extensible and simple to develop for. Inside the class a number of prefab methods are given to the user to implement necessary functionality and complicated processes can work around these obligatory bits of code quite easily. With this in mind, an analyser might perform web scraping, audio descriptor analysis, offline DSP processing, segmentation, call another command line tool or anything!

 'Chains' are described in `YAML` format so it's simple to write and simple to read.

**`ftis`** has a strong concept of metadata retention (in a good way!) where logs are automatically generated when a chain is run as well as creating a trace of all the artefacts that are created in the process. When you come back to the results of a process in the future, its not mysterious what the source material was, or what kind of processing occurred along the way.

## Installation

Right now, the best way to use **`ftis`** is to fork this repository and to `clone` it to your machine. Refer to the "Workflow" section on how to use it.

## Workflow

### `new` and `run`

#### new
New analysers can be created with the command `python3 run.py new -n name_of_new_analyser`.
This will generate a bare bones template in the 'analysers' folder of the ftis module. You can then edit the newly generated files to design the functionality of your new analyser.

#### run 

Running a chain of analysers is executed with the command `python3 run.py run -c /path/to/config.yaml`

For more information on how to structure the `YAML` file, refer either to `configs/basic.yaml` or the "Configuration" section.

## Configuration

Configurations are described in a `YAML` file. An example is provided at `config/basic.yaml`.

A configuration requires three things:

1. A `source`. This is the first input to pass to the first analyser in the chain. This can be anything as long as the analyser can make sense of the input. In most of the default examples these are `json` files, or strings pointing to directories.
2. A `folder`. This is the folder which is created and houses all of the outputs when running the configuration
3. Some `analysers` need to be implemented in the chain.

A basic structure would look something like this:

```yaml
source: ~/dev/crackle/slice
folder: ~/dev/crackle/analysis

analysers:
    mfcc:
        fftsettings: "4096 1024 4096"
        numcoeffs: 13
        
    stats:
        numderivs: 3
        flatten: True

    dimension_reduction:
        components: 10
        post_scaling: "standardise"
```

## Contributing

If you feel up to contributing plumbing code or your own analysers please feel free to do via github.

1. Fork this repository
2. Checkout a branch with your new feature
3. Implement feature
4. Make a pull request!



