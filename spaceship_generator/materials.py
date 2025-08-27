"""Material helpers for the Spaceship Generator."""

from __future__ import annotations

from colorsys import hls_to_rgb
from enum import IntEnum
from random import random, uniform

try:  # pragma: no cover - Blender specific
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None  # type: ignore

from .utils import resource_path


class Material(IntEnum):
    """Enumeration of material slots used by the generator."""

    hull = 0
    hull_lights = 1
    hull_dark = 2
    exhaust_burn = 3
    glow_disc = 4


def get_shader_node(mat):  # pragma: no cover - Blender specific
    ntree = mat.node_tree
    node_out = ntree.get_output_node("EEVEE")
    shader_node = node_out.inputs["Surface"].links[0].from_node
    return shader_node


def get_shader_input(mat, name):  # pragma: no cover - Blender specific
    shader_node = get_shader_node(mat)
    return shader_node.inputs[name]


def add_hull_normal_map(mat, hull_normal_map):  # pragma: no cover - Blender specific
    ntree = mat.node_tree
    shader = get_shader_node(mat)
    links = ntree.links

    teximage_node = ntree.nodes.new("ShaderNodeTexImage")
    teximage_node.image = hull_normal_map
    teximage_node.image.colorspace_settings.name = "Raw"
    teximage_node.projection = "BOX"
    tex_coords_node = ntree.nodes.new("ShaderNodeTexCoord")
    links.new(tex_coords_node.outputs["Object"], teximage_node.inputs["Vector"])
    normalMap_node = ntree.nodes.new("ShaderNodeNormalMap")
    links.new(teximage_node.outputs[0], normalMap_node.inputs["Color"])
    links.new(normalMap_node.outputs["Normal"], shader.inputs["Normal"])
    return tex_coords_node


def set_hull_mat_basics(mat, color, hull_normal_map):  # pragma: no cover - Blender specific
    shader_node = get_shader_node(mat)
    shader_node.inputs["Specular"].default_value = 0.1
    shader_node.inputs["Base Color"].default_value = color

    return add_hull_normal_map(mat, hull_normal_map)


def create_materials():  # pragma: no cover - Blender specific
    ret = []

    for material in Material:
        mat = bpy.data.materials.new(name=material.name)
        mat.use_nodes = True
        ret.append(mat)

    hull_base_color = hls_to_rgb(random(), uniform(0.05, 0.5), uniform(0, 0.25))
    hull_base_color = (
        hull_base_color[0],
        hull_base_color[1],
        hull_base_color[2],
        1.0,
    )

    hull_normal_map = bpy.data.images.load(
        resource_path("textures", "hull_normal.png"), check_existing=True
    )

    mat = ret[Material.hull]
    set_hull_mat_basics(mat, hull_base_color, hull_normal_map)

    mat = ret[Material.hull_lights]
    coords_node = set_hull_mat_basics(mat, hull_base_color, hull_normal_map)
    hull_lights_diffuse = bpy.data.images.load(
        resource_path("textures", "hull_lights_diffuse.png"), check_existing=True
    )
    hull_lights_emit = bpy.data.images.load(
        resource_path("textures", "hull_lights_emit.png"), check_existing=True
    )
    ntree = mat.node_tree
    shader = get_shader_node(mat)
    links = ntree.links
    teximage_node = ntree.nodes.new("ShaderNodeTexImage")
    teximage_node.image = hull_lights_diffuse
    teximage_node.image.colorspace_settings.name = "sRGB"
    teximage_node.projection = "BOX"
    links.new(coords_node.outputs["Object"], teximage_node.inputs["Vector"])
    links.new(teximage_node.outputs[0], shader.inputs["Base Color"])
    teximage_node = ntree.nodes.new("ShaderNodeTexImage")
    teximage_node.image = hull_lights_emit
    teximage_node.image.colorspace_settings.name = "sRGB"
    teximage_node.projection = "BOX"
    links.new(coords_node.outputs["Object"], teximage_node.inputs["Vector"])
    links.new(teximage_node.outputs[0], shader.inputs["Emission"])
    shader.inputs["Emission Strength"].default_value = 5

    mat = ret[Material.hull_dark]
    set_hull_mat_basics(
        mat,
        (hull_base_color[0] * 0.1, hull_base_color[1] * 0.1, hull_base_color[2] * 0.1, 1.0),
        hull_normal_map,
    )

    mat = ret[Material.exhaust_burn]
    shader_node = get_shader_node(mat)
    shader_node.inputs["Emission"].default_value = (1.0, 0.6, 0.2, 1.0)
    shader_node.inputs["Emission Strength"].default_value = 10
    shader_node.inputs["Roughness"].default_value = 0.5

    mat = ret[Material.glow_disc]
    shader_node = get_shader_node(mat)
    shader_node.inputs["Emission"].default_value = (0.8, 0.8, 1.0, 1.0)
    shader_node.inputs["Emission Strength"].default_value = 10

    return ret

