def samps2ms(samples: float, sr: int) -> float:
    """samples to milliseconds given a sampling rate"""
    return (samples / sr) * 1000.0


def ms2samps(ms: int, sr: int) -> int:
    """milliseconds to samples given a sample rate"""
    return (ms * 0.001) * sr


def secs2ms(seconds: int) -> int:
    """seconds to milliseconds"""
    return seconds * 1000
