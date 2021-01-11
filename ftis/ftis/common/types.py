from dataclasses import dataclass, field

@dataclass
class FTISType:
    """
    Base type for FTIS objects
    Everything inside is a dictionary
    """
    data:dict = field(default_factory=dict)

    def __iter__(self):
        yield from self.data

    def __len__(self):
        return len(self.data)

@dataclass
class Indices(FTISType):
    def __iter__(self):
        yield from self.data.items()
    ext:str = ".json"

@dataclass
class AudioFiles(FTISType):
    ext:str = ".json"
    def __post_init__(self):
        """Ensure that the paths are for audio files"""
        self.data = {x for x in self.data if x.suffix in [".wav", ".aiff", ".aif"]}

@dataclass
class Data(FTISType):
    ext:str = ".json"
