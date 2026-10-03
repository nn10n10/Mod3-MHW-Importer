"""Run the deterministic Blender round-trip suite; pass -- --output DIRECTORY."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "tests" / "blender_roundtrip.py"), run_name="__main__")
