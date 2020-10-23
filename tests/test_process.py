from ftis.world import World
import os

this_test_script = os.path.dirname(os.path.abspath(__file__))
test_yaml = os.path.join(this_test_script, "cfgtest.yaml")


def test_instantiation():
    test = World(test_yaml)
    assert test.config_path == test_yaml
