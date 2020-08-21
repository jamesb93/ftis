import setuptools

setuptools.setup(
    name="ftis",
    version="1.0",
    author="James Bradbury",
    author_email="jamesbradbury93@gmail.com",
    description="The finding things in stuff package.",
    packages=["ftis"],
    install_requires=[
        "Soundfile",
        "hdbscan",
        "umap-learn",
        "sklearn",
        "python-rapidjson",
        "untwist @ git+https://github.com/jamesb93/untwist.git",
        "python-flucoma",
        "pydub",
        "scipy",
        "rich",
        "librosa",
    ],
)
