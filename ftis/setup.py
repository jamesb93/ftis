import setuptools
from pathlib import Path

readme = Path("../readme.md")

with open(readme, encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="ftis",
    version="1.0.1",
    author="James Bradbury",
    url="https://github.com/jamesb93/ftis",
    license="GLPv3+",
    author_email="jamesbradbury93@gmail.com",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    description="The finding things in stuff package.",
    packages=["ftis"],
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
