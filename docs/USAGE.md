# Spaceship Generator Usage

This add-on exposes a small Python API. Once the add-on is installed in
Blender, a spaceship can be created programmatically:

```python
import spaceship_generator

# Generate a ship using a fixed seed so results are repeatable
spaceship_generator.generate_spaceship(random_seed="42")
```

The resulting mesh is linked into the current scene and materials are
optionally assigned. See the function docstring for a full list of
parameters controlling the generation process.

