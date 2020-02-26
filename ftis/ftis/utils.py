import os
import yaml
import csv
import soundfile as sf
import simpleaudio as sa
# JSON importing
try:
    import rapidjson as rj
except ImportError:
    import json as rj

def lines_to_list(input_file: str) -> list:
    """Take the lines of a file and return it as a list"""
    with open(input_file, 'r') as f:
        lines = f.readlines(0)
        content = [x.strip() for x in lines]
        return content

def check_make(dir_path: str):
    """Create a directory if it doesn't exist"""
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        print(f'Directory {dir_path} already exists.')

def cd_up(path: str, num: int) -> str:
    """Given path, traverse num directories up from it"""
    t_path = path
    for _ in range(num):
        t_path = os.path.dirname(t_path)
    return t_path

def read_yaml(yaml_file):
    with open(yaml_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def list_to_coll(list_in: list, out_file: str):
    '''
    Turns a list into a coll.

    list: Provide a list to convert
    out_file: a path to a file where the coll will be saved
    '''
    f = open(out_file, 'w+')
    counter = 0
    for item in list_in:
        f.write(f'{counter}, {item};')
        counter += 1
    f.close()

def check_size(path: str, min_size: int) -> bool:
    """
    Check's the size of a fyle in bytes.
    Returns true if the file has a size.
    Used to avoid empty files.
    """
    try:
        if os.path.getsize(path) >= min_size and os.path.getsize(path) <= 150000000:
            return True
    except OSError:
        return False

def check_ext(path: str, extensions: list) -> bool:
    """Given a path and a list of legal extensions it either returns false or true."""
    ext = os.path.splitext(path)[1]
    try:
        dummy = extensions.index(ext)
    except ValueError:
        return True
    else:
        return False
    
def wipe_dir(dir: str):
    """Wipe a directory given a path"""
    for file_name in os.listdir(dir):
        os.remove(os.path.join(dir, file_name))

def bytes_to_mb(val: int) -> float:
    """convert bytes to mb"""
    return val * 0.000001

def get_path() -> str:
    """returns path of script being run"""
    return os.path.dirname(os.path.realpath(__file__))

def samps2ms(ms: float, sr: int) -> float:
    '''
    convert samples to milliseconds given a sampling rate
    '''
    return (ms / sr) * 1000.0

def ms2samps(samples: int, sr: int) -> int:
    '''
    convert milliseconds to samples given a sample rate
    '''
    return (samples/1000) * sr

def ds_store(file_list: list) -> list:
    '''
    Remove .DS_Store if in a list
    '''
    if '.DS_Store' in file_list:
        file_list.remove('.DS_Store')
    return file_list

def bufspill(audio_file_path: str):
    """Reads an audio file and converts its content to a numpy array"""
    try:
        t_data, _ = sf.read(audio_file_path)
        return t_data.transpose()
    except:
        print(f'Could not read: {audio_file_path}')

def write_json(json_file_path: str, in_dict: dict):
    """Takes a dictionary and writes it to JSON file"""
    with open(json_file_path, 'w+') as fp:
        rj.dump(in_dict, fp, indent=4) 

def read_json(json_file_path: str) -> dict:
    """Takes a JSON file and returns a dictionary"""
    with open(json_file_path, 'r') as fp:
        data = rj.load(fp)
        return data

def walkman(audio_path: str):
    """Play a sound file given a path to a valid piece of audio"""
    wave_obj = sa.WaveObject.from_wave_file(os.path.join(audio_path))
    play_obj = wave_obj.play()
    play_obj.wait_done()

def printp(string_to_print: str):
    """A uniform way for printing status updates in scripts"""
    print(f'\n---- {string_to_print} ----')

def printe(string_to_print: str):
    """A uniform way for printing errors in scripts"""
    print(f'!!!! {string_to_print} !!!!')
