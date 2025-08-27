"""Core spaceship generation routines targeting Blender 2.80+."""

from __future__ import annotations

import datetime
import os
from math import cos, sin, radians
from random import randint, random, seed, uniform

try:  # pragma: no cover - Blender specific
    import bpy  # type: ignore
    import bmesh  # type: ignore
    from mathutils import Matrix, Vector  # type: ignore
except Exception:  # pragma: no cover
    bpy = bmesh = None  # type: ignore
    Matrix = Vector = None  # type: ignore

from .geometry import (
    add_cylinders_to_face,
    add_disc_to_face,
    add_exhaust_to_face,
    add_grid_to_face,
    add_sphere_to_face,
    add_surface_antenna_to_face,
    add_weapons_to_face,
    extrude_face,
    get_aspect_ratio,
    is_rear_face,
    ribbed_extrude_face,
    scale_face,
)
from .materials import Material, create_materials
from .utils import reset_scene


def generate_spaceship(
    random_seed: str = "",
    num_hull_segments_min: int = 3,
    num_hull_segments_max: int = 6,
    create_asymmetry_segments: bool = True,
    num_asymmetry_segments_min: int = 1,
    num_asymmetry_segments_max: int = 5,
    create_face_detail: bool = True,
    allow_horizontal_symmetry: bool = True,
    allow_vertical_symmetry: bool = False,
    apply_bevel_modifier: bool = True,
    assign_materials: bool = True,
):
    """Generate a procedural spaceship mesh and return the object."""

    if random_seed:
        seed(random_seed)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    scale_vector = Vector((uniform(0.75, 2.0), uniform(0.75, 2.0), uniform(0.75, 2.0)))
    bmesh.ops.scale(bm, vec=scale_vector, verts=bm.verts)

    for face in bm.faces[:]:
        if abs(face.normal.x) > 0.5:
            hull_segment_length = uniform(0.3, 1)
            num_hull_segments = randint(num_hull_segments_min, num_hull_segments_max)
            hull_segment_range = range(num_hull_segments)
            for i in hull_segment_range:
                is_last_hull_segment = i == hull_segment_range[-1]
                val = random()
                if val > 0.1:
                    face = extrude_face(bm, face, hull_segment_length)
                    if random() > 0.75:
                        face = extrude_face(bm, face, hull_segment_length * 0.25)

                    if random() > 0.5:
                        sy = uniform(1.2, 1.5)
                        sz = uniform(1.2, 1.5)
                        if is_last_hull_segment or random() > 0.5:
                            sy = 1 / sy
                            sz = 1 / sz
                        scale_face(bm, face, 1, sy, sz)

                    if random() > 0.5:
                        sideways_translation = Vector(
                            (0, 0, uniform(0.1, 0.4) * scale_vector.z * hull_segment_length)
                        )
                        if random() > 0.5:
                            sideways_translation = -sideways_translation
                        bmesh.ops.translate(bm, vec=sideways_translation, verts=face.verts)

                    if random() > 0.5:
                        angle = 5
                        if random() > 0.5:
                            angle = -angle
                        bmesh.ops.rotate(
                            bm,
                            verts=face.verts,
                            cent=(0, 0, 0),
                            matrix=Matrix.Rotation(radians(angle), 3, "Y"),
                        )
                else:
                    rib_scale = uniform(0.75, 0.95)
                    face = ribbed_extrude_face(
                        bm, face, hull_segment_length, randint(2, 4), rib_scale
                    )

    if create_asymmetry_segments:
        for face in bm.faces[:]:
            if get_aspect_ratio(face) > 4:
                continue
            if random() > 0.85:
                hull_piece_length = uniform(0.1, 0.4)
                for _ in range(randint(num_asymmetry_segments_min, num_asymmetry_segments_max)):
                    face = extrude_face(bm, face, hull_piece_length)
                    if random() > 0.25:
                        s = 1 / uniform(1.1, 1.5)
                        scale_face(bm, face, s, s, s)

    if create_face_detail:
        engine_faces = []
        grid_faces = []
        antenna_faces = []
        weapon_faces = []
        sphere_faces = []
        disc_faces = []
        cylinder_faces = []
        for face in bm.faces[:]:
            if get_aspect_ratio(face) > 3:
                continue

            val = random()
            if is_rear_face(face):
                if not engine_faces or val > 0.75:
                    engine_faces.append(face)
                elif val > 0.5:
                    cylinder_faces.append(face)
                elif val > 0.25:
                    grid_faces.append(face)
                else:
                    face.material_index = Material.hull_lights
            elif face.normal.x > 0.9:
                if face.normal.dot(face.calc_center_bounds()) > 0 and val > 0.7:
                    antenna_faces.append(face)
                    face.material_index = Material.hull_lights
                elif val > 0.4:
                    grid_faces.append(face)
                else:
                    face.material_index = Material.hull_lights
            elif face.normal.z > 0.9:
                if face.normal.dot(face.calc_center_bounds()) > 0 and val > 0.7:
                    antenna_faces.append(face)
                    face.material_index = Material.hull_lights
                elif val > 0.6:
                    grid_faces.append(face)
                elif val > 0.3:
                    cylinder_faces.append(face)
            elif face.normal.z < -0.9:
                if val > 0.75:
                    disc_faces.append(face)
                elif val > 0.5:
                    grid_faces.append(face)
                elif val > 0.25:
                    weapon_faces.append(face)
            elif val > 0.9:
                sphere_faces.append(face)
            elif val > 0.6:
                grid_faces.append(face)
            elif val > 0.3:
                cylinder_faces.append(face)

        for face in engine_faces:
            add_exhaust_to_face(bm, face)
        for face in grid_faces:
            add_grid_to_face(bm, face)
        for face in antenna_faces:
            add_surface_antenna_to_face(bm, face)
        for face in weapon_faces:
            add_weapons_to_face(bm, face)
        for face in sphere_faces:
            add_sphere_to_face(bm, face)
        for face in disc_faces:
            face.material_index = Material.glow_disc
            add_disc_to_face(bm, face)
        for face in cylinder_faces:
            add_cylinders_to_face(bm, face)

    mesh = bpy.data.meshes.new("Spaceship")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Spaceship", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    if allow_horizontal_symmetry or allow_vertical_symmetry:
        mod = obj.modifiers.new("Mirror", type="MIRROR")
        mod.use_axis[0] = allow_horizontal_symmetry
        mod.use_axis[1] = allow_vertical_symmetry

    if apply_bevel_modifier:
        mod = obj.modifiers.new("Bevel", type="BEVEL")
        mod.width = 0.02
        mod.segments = 2

    if assign_materials:
        for mat in create_materials():
            obj.data.materials.append(mat)

    bpy.ops.object.shade_smooth()
    return obj


def generate_movie(
    random_seed: str = "",
    output_path: str = "",
    fps: int = 24,
    total_movie_duration: float = 10.0,
    total_spaceship_duration: float = 5.0,
    inv_fps: float = 1.0 / 24.0,
    camera_pole_length: float = 10.0,
    camera_pole_pitch_min: float = 5.0,
    camera_pole_pitch_max: float = 50.0,
    camera_pole_pitch_offset: float = 0.0,
    camera_pole_rate: float = 2.0,
    yaw_rate: float = 45.0,
    yaw_offset: float = 0.0,
    fov: float = 50.0,
    camera_refocus_object_every_frame: bool = True,
):  # pragma: no cover - Blender specific
    """Generate a flickering fly-by video by repeatedly generating ships."""

    scene = bpy.context.scene
    render = scene.render
    render.resolution_x = 1920
    render.resolution_y = 1080
    render.image_settings.file_format = "PNG"

    if random_seed:
        seed(random_seed)

    movie_duration = 0
    spaceship_duration = total_spaceship_duration

    if "Camera" not in bpy.data.objects:
        bpy.ops.object.camera_add(location=(0, -camera_pole_length, camera_pole_length))
    scene.camera = bpy.data.objects["Camera"]
    scene.camera.rotation_mode = "XYZ"
    scene.camera.data.angle = radians(fov)
    frame = 0
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    while movie_duration < total_movie_duration:
        movie_duration += inv_fps
        spaceship_duration += inv_fps
        if spaceship_duration >= total_spaceship_duration:
            spaceship_duration -= total_spaceship_duration

            reset_scene()
            obj = generate_spaceship()

            lowest_z = min((Vector(b).z for b in obj.bound_box))
            plane_obj = bpy.data.objects["Plane"] if "Plane" in bpy.data.objects else None
            if plane_obj:
                plane_obj.location.z = lowest_z - 0.3

        rad = radians(yaw_offset + (yaw_rate * movie_duration))
        camera_pole_pitch_lerp = 0.5 * (1 + cos(camera_pole_rate * movie_duration))
        camera_pole_pitch = camera_pole_pitch_max * camera_pole_pitch_lerp + \
            camera_pole_pitch_min * (1 - camera_pole_pitch_lerp)
        scene.camera.rotation_euler = (
            radians(90 - camera_pole_pitch + camera_pole_pitch_offset),
            0,
            rad,
        )
        scene.camera.location = (
            sin(rad) * camera_pole_length,
            cos(rad) * -camera_pole_length,
            sin(radians(camera_pole_pitch)) * camera_pole_length,
        )
        if camera_refocus_object_every_frame:
            bpy.ops.view3d.camera_to_view_selected()

        script_path = bpy.context.space_data.text.filepath if bpy.context.space_data else __file__
        folder = output_path if output_path else os.path.split(os.path.realpath(script_path))[0]
        filename = os.path.join("renders", timestamp, timestamp + "_" + str(frame).zfill(5) + ".png")
        bpy.data.scenes["Scene"].render.filepath = os.path.join(folder, filename)
        print("Rendering frame " + str(frame) + "...")
        bpy.ops.render.render(write_still=True)
        frame += 1

