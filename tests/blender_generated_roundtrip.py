"""Keep testing actual reconstruction separately from opaque source replay.

These scenes are created from synthetic fixture objects with explicitly known
ownership, not inferred from a parsed mesh header byte. No guard is bypassed.
"""
import importlib
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import bpy

sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root.parent))
sys.path.insert(0, str(root / 'tests'))
from fixtures import fixture, parse, Mod3Vertex

addon = importlib.import_module(root.name)
addon.register()
api = importlib.import_module(root.name + '.blender.BlenderMod3Importer').BlenderImporterAPI
cases = [(block, 0) for block in Mod3Vertex.blocklist] + [(0xf637401c, 2), (0x81f58067, 2)]
with tempfile.TemporaryDirectory() as directory:
    for block, flags in cases:
        model = fixture(block, weight_bits=flags)
        # Match the on-disk fixed-width material names used by normal imports.
        for material in model.Materials:
            material.materialName = material.materialName.ljust(128, '\0')
        source = bytearray(model.serialize())
        context = SimpleNamespace(path='generated.mod3', meshes=[], armature=None)
        api.clearScene(context)
        api.setScene(model.sceneProperties(), context)
        api.createEmptyTree(model.prepareArmature(), context)
        api.createMeshParts(model.prepareMeshparts(2), False, context)
        context.boundingBoxes = [model.boundingBoxes()]  # fixture explicitly owns its one box
        api.loadBoundingBoxes(model.boundingBoxes(), context)
        destination = Path(directory) / 'generated.mod3'
        assert bpy.ops.custom_export.export_mhw_mod3(filepath=str(destination),
                    coerce_fourth=False, export_bounds='Explicit') == {'FINISHED'}
        output = bytearray(destination.read_bytes())
        # The normal exporter refreshes creationDate, unlike opaque replay.
        source[40:48] = output[40:48] = bytes(8)
        assert source == output, 'Reconstruction changed synthetic data: %08x flags %d; differences %s lengths %s' % (block, flags, [(i,a,b) for i,(a,b) in enumerate(zip(source,output)) if a!=b][:20],(len(source),len(output)))
        assert parse(destination.read_bytes()).MeshParts.BoundingBoxes.count == 1
addon.unregister()
print('PASS: 16 synthetic generated exports are byte-identical except creationDate')
