from dataclasses import dataclass, field


@dataclass
class Indices:
    data:dict = field(default_factory=dict)
    ext:str = ".json"

@dataclass
class AudioFiles:
    data:dict = field(default_factory=dict)

@dataclass
class Data:
    data:dict = field(default_factory=dict)
    ext:str = ".json"
