from ftis.common.exceptions import OutputNotFound
from ftis.common.types import ftypes
from ftis.common.io import read_json, write_json


class FTISAnalyser:
    """Every analyser inherits from this class"""

    def __init__(self, cache=False):
        self.process = None  # pass the parent process in
        self.input = None # This can be anything
        self.output = None # This can be anything
        self.input_type = "" #TODO Implement fixed types here
        self.dump_type = ""
        self.name = self.__class__.__name__
        self.order: int = -1
        self.cache = cache
        self.cache_possible = False

    def log(self, log_text):
        self.process.logger.debug(f"{self.name}: {log_text}")

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
        self.process.metadata = self.process.metadata
        self.process.prev_meta = self.process.prev_meta
        ident = f"{self.order}_{self.name}"
        try:
            new_params = self.process.metadata["analyser"][ident]
        except KeyError:
            new_params = False

        try:
            old_params = self.process.prev_meta["analyser"][ident]
        except KeyError:
            old_params = False

        try:
            success = self.process.prev_meta["success"][f"{self.order}_{self.name}"]
        except KeyError:
            success = False

        return old_params == new_params and success

    def cache_exists(self) -> bool:
        if self.dump_path.exists():
            if self.dump_type == ftypes.folder:
                return self.folder_integrity()
            else:
                return True
        else:
            return False

    def update_success(self, status: bool):
        try:
            existing_metadata = read_json(self.process.metapath)
        except FileNotFoundError:
            existing_metadata = {}

        try:
            success = existing_metadata["success"] # extract the progress dict
        except KeyError:
            success = {} # in the situation that progress doesnt exist yet

        success[f"{self.order}_{self.name}"] = status # update the status of this analyser
        # here we need to join any existing data into the metadata
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
