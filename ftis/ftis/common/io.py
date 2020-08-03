import soundfile as sf
import rapidjson as rj


def write_json(json_file_path: str, in_dict: dict):
    """Takes a dictionary and writes it to JSON file"""
    with open(json_file_path, "w+") as fp:
        rj.dump(in_dict, fp, indent=4)

def read_json(json_file_path: str) -> dict:
    """Takes a JSON file and returns a dictionary"""
    with open(json_file_path, "r") as fp:
        data = rj.load(fp)
        return data

def peek(audio_file_path: str, output: str = "np"):
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

def get_duration(path):
    data, sr = peek(path)
    return len(data) / sr

