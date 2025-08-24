"""Test helpers to stub Blender modules."""

import sys
import types


def _stub(name: str) -> types.ModuleType:
    return types.ModuleType(name)


if "bpy" not in sys.modules:
    bpy = _stub("bpy")
    bpy.props = _stub("bpy.props")
    bpy.props.StringProperty = lambda *a, **k: None
    bpy.props.BoolProperty = lambda *a, **k: None
    bpy.props.IntProperty = lambda *a, **k: None
    bpy.types = _stub("bpy.types")
    bpy.types.Operator = object  # type: ignore
    bpy.__path__ = []  # mark as package
    sys.modules["bpy"] = bpy
    sys.modules["bpy.types"] = bpy.types

if "bmesh" not in sys.modules:
    sys.modules["bmesh"] = _stub("bmesh")

if "mathutils" not in sys.modules:
    mathutils = _stub("mathutils")
    mathutils.Vector = object  # type: ignore
    mathutils.Matrix = object  # type: ignore
    sys.modules["mathutils"] = mathutils

