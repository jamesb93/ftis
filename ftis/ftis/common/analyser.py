from ftis.common.exceptions import OutputNotFound, ChainIOError
from ftis.common.io import read_json, write_json
from ftis.common.utils import ignored_keys, create_hash
from collections.abc import Callable
from collections import OrderedDict
from pathlib import Path


class FTISAnalyser:
    """Every analyser inherits from this class"""
    def __init__(self, cache=False, pre=None, post=None):
        self.process = None  # pass the parent process in
        self.input = None  
        self.output = None
        self.dump_path: Path = None
        self.model_dump: Path = None  #
        self.name = self.__class__.__name__
        self.order: int = -1
        self.cache: bool = cache
        self.cache_possible: bool = False
        self.pre: Callable = pre
        self.post: Callable = post
        # Overloading Stuff
        self.scripting = True
        self.suborder = 0
        self.parent = None
        self.chain = OrderedDict()
        self.parent_string = self.__class__.__name__
        self.identity = {}
        self.workables = []

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __rshift__(self, right):
        # right.order = self.order + 1
        self.scripting = True
        self.chain[right] = None
        return right
    
    def traverse_parent_parameters(self):
        self.parent_parameters[self.parent.__class__.__name__] = self.parent.identity["hash"]
        if hasattr(self.parent, 'parent'): # if the parent has a parent
            self.parent.traverse_parent_parameters()

    def create_identity(self) -> None:
        p = {
            k: str(v) 
            for k, v in vars(self).items() 
            if k not in ignored_keys
        }
        self.parent_parameters = {}
        self.traverse_parent_parameters()
        self.identity["hash"] = create_hash(self.parent_parameters, p)

    def compare_meta(self) -> bool:
        # TODO You could use a hashing function here to determine the similarity of the metadata
        # TODO You should use a hashing function because adding things to the front of the chain makes it not equal between runs
        try:
            new_params = self.process.metadata["analyser"][self.identity["hash"]]["identity"]
        except KeyError:
            new_params = False

        try:
            old_params = self.process.prev_meta["analyser"][self.identity["hash"]]["identity"]
        except KeyError:
            old_params = False

        try:
            success = self.process.prev_meta["success"][self.identity["hash"]]
        except KeyError:
            success = False
        return old_params == new_params and success

    def cache_exists(self) -> bool:
        if self.dump_path.exists():
            return True
        else:
            return False

    def update_success(self, status: bool) -> None:
        try:
            existing_metadata = read_json(self.process.metapath)
        except FileNotFoundError:
            existing_metadata = {}

        try:
            success = existing_metadata["success"]  # extract the progress dict
        except KeyError:
            success = {}  # progress doesnt exist yet

        success[self.identity["hash"]] = status  # update the status of this analyser
        # join any existing data into the metadata
        self.process.metadata["success"] = success  # modify the original
        write_json(self.process.metapath, self.process.metadata)

    def walk_chain(self) -> None:
        self.log("Initialising")
        # Determine whether we caching is possible
        if self.cache and self.cache_exists() and self.compare_meta() and self.process.metapath.exists():
            self.cache_possible = True
        
        self.update_success(False)
        if self.cache_possible:
            self.load_cache()
            self.process.fprint(f"{self.name} was cached")
        else:
            if self.pre: # preprocess
                self.pre(self)
            self.run()
            if self.post: # postprocess
                self.post(self)

        if self.output != None: 
            self.log("Ran Successfully")
            self.update_success(True)
        else:
            self.log("Output was invalid")
            raise OutputNotFound(self.name)

        self.dump()
        # Pass output to the input of all of connected things
        # TODO: redo type checking
        for forward_connection in self.chain:
        #     if self.output_type in forward_connection.input_type:
            forward_connection.input = self.output
            forward_connection.walk_chain()
        #     else:
        #         raise ChainIOError(self, forward_connection)

    def _get_parents(self) -> None:
        self.parent_string = (
            f"{self.parent.__class__.__name__}.{self.parent_string}"
        )

    def set_dump(self) -> None:
        self._get_parents()
        if self.scripting:
            self.dump_path  = (
                self.process.sink / 
                f"{self.order}.{self.suborder}-{self.parent_string}.json"
            )
            self.model_dump = (
                self.process.sink / 
                f"{self.order}.{self.suborder}-{self.parent_string}.joblib"
            )


    def log(self, log_text: str) -> None:
        try:
            self.process.logger.debug(f"{self.name}: {log_text}")
        except AttributeError:
            pass

    def folder_integrity(self) -> bool:
        # TODO: implement folder integrity checking for analysers like Explode/Collapse
        # TODO: Implement a method for knowing about folder-y outputs before they're made (workables!)
        return True

    def load_cache(self) -> None:
        """Implemented in the analyser"""

    def dump(self) -> None:
        """Defined in the analyser that inherits this class"""

    def adapt_input(self):
        """Adapters are made on a per object basis"""

    def run(self) -> None:
        """Method for running the processing chain from input to output"""
