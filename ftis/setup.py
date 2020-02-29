import setuptools

setuptools.setup(
    name="ftis",
    version="1.0",
    author="James Bradbury",
    author_email="jamesbradbury93@gmail.com",
    description="The finding things in stuff package.",
    packages=["ftis"],
    install_requires=[
        "PyYAML",
        "python-rapidjson",
        "SoundFile",
        "simpleaudio",
        "sklearn",
        "hdbscan",
        "numpy",
        "scikit-learn",
        "scipy",
        "umap-learn",
        "pydub",
    ],
)
