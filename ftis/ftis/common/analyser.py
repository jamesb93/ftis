from ftis.common.exceptions import OutputNotFound
from ftis.common.types import ftypes
from ftis.common.io import read_json, write_json


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
        self.cache_possible = False

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
        # TODO: Implement a method for knowing about folder-y outputs before they're made (workables!)
        return True

    def compare_meta(self) -> bool:
        old_meta = read_json(self.process.metapath)
        success = old_meta["success"][f"{self.order}_{self.name}"]
        pcopy = dict(old_meta)
        ignored_keys = [
            "process", 
            "logger", 
            "input", 
            "output", 
            "input_type", 
            "dump_type",
            "order",
            "dumpout",
            "cache",
            "cache_possible"] #FIXME this should not be duplicated
        
        for x in ignored_keys:
            old_meta.pop("cache", None)
            pcopy.pop("cache", None)

        return pcopy == old_meta and success

    def cache_exists(self) -> bool:
        if self.dump_path.exists(): # TODO: type and metadata checking
            if self.dump_type == ftypes.folder:
                return self.folder_integrity()
            else:
                return True 

    def update_success(self, status: bool):
        try: #FIXME combine these two try statements
            self.process.metadata = read_json(self.process.metapath)
        except FileNotFoundError:
            self.process.metadata = {}

        try:
            success = self.process.metadata["success"] # extract the progress dict
        except KeyError:
            success = {} # in the situation that progress doesnt exist yet

        success[f"{self.order}_{self.name}"] = status # update the status of this analyser
        self.process.metadata["success"] = success # modify the original
        write_json(self.process.metapath, self.process.metadata)

    def do(self):
        self.log("Initiating")

        # Determine whether we caching is possible
        if self.cache and self.cache_exists()and self.compare_meta() and self.process.metapath.exists():
            self.cache_possible = True

        # Set the status to failure and only update to success if it all ends correctly
        self.update_success(False)
        if self.cache_possible:
            self.load_cache()
            self.process.fprint(f"{self.name} was cached")
        else:
            self.run()
            self.dump()

        if self.output != None: #TODO comprehensive output checking
            self.log("Ran Successfully")
            self.update_success(True)
        else:
            self.log("Ouput was invalid")
            raise OutputNotFound(self.name)

    def run(self):
        """Method for running the processing chain from input to output"""
