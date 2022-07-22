import soundfile as sf
import audioread
from typing import Union, Tuple, List
from pathlib import Path
import json


def write_json(json_file_path: str, in_dict: dict) -> None:
    """Takes a dictionary and writes it to JSON file"""
    with open(json_file_path, "w+") as fp:
        json.dump(in_dict, fp, indent=4)


def read_json(json_file_path: str) -> dict:
    """Takes a JSON file and returns a dictionary"""
    with open(json_file_path, "r") as fp:
        data = json.load(fp)
        return data


def peek(audio_file_path: Union[str, Path], output: str = "np"):
    """
    Returns a tuple of audio data and its sampling rate
    The audio data can be a numpy array or list
    """
    data, sr = sf.read(audio_file_path, dtype="float32")
    data = data.transpose()
    if output == "list":
        return data.tolist(), sr
    if output == "np":
        return data, sr


def get_duration(path:Union[str, Path], units:str='ms') -> float:
    data, sr = peek(path)
    if units == 'ms':
        return len(data) / sr * 1000
    if units == 'samples':
        return len(data)
    if units == 'seconds':
        return len(data) / sr


def get_sr(path: Union[str, Path]) -> int:
    try:
        with sf.SoundFile(path) as f:
            return int(f.samplerate)
    except RuntimeError:
        with audioread.audio_open(path) as f:
            return int(f.samplerate)
