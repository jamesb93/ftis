import soundfile as sf
from typing import Union, Tuple, List
from pathlib import Path
try:
    import simdjson
except ImportError:
    import json as simdjson


def write_json(json_file_path: str, in_dict: dict) -> None:
    """Takes a dictionary and writes it to JSON file"""
    with open(json_file_path, "w+") as fp:
        simdjson.dump(in_dict, fp, indent=4)


def read_json(json_file_path: str) -> dict:
    """Takes a JSON file and returns a dictionary"""
    with open(json_file_path, "r") as fp:
        data = simdjson.load(fp)
        return data


def peek(audio_file_path: Union[str, Path], output: str = "np"):
    """
    Returns a tuple of audio data and its sampling rate
    The audio data can be a numpy array or list
    """
    data, sr = sf.read(audio_file_path)
    data = data.transpose()
    if output == "list":
        return data.tolist(), sr
    if output == "np":
        return data, sr


def get_duration(path: Union[str, Path]) -> float:
    data, sr = peek(path)
    return len(data) / sr
