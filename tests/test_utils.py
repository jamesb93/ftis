from ftis.common.utils import (
    bytes_to_mb,
    samps2ms,
    ms2samps,
    rm_ds
)


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


def test_rm_ds():
    test_list = [
        ".DS_Store",
        "foo.bar"
    ]
    result = rm_ds(test_list)
    assert len(result) == 1
    assert test_list[0] == "foo.bar"
    assert ".DS_Store" not in result
