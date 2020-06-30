import os
from ftis.common.utils import read_yaml
from ftis.common.types import Ftypes
from pathlib import Path


class FTISAnalyser:
    """Every analyser inherits from this class"""

    def __init__(self, parent_process):
        self.parent_process = parent_process
        self.config = self.parent_process.config
        self.logger = self.parent_process.logger
        self.input = ""
        self.output = ""
        self.input_type = ""
        self.output_type = ""
        self.parameters = {}
        self.parameter_template = {}
        self.name = self.__class__.__name__
        self.order: int = -1
        self.cache_exists = False

    def log(self, log_text):
        self.logger.debug(f"{self.name}: {log_text}")

    def validate_parameters(self):
        """Validates parameters from the config against the template"""
        self.log("Validating parameters")
        module_parameters = Path(__file__).parent.parent / "analysers" / self.name / "parameters.yaml"
        self.parameter_template = read_yaml(module_parameters)

        # Put the caching parameter in no matter what
        if not self.parameter_template:
            self.parameter_template = {"cache" : {"default" : False}}
        else:
            self.parameter_template["cache"] = {"default": False}

        # Now overwrite any analyser specific caching with the global
        try: 
            self.parameter_template["cache"] = {"default": self.parent_process.config["cache"]}
        except KeyError:
            pass

        # Now assign the defaults to the parameters 
        for key in self.parameter_template:
            self.parameters[key] = self.parameter_template[key]["default"]

        # If there are any things specified in the config overwrite the previously written defaults
        try:
            for parameter in self.config["analysers"][self.name]:
                self.parameters[parameter] = self.config["analysers"][self.name][parameter]
        except TypeError:
            self.log("using all default parameters")

        self.set_output()

    def set_output(self):
        """Create the output for path/type"""
        self.output = self.parent_process.base_dir / f"{self.order}_{self.name}{self.output_type}"

        if self.output.exists(): #TODO more rigorous caching techniques here.
            # TODO: You could look project at what should be created and see if they all exist
            if self.output_type == Ftypes.folder:
                self.cache_exists = len(list(self.output.iterdir())) > 0 # if its a folder lets see if there is anything in it
            else:
                self.cache_exists = True # We have to flag here because we make the output anyway and cannot check later

        if self.output_type == Ftypes.folder:
            self.output.mkdir(exist_ok=True)

        self.log("Setting outputs")

    def do(self):
        self.log("Executing process")
        if self.parameters["cache"] == True:
            self.log("Intending to cache")
            if self.cache_exists:
                if self.parent_process.metapath.exists() and self.compare_meta():
                    self.parent_process.fprint(f"{self.name} was cached!") # Display on console
                elif not self.parent_process.metapath.exists():
                    self.log("Cache was true but there was no metadata to compare parameters for")
                    self.parent_process.fprint(f"{self.name} was cached!") # Display on console
            else:
                self.run()
                self.log("Cache was true but there was no cache")
        else:
            self.run()
            self.log("Ran without caching")

        self.log("Finished processing")

    def compare_meta(self)-> bool:
        old_meta = read_yaml(self.parent_process.metapath)["analysers"][self.__class__.__name__]
        pcopy = dict(self.parameters)
        old_meta.pop("cache", None)
        pcopy.pop("cache", None)
        return pcopy == old_meta

    def dry(self):
        self.log("Executing process")
        if self.parameters["cache"] == True:
            self.log("Intending to cache")
            
            if self.cache_exists: 
                if self.parent_process.metapath.exists() and self.compare_meta():
                    self.parent_process.fprint(f"{self.name} was cached!") # Display on console
                elif not self.parent_process.metapath.exists():
                    self.dry_print(f"No metadata to cache against")
            else:
                self.parent_process.dry_print(f"Cache was true but there was no cache or something changed")
                self.log("Cache was true but there was no cache")
        else:
            self.parent_process.dry_print(f"{self.name}: Ran without caching")
            self.log("Ran without caching")

        self.log("Finished processing")


    def run(self):
        """Method for running the processing chain from input to output"""
