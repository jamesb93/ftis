from dataclasses import dataclass


@dataclass
class FTISTypes:
    json: str = ".json"
    text: str = ".txt"
    folder: str = ""
    python: str = ".py"


ftypes = FTISTypes()
