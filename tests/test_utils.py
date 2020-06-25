from ftis.common.utils import (
    bytes_to_mb,
    samps2ms,
    ms2samps,
    rm_ds,
    filter_extensions
)
from pathlib import Path



def test_filter_extensions():
    test = [Path("foo.wav"), Path("grab.wav"), Path("foo.csv")]
    truth = [Path("foo.wav"), Path("grab.wav")]
    filtered = filter_extensions(test, (".wav"))
    assert truth == filtered


def test_bytes_to_mb():
    base_value = 10
    test_value = bytes_to_mb(base_value)
    assert test_value == 10 * 0.000001


def test_samps2ms():
    samps = 44100
    sr = 44100
    assert samps2ms(samps, sr) == 1000


def test_ms2samps():
    ms = 1000
    sr = 44100
    assert ms2samps(ms, sr) == 44100.0
