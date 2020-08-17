import os, math, hashlib
import soundfile as sf
import numpy as np
from pathlib import Path


def get_workables(pth):
    temp_workables = []
    for root, _, files in os.walk(pth):
        for f in files:
            full_path = Path(root) / f
            temp_workables.append(full_path)
    return temp_workables


def list_to_coll(list_input: list, out_file: str):
    """Turns a list into a coll."""
    f = open(out_file, "w+")
    counter = 0
    for item in list_input:
        f.write(f"{counter}, {item};")
        counter += 1
    f.close()


def bytes_to_mb(val: int) -> float:
    """convert bytes to mb"""
    return val * 0.000001

def create_hash(*items) -> str:
    """Create a hash from a list of items"""
    m = hashlib.blake2b(digest_size=32)
    for item in items:
        m.update(str(item).encode('utf-8'))
    return m.hexdigest()

