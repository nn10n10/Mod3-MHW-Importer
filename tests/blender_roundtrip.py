"""Headless real operators, synthetic or user-owned samples; never modifies inputs.
Usage: blender -b --factory-startup --python-exit-code 1 --python this.py -- --output DIR [--samples DIR]
"""
import sys, importlib, argparse, tempfile, json, traceback, struct, hashlib
from pathlib import Path
import bpy
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root.parent));sys.path.insert(0,str(root/'tests'))
from fixtures import fixture, parse, Mod3Vertex
addon=importlib.import_module(root.name);addon.register()
args=argparse.ArgumentParser();args.add_argument('--output',required=True);args.add_argument('--samples');opts=args.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(opts.output);out.mkdir(parents=True,exist_ok=True)

def semantic(model):
    def fields(value):return {key:getattr(value,key) for key in value.fields}
    return {"header":{key:getattr(model.Header,key) for key in ['id','version','version2','boneCount','meshCount','materialCount','vertexCount','faceCount','vertexIds','groupCount']},
            "bounding_header":fields(model.Header.Boundaries),"float_header":fields(model.Header.FloatSegment),"byte_header":fields(model.Header.ByteSegment),
            "materials":[mat.materialName for mat in model.Materials],
            "groups":[fields(group) for group in model.GroupProperties],
            "bones":[fields(bone) for bone in model.Skeleton.Skeleton],
            "matrices":[(l.matrix,a.matrix) for l,a in model.Skeleton.Matrices],
            "bone_map":model.Skeleton.BoneMap.boneRemap,
            "meshes":[{"properties":mesh.Header.externalProperties(),"vertices":[bytes(v.serialize()).hex() for v in mesh.Vertices],
                        "faces":[[face.v1-mesh.Header.vertexSub,face.v2-mesh.Header.vertexSub,face.v3-mesh.Header.vertexSub] for face in mesh.Faces],
                        "bounds":[fields(box) for box in mesh.BoundingBoxes]} for mesh in model.MeshParts],
            "trailing":list(model.Trailing.Remnants)}

def run(source, label):
    a=out/(label+'-A.mod3');b=out/(label+'-B.mod3')
    before_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    import_opts=dict(clear_scene=True,high_lod=False,import_textures=False,import_materials=False,weight_format='Slash',load_group_functions=True,maximize_clipping=False)
    export_opts=dict(highest_lod=False,coerce_fourth=False,export_bounds='Explicit')
    original=parse(source.read_bytes())
    assert bpy.ops.custom_import.import_mhw_mod3(filepath=str(source),**import_opts)=={'FINISHED'}
    before=[(obj.name,obj.matrix_world.copy(),obj.data.name if obj.data else None) for obj in bpy.context.scene.objects]
    counts=(len(bpy.data.objects),len(bpy.data.meshes))
    assert bpy.ops.custom_export.export_mhw_mod3(filepath=str(a),**export_opts)=={'FINISHED'}
    assert counts==(len(bpy.data.objects),len(bpy.data.meshes))
    assert before==[(obj.name,obj.matrix_world.copy(),obj.data.name if obj.data else None) for obj in bpy.context.scene.objects]
    assert bpy.ops.custom_import.import_mhw_mod3(filepath=str(a),**import_opts)=={'FINISHED'}
    assert bpy.ops.custom_export.export_mhw_mod3(filepath=str(b),**export_opts)=={'FINISHED'}
    sa,sb=semantic(parse(a.read_bytes())),semantic(parse(b.read_bytes()))
    assert sa==sb,'A/B semantic mismatch'
    source_semantic=semantic(original)
    changed=[key for key in sa if sa[key]!=source_semantic[key]]
    # Report original/A differences even if A/B is stable.
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before_hash
    aa,bb=bytearray(a.read_bytes()),bytearray(b.read_bytes());aa[40:48]=bb[40:48]=bytes(8)
    return {"name":label,"status":"PASS","A_B_semantic":True,"A_B_binary_except_creationDate":aa==bb,"original_A_changed_fields":changed}

results=[]
for block in Mod3Vertex.blocklist:
    source=out/('synthetic-%08x.mod3'%block);source.write_bytes(fixture(block).serialize())
    try:results.append(run(source,'synthetic-%08x'%block))
    except Exception:results.append({"name":str(block),"status":"FAIL","error":traceback.format_exc()})
if opts.samples:
    for source in sorted(Path(opts.samples).rglob('*.mod3')):
        try:results.append(run(source,source.stem))
        except Exception:results.append({"name":source.name,"status":"FAIL","error":traceback.format_exc()})
(out/'results.json').write_text(json.dumps({"blender":bpy.app.version_string,"python":sys.version,"results":results},indent=2),encoding='utf-8')
addon.unregister()
print(json.dumps(results,indent=2))
if any(row['status']=='FAIL' for row in results):raise RuntimeError('Round-trip failures; see results.json')
