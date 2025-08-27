"""Test fixtures for stubbing Blender modules."""

import sys
import types
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))


def _stub(name: str) -> types.ModuleType:
    return types.ModuleType(name)


stub_bpy = _stub("bpy")
stub_bpy.props = _stub("bpy.props")
stub_bpy.props.StringProperty = lambda *a, **k: None
stub_bpy.props.BoolProperty = lambda *a, **k: None
stub_bpy.props.IntProperty = lambda *a, **k: None
sys.modules.setdefault("bpy", stub_bpy)
sys.modules.setdefault("bmesh", _stub("bmesh"))


class Vector:
    def __init__(self, coords):
        self.x, self.y, self.z = coords

    def __sub__(self, other):
        return Vector((self.x - other.x, self.y - other.y, self.z - other.z))

    def normalized(self):
        length = (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
        if length == 0:
            return Vector((0, 0, 0))
        return Vector((self.x / length, self.y / length, self.z / length))

    def cross(self, other):
        return Vector(
            (
                self.y * other.z - self.z * other.y,
                self.z * other.x - self.x * other.z,
                self.x * other.y - self.y * other.x,
            )
        )

    @property
    def length(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    def lerp(self, other, t):
        return Vector(
            (
                self.x + (other.x - self.x) * t,
                self.y + (other.y - self.y) * t,
                self.z + (other.z - self.z) * t,
            )
        )

    def __iter__(self):
        return iter((self.x, self.y, self.z))


class Matrix:
    def __init__(self, rows):
        self.rows = rows
        self.translation = Vector((0, 0, 0))

    def to_4x4(self):
        return self

    @staticmethod
    def Rotation(angle, size, axis):  # pragma: no cover - used in stubs
        return Matrix.identity()

    @staticmethod
    def Translation(t):  # pragma: no cover - used in stubs
        m = Matrix.identity()
        m.translation = Vector(t)
        return m

    @staticmethod
    def identity():  # pragma: no cover - used in stubs
        return Matrix([Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))])

    def __matmul__(self, other):  # pragma: no cover - used in stubs
        return self


mathutils = _stub("mathutils")
mathutils.Vector = Vector
mathutils.Matrix = Matrix
sys.modules.setdefault("mathutils", mathutils)

