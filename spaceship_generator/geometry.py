"""Geometry utilities for constructing spaceship meshes."""

from __future__ import annotations

from math import cos, pi, radians, sin, sqrt
from random import randint, random, uniform

try:  # pragma: no cover - Blender specific
    import bmesh  # type: ignore
    from mathutils import Matrix, Vector  # type: ignore
except Exception:  # pragma: no cover
    bmesh = None  # type: ignore
    Matrix = Vector = None  # type: ignore

from .materials import Material


def extrude_face(bm, face, translate_forwards: float = 0.0, extruded_face_list=None):
    """Extrude ``face`` along its normal and return the new face."""

    new_faces = bmesh.ops.extrude_discrete_faces(bm, faces=[face])["faces"]
    if extruded_face_list is not None:
        extruded_face_list += new_faces[:]
    new_face = new_faces[0]
    bmesh.ops.translate(
        bm, vec=new_face.normal * translate_forwards, verts=new_face.verts
    )
    return new_face


def ribbed_extrude_face(bm, face, translate_forwards, num_ribs: int = 3, rib_scale: float = 0.9):
    """Extrude a face creating evenly spaced ribs."""

    translate_forwards_per_rib = translate_forwards / float(num_ribs)
    new_face = face
    for _ in range(num_ribs):
        new_face = extrude_face(bm, new_face, translate_forwards_per_rib * 0.25)
        new_face = extrude_face(bm, new_face, 0.0)
        scale_face(bm, new_face, rib_scale, rib_scale, rib_scale)
        new_face = extrude_face(bm, new_face, translate_forwards_per_rib * 0.5)
        new_face = extrude_face(bm, new_face, 0.0)
        scale_face(bm, new_face, 1 / rib_scale, 1 / rib_scale, 1 / rib_scale)
        new_face = extrude_face(bm, new_face, translate_forwards_per_rib * 0.25)
    return new_face


def scale_face(bm, face, scale_x: float, scale_y: float, scale_z: float):
    """Scale a face in local space."""

    face_space = get_face_matrix(face)
    face_space.invert()
    bmesh.ops.scale(
        bm,
        vec=Vector((scale_x, scale_y, scale_z)),
        space=face_space,
        verts=face.verts,
    )


def get_face_matrix(face, pos=None):
    """Return an approximate transform matrix for ``face``."""

    x_axis = (face.verts[1].co - face.verts[0].co).normalized()
    y_axis = (face.verts[3].co - face.verts[0].co).normalized()
    normal = x_axis.cross(y_axis)
    if pos is None:
        pos = face.verts[0].co
    mat = Matrix((x_axis, y_axis, normal)).to_4x4()
    mat.translation = pos
    return mat


def get_face_width_and_height(face):
    width = (face.verts[1].co - face.verts[0].co).length
    height = (face.verts[3].co - face.verts[0].co).length
    return width, height


def get_aspect_ratio(face) -> float:
    if not face.is_valid:
        return 1.0
    face_aspect_ratio = max(0.01, face.edges[0].calc_length() / face.edges[1].calc_length())
    if face_aspect_ratio < 1.0:
        face_aspect_ratio = 1.0 / face_aspect_ratio
    return face_aspect_ratio


def is_rear_face(face) -> bool:
    return face.normal.x < -0.95


def add_exhaust_to_face(bm, face):
    if not face.is_valid:
        return

    num_cuts = randint(1, int(4 - get_aspect_ratio(face)))
    result = bmesh.ops.subdivide_edges(
        bm, edges=face.edges[:], cuts=num_cuts, fractal=0.02, use_grid_fill=True
    )

    exhaust_length = uniform(0.1, 0.2)
    scale_outer = 1 / uniform(1.3, 1.6)
    scale_inner = 1 / uniform(1.05, 1.1)
    for face in result["geom"]:
        if isinstance(face, bmesh.types.BMFace):
            if is_rear_face(face):
                face.material_index = Material.hull_dark
                face = extrude_face(bm, face, exhaust_length)
                scale_face(bm, face, scale_outer, scale_outer, scale_outer)
                extruded_face_list = []
                face = extrude_face(bm, face, -exhaust_length * 0.9, extruded_face_list)
                for extruded_face in extruded_face_list:
                    extruded_face.material_index = Material.exhaust_burn
                scale_face(bm, face, scale_inner, scale_inner, scale_inner)


def add_grid_to_face(bm, face):
    if not face.is_valid:
        return

    result = bmesh.ops.subdivide_edges(
        bm,
        edges=face.edges[:],
        cuts=randint(2, 4),
        fractal=0.02,
        use_grid_fill=True,
        use_single_edge=False,
    )
    grid_length = uniform(0.025, 0.15)
    scale = 0.8
    for face in result["geom"]:
        if isinstance(face, bmesh.types.BMFace):
            material_index = Material.hull_lights if random() > 0.5 else Material.hull
            extruded_face_list = []
            face = extrude_face(bm, face, grid_length, extruded_face_list)
            for extruded_face in extruded_face_list:
                if abs(face.normal.z) < 0.707:
                    extruded_face.material_index = material_index
            scale_face(bm, face, scale, scale, scale)


def add_cylinders_to_face(bm, face):
    if not face.is_valid or len(face.verts[:]) < 4:
        return

    horizontal_step = randint(1, 3)
    vertical_step = randint(1, 3)
    num_segments = randint(6, 12)
    face_width, face_height = get_face_width_and_height(face)
    cylinder_depth = 1.3 * min(
        face_width / (horizontal_step + 2), face_height / (vertical_step + 2)
    )
    cylinder_size = cylinder_depth * 0.5
    for h in range(horizontal_step):
        top = face.verts[0].co.lerp(
            face.verts[1].co, (h + 1) / float(horizontal_step + 1)
        )
        bottom = face.verts[3].co.lerp(
            face.verts[2].co, (h + 1) / float(horizontal_step + 1)
        )
        for v in range(vertical_step):
            pos = top.lerp(bottom, (v + 1) / float(vertical_step + 1))
            cylinder_matrix = get_face_matrix(face, pos) @ Matrix.Rotation(radians(90), 3, "X").to_4x4()
            bmesh.ops.create_cone(
                bm,
                cap_ends=True,
                cap_tris=False,
                segments=num_segments,
                diameter1=cylinder_size,
                diameter2=cylinder_size,
                depth=cylinder_depth,
                matrix=cylinder_matrix,
            )


def add_weapons_to_face(bm, face):
    if not face.is_valid or len(face.verts[:]) < 4:
        return

    horizontal_step = randint(1, 2)
    vertical_step = randint(1, 2)
    num_segments = 16
    face_width, face_height = get_face_width_and_height(face)
    weapon_size = 0.5 * min(
        face_width / (horizontal_step + 2), face_height / (vertical_step + 2)
    )
    weapon_depth = weapon_size * 0.2
    for h in range(horizontal_step):
        top = face.verts[0].co.lerp(
            face.verts[1].co, (h + 1) / float(horizontal_step + 1)
        )
        bottom = face.verts[3].co.lerp(
            face.verts[2].co, (h + 1) / float(horizontal_step + 1)
        )
        for v in range(vertical_step):
            pos = top.lerp(bottom, (v + 1) / float(vertical_step + 1))
            base_matrix = get_face_matrix(face, pos)
            turret_base = bmesh.ops.create_cone(
                bm,
                cap_ends=True,
                cap_tris=False,
                segments=num_segments,
                diameter1=weapon_size,
                diameter2=weapon_size,
                depth=weapon_depth,
                matrix=base_matrix,
            )["verts"]

            barrel_matrix = base_matrix @ Matrix.Translation(
                (0, 0, weapon_depth * 0.5)
            ) @ Matrix.Rotation(radians(randint(-45, 45)), 3, "Z").to_4x4()
            bmesh.ops.create_cone(
                bm,
                cap_ends=True,
                cap_tris=False,
                segments=num_segments,
                diameter1=weapon_size * 0.25,
                diameter2=weapon_size * 0.25,
                depth=weapon_size,
                matrix=barrel_matrix,
            )


def add_sphere_to_face(bm, face):
    if not face.is_valid or len(face.verts[:]) < 4:
        return

    face_width, face_height = get_face_width_and_height(face)
    size = min(face_width, face_height)
    matrix = get_face_matrix(face) @ Matrix.Translation((0, 0, size * 0.5))
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=8, diameter=size, matrix=matrix)


def add_surface_antenna_to_face(bm, face):
    if not face.is_valid or len(face.verts[:]) < 4:
        return

    face_width, face_height = get_face_width_and_height(face)
    size = min(face_width, face_height)
    matrix = get_face_matrix(face) @ Matrix.Translation((0, 0, size * 0.5))
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=8,
        diameter1=size * 0.5,
        diameter2=0,
        depth=size,
        matrix=matrix,
    )


def add_disc_to_face(bm, face):
    if not face.is_valid or len(face.verts[:]) < 4:
        return

    face_width, face_height = get_face_width_and_height(face)
    size = min(face_width, face_height)
    matrix = get_face_matrix(face)
    bmesh.ops.create_circle(
        bm,
        cap_ends=False,
        cap_tris=False,
        segments=32,
        radius=size * 0.5,
        matrix=matrix,
    )

