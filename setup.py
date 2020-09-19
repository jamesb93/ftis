from setuptools import setup, find_packages
from pathlib import Path

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name="ftis",
    version="1.0.4",
    author="James Bradbury",
    url="https://github.com/jamesb93/ftis",
    license="GLPv3+",
    author_email="jamesbradbury93@gmail.com",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    description="The finding things in stuff package.",
    packages=find_packages(),
    install_requires=[
        "Soundfile",
        "hdbscan",
        "umap-learn",
        "sklearn",
        "pysimdjson",
        "python-flucoma",
        "pydub",
        "scipy",
        "rich",
        "librosa",
    ],
)
