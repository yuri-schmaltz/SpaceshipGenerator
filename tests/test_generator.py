"""Tests for generator utilities that do not require Blender."""

import inspect


def test_no_randrange_usage():
    import spaceship_generator.generator as generator

    source = inspect.getsource(generator)
    assert "randrange" not in source

