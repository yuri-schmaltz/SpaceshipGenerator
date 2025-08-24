"""Utility helpers for the Spaceship Generator add-on.

These functions are kept lightweight so they can be imported in
environments where Blender's Python API (``bpy``) is unavailable.
"""

from __future__ import annotations

import os

try:  # pragma: no cover - Blender specific
    import bpy  # type: ignore
except Exception:  # pragma: no cover - Blender not available
    bpy = None  # type: ignore

DIR = os.path.dirname(os.path.abspath(__file__))


def resource_path(*path_components: str) -> str:
    """Return an absolute path to a resource inside the add-on package."""

    return os.path.join(DIR, *path_components)


def reset_scene() -> None:
    """Remove generated ships and unused materials from the scene.

    When running outside Blender (``bpy`` is ``None``) the function is a no-op
    so that unit tests can import the module without requiring Blender.
    """

    if bpy is None:  # pragma: no cover - Blender specific
        return

    for item in bpy.data.objects:
        item.select_set(item.name.startswith("Spaceship"))
    bpy.ops.object.delete()

    for material in list(bpy.data.materials):
        if not material.users:
            bpy.data.materials.remove(material)

    for texture in list(bpy.data.textures):
        if not texture.users:
            bpy.data.textures.remove(texture)

