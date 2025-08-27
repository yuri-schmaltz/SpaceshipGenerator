"""Tests for geometry utilities using stubbed Blender modules."""

from spaceship_generator import geometry


class Vert:
    def __init__(self, co):
        self.co = co


class Edge:
    def __init__(self, length):
        self._length = length

    def calc_length(self):
        return self._length


class Face:
    def __init__(self, verts, edges, normal, is_valid=True):
        self.verts = verts
        self.edges = edges
        self.normal = normal
        self.is_valid = is_valid


def test_get_face_matrix_triangle():
    v0 = Vert(geometry.Vector((0, 0, 0)))
    v1 = Vert(geometry.Vector((1, 0, 0)))
    v2 = Vert(geometry.Vector((0, 2, 0)))
    face = Face([v0, v1, v2], [], geometry.Vector((0, 0, 1)))

    mat = geometry.get_face_matrix(face)

    assert mat.translation.x == 0
    assert mat.translation.y == 0
    assert mat.translation.z == 0


def test_get_face_width_and_height_triangle():
    v0 = Vert(geometry.Vector((0, 0, 0)))
    v1 = Vert(geometry.Vector((1, 0, 0)))
    v2 = Vert(geometry.Vector((0, 2, 0)))
    face = Face([v0, v1, v2], [], geometry.Vector((0, 0, 1)))

    width, height = geometry.get_face_width_and_height(face)

    assert width == 1
    assert height == 2


def test_get_aspect_ratio_invalid_face():
    face = Face([], [], geometry.Vector((0, 0, 0)), is_valid=False)

    assert geometry.get_aspect_ratio(face) == 1.0

