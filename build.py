#!/usr/bin/env python
"""Build the add-on using setuptools.

This script is a thin wrapper around ``python -m build`` to produce a
wheel and source distribution for the add-on.
"""

import subprocess
import sys


def main() -> int:
    return subprocess.call([sys.executable, "-m", "build"])


if __name__ == "__main__":  # pragma: no cover - script entry point
    raise SystemExit(main())

