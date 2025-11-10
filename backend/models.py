"""
Compatibility shim for imports that expect a `models` package.

This module ensures imports like `from models.ganstego import ...` work even
though there's both a file `models.py` and a folder `models/` in the backend.

It also re-exports the SQLAlchemy models from `db_models` for backward
compatibility (e.g., `from models import User`).
"""
import importlib.util
import os
import sys

# Load the ganstego submodule from the models directory and register it as
# `models.ganstego` so `from models.ganstego import AdvancedGenerator` works.
try:
    ganstego_path = os.path.join(os.path.dirname(__file__), 'models', 'ganstego.py')
    if os.path.exists(ganstego_path):
        spec = importlib.util.spec_from_file_location('models.ganstego', ganstego_path)
        ganstego = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(ganstego)
        sys.modules['models.ganstego'] = ganstego
        # Also expose as attribute on this module
        globals()['ganstego'] = ganstego
except Exception:
    # If loading fails, leave it; imports will raise when used.
    pass

# Re-export everything from db_models
from db_models import *  # noqa: F401,F403
