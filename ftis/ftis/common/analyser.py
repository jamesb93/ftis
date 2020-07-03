class FTISAnalyser:
    """Every analyser inherits from this class"""

    def __init__(self, dumpout=False):
        self.process = None  # pass the parent process in
        self.logger = None
        self.input = ""
        self.output = None
        self.input_type = ""
        self.dump_type = ""
        self.name = self.__class__.__name__
        self.order: int = -1
        self.cache_exists = False
        self.dumpout = dumpout

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
        self.run()
        self.log("Ran Successfully")
        assert self.output != None  # add this back in with a proper exception
        # if self.dumpout == True:
        self.dump()
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

        # self.log("Finished processing")

    # def compare_meta(self) -> bool:
    #     old_meta = read_yaml(self.process.metapath)["analysers"][
    #         self.__class__.__name__
    #     ]
    #     pcopy = dict(self.parameters)
    #     old_meta.pop("cache", None)
    #     pcopy.pop("cache", None)
    #     return pcopy == old_meta

    # def dry(self):
    #     self.log("Executing process")
    #     if self.parameters["cache"] == True:
    #         self.log("Intending to cache")

    #         if self.cache_exists:
    #             if self.process.metapath.exists() and self.compare_meta():
    #                 self.process.fprint(
    #                     f"{self.name} was cached!"
    #                 )  # Display on console
    #             elif not self.process.metapath.exists():
    #                 self.dry_print(f"No metadata to cache against")
    #         else:
    #             self.process.dry_print(
    #                 f"Cache was true but there was no cache or something changed"
    #             )
    #             self.log("Cache was true but there was no cache")
    #     else:
    #         self.process.dry_print(f"{self.name}: Ran without caching")
    #         self.log("Ran without caching")

    # self.log("Finished processing")

    def run(self):
        """Method for running the processing chain from input to output"""
