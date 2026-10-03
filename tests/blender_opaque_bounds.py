"""Real Blender export guards and save/close/reopen; synthetic assets only.

blender -b --factory-startup --python-exit-code 1 --python this.py -- --output DIR
"""
import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

import bpy

sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root.parent))
sys.path.insert(0, str(root / 'tests'))
from fixtures import opaque_fixture

addon = importlib.import_module(root.name)
addon.register()
opaque = importlib.import_module(root.name + '.blender.BlenderOpaqueBounds')
args = argparse.ArgumentParser()
args.add_argument('--output', required=True)
args.add_argument('--reopen', action='store_true')
args.add_argument('--reopen-sample', help='Optional private MOD3 for a real-file save/reopen check')
opts = args.parse_args(sys.argv[sys.argv.index('--') + 1:])
out = Path(opts.output).resolve()
out.mkdir(parents=True, exist_ok=True)
source = out / 'opaque-source.mod3'
destination = out / 'opaque-output.mod3'
results = []


def load(**options):
    settings = dict(clear_scene=True, high_lod=False, import_header=False,
                    import_textures=False, import_materials=False, weight_format='Slash',
                    load_group_functions=False, maximize_clipping=False)
    settings.update(options)
    assert bpy.ops.custom_import.import_mhw_mod3(filepath=str(source), **settings) == {'FINISHED'}


def unchanged():
    assert bpy.ops.custom_export.export_mhw_mod3(filepath=str(destination)) == {'FINISHED'}
    assert destination.read_bytes() == source.read_bytes()


def refused(label):
    destination.write_bytes(b'KEEP EXISTING DESTINATION')
    try:
        status = bpy.ops.custom_export.export_mhw_mod3(filepath=str(destination))
    except RuntimeError:
        status = {'CANCELLED'}  # ERROR reports raise through bpy.ops
    assert status == {'CANCELLED'}, label
    assert destination.read_bytes() == b'KEEP EXISTING DESTINATION', label
    assert not list(out.glob('.mod3-*')), label
    results.append(label)


if opts.reopen:
    opaque._baselines.clear()  # baseline must work without process-local cache
    unchanged()
    results.append('save_close_reopen_exact_replay')
    mesh = next(obj for obj in bpy.context.scene.objects if obj.type == 'MESH')
    mesh.data.vertices[0].co.x += 0.125
    refused('reopened_geometry_edit')
else:
    for fields, count in [((0, 0), 23), ((0, 60), 23), ((12,), 195)]:
        source.write_bytes(opaque_fixture(fields, count))
        load(omit_empty=True)
        assert len([o for o in bpy.context.scene.objects if o.type == 'MESH']) == len(fields)
        assert all(o.vertex_groups for o in bpy.context.scene.objects if o.type == 'MESH')
        unchanged()
        results.append('raw_preservation_%s_%d' % (fields, count))
    source.write_bytes(opaque_fixture())
    mutations = {
        'positions': lambda m: setattr(m.data.vertices[0].co, 'x', 0.125),
        'topology': lambda m: m.data.clear_geometry(),
        'weights': lambda m: m.vertex_groups[0].add([0], 0.5, 'REPLACE'),
        'mesh_order': lambda m: setattr(m.data, 'name', 'zz-reordered'),
        'lod': lambda m: m.data.__setitem__('lod', 123),
        'transform': lambda m: setattr(m.location, 'x', 1),
        'modifier': lambda m: m.modifiers.new('new', 'SUBSURF'),
        'uv': lambda m: setattr(m.data.uv_layers[0].data[0], 'uv', (0.2, 0.3)),
        'normals': lambda m: m.data.normals_split_custom_set([(1, 0, 0)] * len(m.data.loops)),
        'bone_hierarchy': lambda m: setattr(next(o for o in bpy.context.scene.objects if o.get('indexHint') == 1), 'parent', None),
        'bone_rest_transform': lambda m: setattr(next(o for o in bpy.context.scene.objects if o.get('indexHint') == 1).location, 'x', 1),
        'bone_index': lambda m: next(o for o in bpy.context.scene.objects if o.get('indexHint') == 1).__setitem__('indexHint', 7),
        'unknown_mesh_property': lambda m: m.data.__setitem__('intUnknown', 456),
        'mesh_identity': lambda m: m.__setitem__(opaque.IDENTITY, 'replacement'),
        'mesh_count': lambda m: [collection.objects.unlink(m) for collection in tuple(m.users_collection)],
        'vertex_colors': lambda m: m.data.color_attributes.new(name='edited', type='BYTE_COLOR', domain='CORNER'),
        'instancing': lambda m: setattr(next(o for o in bpy.context.scene.objects if o.type=='EMPTY'), 'instance_type', 'COLLECTION'),
    }
    for label, mutate in mutations.items():
        load()
        mesh = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
        mutate(mesh)
        refused(label)
    load()
    text = bpy.data.texts[bpy.context.scene[opaque.LINK]]
    text.write('tampered')
    refused('tampered_baseline')
    load()
    del bpy.context.scene[opaque.LINK]
    refused('missing_baseline_link')
    load(high_lod=True)
    refused('filtered_import')
    load(weight_format='Group')
    refused('lossy_weight_import')
    load(import_skeleton='None')
    refused('missing_skeleton')
    load()
    mesh = next(o for o in bpy.context.scene.objects if o.type=='MESH')
    mesh.shape_key_add(name='unsupported')
    opaque.capture(source.read_bytes(), type('Context', (), {'meshes':[mesh]})(), True)
    packed = bpy.data.texts[bpy.context.scene[opaque.LINK]].as_string()
    payload = json.loads(opaque.zlib.decompress(opaque.base64.b64decode(packed)))
    assert opaque.base64.b64decode(payload['source'])==source.read_bytes()
    assert payload['complete'] is False and payload['blocked_reason']
    refused('unverifiable_snapshot_still_preserves_source')
    load()
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'opaque.blend'))
    # Separate process genuinely closes/reopens the serialized .blend baseline.
    child = subprocess.run([bpy.app.binary_path, '--background', str(out / 'opaque.blend'),
                            '--python-exit-code', '1', '--python', str(Path(__file__).resolve()),
                            '--', '--output', str(out), '--reopen'],
                           capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
    (out / 'reopen.log').write_text(child.stdout + child.stderr, encoding='utf-8')
    assert child.returncode == 0, child.stdout + child.stderr
    results.append('save_close_reopen_child_PASS')
    load(import_skeleton='Armature')
    unchanged()
    armature = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
    armature.pose.bones[0].location.x = 0.25
    refused('armature_pose_edit')
    load(import_skeleton='Armature')
    armature = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    armature.data.edit_bones[0].tail.x += 0.25
    bpy.ops.object.mode_set(mode='OBJECT')
    refused('armature_rest_edit')
    if opts.reopen_sample:
        original = Path(opts.reopen_sample)
        original_bytes = original.read_bytes()
        private = out / 'real-reopen'
        private.mkdir(exist_ok=True)
        source = private / 'opaque-source.mod3'
        source.write_bytes(original_bytes)
        load()
        unchanged()
        bpy.ops.wm.save_as_mainfile(filepath=str(private / 'opaque.blend'))
        child = subprocess.run([bpy.app.binary_path, '--background', str(private / 'opaque.blend'),
                                '--python-exit-code', '1', '--python', str(Path(__file__).resolve()),
                                '--', '--output', str(private), '--reopen'],
                               capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        (private / 'reopen.log').write_text(child.stdout + child.stderr, encoding='utf-8')
        assert child.returncode == 0, child.stdout + child.stderr
        assert original.read_bytes() == original_bytes
        results.append('real_file_save_close_reopen_child_PASS')

(out / ('reopen-results.json' if opts.reopen else 'results.json')).write_text(
    json.dumps({'blender': bpy.app.version_string, 'python': sys.version, 'passed': results}, indent=2), encoding='utf-8')
addon.unregister()
print('PASS opaque bbox guards:', results)
