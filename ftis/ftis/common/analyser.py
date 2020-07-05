from ftis.common.exceptions import OutputNotFound
from ftis.common.types import ftypes
from ftis.common.io import read_json


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
        """Defined in the analyser that inherits this class"""

    def folder_integrity(self) -> bool:
        # TODO: implement folder integirty checking for analysers like Explode/Collapse
        # We can know this from looking at the previous outputs
        return True

    # def compare_meta(self) -> bool:
    #     old_meta = read_json(self.process.metapath)["analysers"][
    #         self.__class__.__name__
    #     ]
    #     pcopy = dict(self.parameters)
    #     old_meta.pop("cache", None)
    #     pcopy.pop("cache", None)
    #     return pcopy == old_meta

    def do(self):
        self.log("Initiating")
        if self.dump_path.exists(): # TODO: type and metadata checking
            if self.dump_type == ftypes.folder:
                self.cache_exists = self.folder_integrity()
            else:
                self.cache_exists = True

        # if self.cache and self.cache_exists and self.process.metapath.exists() and self.compare_meta():
        if self.cache and self.cache_exists and self.process.metapath.exists():
            self.load_cache()
            self.process.fprint(f"{self.name} was cached")
        else:
            self.run()
            self.dump()

        if self.output != None:
            self.log("Ran Successfully")
        else:
            self.log("Ouput was invalid")
            raise OutputNotFound(self.name)

    def run(self):
        """Method for running the processing chain from input to output"""
