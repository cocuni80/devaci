from importlib.metadata import version

import devaci


def test_version():
    assert devaci.__version__ == version("devaci")
