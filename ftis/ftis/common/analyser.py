from ftis.common.exceptions import OutputNotFound


class FTISAnalyser:
    """Every analyser inherits from this class"""

    def __init__(self, dumpout=False, cache=False):
        self.process = None  # pass the parent process in
        self.logger = None
        self.input = ""
        self.output = None
        self.input_type = ""
        self.dump_type = ""
        self.name = self.__class__.__name__
        self.order: int = -1
        self.dumpout = dumpout
        self.cache = cache
        self.cache_exists = False

    def log(self, log_text):
        self.logger.debug(f"{self.name}: {log_text}")

    def set_dump(self):
        self.dump_path = (
            self.process.folder / f"{self.order}_{self.name}{self.dump_type}"
        )

    def dump(self):
        pass

    def do(self):
        self.log("Initiating")

        if self.dump_path.exists(): # TODO: more comprehensive checking here depending on the types
            self.cache_exists = True

        if self.cache and self.cache_exists:
            self.load_cache()
            self.process.fprint(f"{self.name} caching!")
        else:
            self.run()
            self.dump()

        if self.output != None:
            self.log("Ran Successfully")
        else:
            self.log("Ouput was invalid")
            raise OutputNotFound(self.name)
        
        # self.log("Executing process")
        # if self.parameters["cache"] == True:
        #     self.log("Intending to cache")
        #     if self.cache_exists:
        #         if self.process.metapath.exists() and self.compare_meta():
        #             self.process.fprint(
        #                 f"{self.name} was cached!"
        #             )  # Display on console
        #         elif not self.process.metapath.exists():
        #             self.log(
        #                 "Cache was true but there was no metadata to compare parameters for"
        #             )
        #             self.process.fprint(
        #                 f"{self.name} was cached!"
        #             )  # Display on console
        #     else:
        #         self.run()
        #         self.log("Cache was true but there was no cache")
        # else:
        #     self.run()
        #     self.log("Ran without caching")

    # def compare_meta(self) -> bool:
    #     old_meta = read_yaml(self.process.metapath)["analysers"][
    #         self.__class__.__name__
    #     ]
    #     pcopy = dict(self.parameters)
    #     old_meta.pop("cache", None)
    #     pcopy.pop("cache", None)
    #     return pcopy == old_meta

    def run(self):
        """Method for running the processing chain from input to output"""
