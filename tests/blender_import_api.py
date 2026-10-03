import sys, importlib, math
from pathlib import Path
from types import SimpleNamespace
import bpy
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(root.parent))
addon=importlib.import_module(root.name); addon.register()
api=importlib.import_module(root.name+".blender.BlenderMod3Importer").BlenderImporterAPI
part={"vertices":[(0,0,0),(1,0,0),(0,1,0)],"faces":[(0,1,2)],"properties":{"lod":1}}
mesh,obj=api.createMesh("test",part)
api.createTextureLayer("UV0",mesh,[(0,0),(1,0),(0,1)])
api.setNormals([(0,0,127)]*3,mesh)
for invalid in [[(0,0,0)]*3, [(float('nan'),0,1)]*3]:
    try: api.setNormals(invalid,mesh)
    except ValueError: pass
    else: raise AssertionError('Invalid normals accepted')
assert mesh.has_custom_normals
assert all(abs(n.vector.z-1)<1e-5 for n in mesh.corner_normals)
assert not any(edge.use_edge_sharp for edge in mesh.edges)
assert [tuple(x.uv) for x in mesh.uv_layers[0].data]==[(0,0),(1,0),(0,1)]
opposing = bpy.data.meshes.new("opposing")
opposing.from_pydata([(0,0,0),(0,1,0),(1,0,0)], [], [(0,1,2),(0,2,1)])
api.setNormals([(0,45,-127),(0,5,127),(0,25,124)], opposing)
expected = [(0,45,-127),(0,5,127),(0,25,124)]
assert all(edge.use_edge_sharp for edge in opposing.edges)
assert all(corner.vector.dot(Vector(expected[loop.vertex_index]).normalized()) > 1-1e-4
           for loop,corner in zip(opposing.loops,opposing.corner_normals))
ctx=SimpleNamespace(path="test.mod3",meshes=[])
api.createEmptyTree([],ctx)
assert 255 in ctx.armature
api.createArmature([],ctx)
assert ctx.skeleton.type=="ARMATURE"
api.maximizeClipping(ctx)
other = bpy.data.scenes.new("other")
other.collection.objects.link(obj)
image = bpy.data.images.new("shared", width=1, height=1)
api.clearScene(ctx)
assert obj.name in other.objects
assert image.name in bpy.data.images
addon.unregister()
print("PASS: mesh, UV, custom normals, empty skeleton, armature API",bpy.app.version_string)
