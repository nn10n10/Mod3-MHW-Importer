"""Run with blender --background --factory-startup --python-exit-code 1 --python this_file."""
import importlib.util
import sys
from pathlib import Path
import bpy

sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root.parent))
addon = importlib.import_module(root.name)
for _ in range(2):
    addon.register()
    addon.register()
    assert hasattr(bpy.types.Object, "MHW_Symmetric_Pair")
    assert bpy.ops.custom_import.import_mhw_mod3.get_rna_type().properties.get("weight_format")
    assert bpy.ops.custom_export.export_mhw_mod3.get_rna_type().properties.get("export_bounds")
    addon.unregister()
    addon.unregister()
    assert not hasattr(bpy.types.Object, "MHW_Symmetric_Pair")
addon = importlib.reload(addon)
addon.register()
addon.unregister()
print("PASS: registration, RNA properties, unregister, reload", bpy.app.version_string)
