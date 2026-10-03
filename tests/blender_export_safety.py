import sys,importlib,tempfile
from pathlib import Path
from types import SimpleNamespace
import bpy
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root.parent));sys.path.insert(0,str(root/'tests'));sys.dont_write_bytecode=True
from fixtures import fixture
addon=importlib.import_module(root.name);addon.register()
api=importlib.import_module(root.name+".blender.BlenderMod3Exporter")
with tempfile.TemporaryDirectory() as directory:
    source=Path(directory)/'source.mod3';source.write_bytes(fixture().serialize())
    bpy.ops.custom_import.import_mhw_mod3(filepath=str(source),clear_scene=True,import_textures=False,load_group_functions=True,weight_format='Slash')
    mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH')
    destination=Path(directory)/'out.mod3';destination.write_bytes(b'KEEP')
    mesh.modifiers.new(name='unsupported',type='SUBSURF')
    try:bpy.ops.custom_export.export_mhw_mod3(filepath=str(destination))
    except RuntimeError:pass
    assert destination.read_bytes()==b'KEEP'
    mesh.modifiers.clear()
    original=mesh.data; mesh.location.x=5; bpy.context.view_layer.update()
    with api.MeshClone(mesh) as clone:
        assert abs(clone.data.vertices[0].co.x-5)<1e-6
        assert original.vertices[0].co.x==0
    assert mesh.data==original and mesh.location.x==5
    # Corner conflicts must abort independently of user warning preferences.
    conflict=bpy.data.meshes.new('seam');conflict.from_pydata([(0,0,0),(1,0,0),(0,1,0),(1,1,0)],[],[(0,1,2),(1,3,2)])
    layer=conflict.uv_layers.new(name='UV');layer.data[1].uv=(0,0);layer.data[3].uv=(1,1)
    try:api.BlenderExporterAPI.uvValues(conflict,None)
    except ValueError:pass
    else:raise AssertionError('UV conflict not rejected')
armature=bpy.data.armatures.new('unsupported-skeleton')
armature_obj=bpy.data.objects.new('unsupported-skeleton',armature)
bpy.context.scene.collection.objects.link(armature_obj)
bpy.context.view_layer.objects.active=armature_obj
armature_obj.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bone=armature.edit_bones.new('bone');bone.tail=(0,0,1)
bpy.ops.object.mode_set(mode='OBJECT')
armature.bones['bone']['boneFunction']=1
try: api.BlenderExporterAPI.getSkeletalStructure(None)
except ValueError: pass
else: raise AssertionError('Unsupported Armature export accepted')
addon.unregister()
print('PASS: failure preserves existing output; source transforms/data unchanged; UV conflict rejected')
