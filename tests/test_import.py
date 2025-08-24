"""Basic import tests for the package.

These tests stub out Blender-specific modules so the package can be
imported in a normal Python environment.
"""

import sys
import types

import pytest


def _stub(name: str) -> types.ModuleType:
    module = types.ModuleType(name)
    return module


stub_bpy = _stub("bpy")
stub_bpy.props = _stub("bpy.props")
stub_bpy.props.StringProperty = lambda *a, **k: None
stub_bpy.props.BoolProperty = lambda *a, **k: None
stub_bpy.props.IntProperty = lambda *a, **k: None
sys.modules.setdefault("bpy", stub_bpy)
sys.modules.setdefault("bmesh", _stub("bmesh"))
mathutils = _stub("mathutils")
mathutils.Vector = object  # type: ignore
mathutils.Matrix = object  # type: ignore
sys.modules.setdefault("mathutils", mathutils)


def test_generate_spaceship_available():
    import importlib

    spaceship_generator = importlib.import_module(
        "SpaceshipGenerator.spaceship_generator"
    )

    assert callable(spaceship_generator.generate_spaceship)

