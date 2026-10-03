"""Headless real operators, synthetic or user-owned samples; never modifies inputs.
Usage: blender -b --factory-startup --python-exit-code 1 --python this.py -- --output DIR [--samples DIR]
"""
import sys, importlib, argparse, tempfile, json, traceback, struct, hashlib, os
from pathlib import Path
import bpy
from mathutils import Vector
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root.parent));sys.path.insert(0,str(root/'tests'))
from fixtures import fixture, parse, Mod3Vertex
addon=importlib.import_module(root.name);addon.register()
args=argparse.ArgumentParser();args.add_argument('--output',required=True);args.add_argument('--samples',default=os.environ.get('MHW_MOD3_TEST_DATA'));opts=args.parse_args(sys.argv[sys.argv.index('--')+1:])
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
            "global_bbox_raw":model.MeshParts.BoundingBoxes.rawRecords.hex(),
            "mesh_headers_raw":[mesh.rawHeader.hex() for mesh in model.MeshParts],
            "meshes":[{"properties":mesh.Header.externalProperties(),"vertices":[bytes(v.serialize()).hex() for v in mesh.Vertices],
                        "faces":[[face.v1-mesh.Header.vertexSub,face.v2-mesh.Header.vertexSub,face.v3-mesh.Header.vertexSub] for face in mesh.Faces],
                        "bounds":[fields(box) for box in mesh.BoundingBoxes]} for mesh in model.MeshParts],
            "trailing":list(model.Trailing.Remnants)}

def check_scene(model):
    meshes=sorted((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:o.data.name)
    bones={o['indexHint']:o for o in bpy.context.scene.objects if o.type=='EMPTY' and 'boneFunction' in o}
    assert len(meshes)==model.Header.meshCount
    assert len(bones)==model.Header.boneCount
    for index,bone in enumerate(model.Skeleton.Skeleton):
        obj=bones[index]
        assert obj['boneFunction']==bone.boneFunction
        actual_parent=255 if obj.parent.get('Type')=='MOD3_SkeletonRoot' else obj.parent['indexHint']
        assert actual_parent==bone.parentId
    degenerate_normal_mismatches=0
    nondegenerate_normal_mismatches=0
    for obj,part in zip(meshes,model.MeshParts):
        mesh=obj.data
        assert len(mesh.vertices)==len(part.Vertices)
        assert len(mesh.polygons)==len(part.Faces)
        expected=part.traditionalMeshStructure(2)
        for vertex,position in zip(mesh.vertices,expected['vertices']):
            assert tuple(vertex.co)==tuple(position)
        assert [tuple(p.vertices) for p in mesh.polygons]==[tuple(getattr(f,k)-part.Header.vertexSub for k in ('v1','v2','v3')) for f in part.Faces]
        for layer,uvs in zip(mesh.uv_layers,expected['uvs']):
            for loop,value in zip(mesh.loops,layer.data):
                assert all(abs(a-b)<1e-6 for a,b in zip(value.uv,uvs[loop.vertex_index]))
        assert len(mesh.uv_layers)==len(expected['uvs'])
        degenerate_loops={li for polygon in mesh.polygons if polygon.area==0 for li in polygon.loop_indices}
        for loop,normal in zip(mesh.loops,mesh.corner_normals):
            if normal.vector.dot(Vector(expected['normals'][loop.vertex_index]).normalized())<=1-1e-4:
                if loop.index in degenerate_loops:
                    degenerate_normal_mismatches+=1
                else:
                    nondegenerate_normal_mismatches+=1
        if expected['colour']:
            assert len(mesh.color_attributes)==1
            for loop,item in zip(mesh.loops,mesh.color_attributes[0].data):
                col=expected['colour'][loop.vertex_index]
                assert all(abs(a-b/255)<1/255+1e-6 for a,b in zip(item.color_srgb,(col.Red,col.Green,col.Blue,col.Alpha)))
        for group,weights in expected['weightGroups'].items():
            bone_index=group if isinstance(group,int) else group[0]
            # Blender may rename a newly imported bone when earlier unlinked
            # datablocks still own its requested name. Groups reference that
            # actual object name; indexHint supplies the original bone identity.
            function=int(bones[bone_index].name.split('.')[1])
            suffix='%03d'%function if isinstance(group,int) else '(%03d,%s)'%(function,group[1])
            actual=obj.vertex_groups['BoneFunction.'+suffix]
            for index,weight in weights:
                assert abs(actual.weight(index)-weight)<1e-6
    return {'meshes':len(meshes),'bones':len(bones),'vertices':sum(len(o.data.vertices) for o in meshes),
            'faces':sum(len(o.data.polygons) for o in meshes),'geometry_weights_uv_colors_checked':True,
            'nondegenerate_normals_checked':True,'degenerate_normal_mismatches':degenerate_normal_mismatches,
            'nondegenerate_normal_mismatches':nondegenerate_normal_mismatches}

def run(source, label):
    a=out/(label+'-A.mod3');b=out/(label+'-B.mod3')
    before_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    import_opts=dict(clear_scene=True,high_lod=False,import_textures=False,import_materials=False,weight_format='Slash',load_group_functions=True,maximize_clipping=False)
    export_opts=dict(highest_lod=False,coerce_fourth=False,export_bounds='Explicit')
    assert bpy.ops.custom_import.import_mhw_mod3(filepath=str(source),**import_opts)=={'FINISHED'}
    original=parse(source.read_bytes())
    scene_evidence=check_scene(original)
    before=[(obj.name,obj.matrix_world.copy(),obj.data.name if obj.data else None) for obj in bpy.context.scene.objects]
    counts=(len(bpy.data.objects),len(bpy.data.meshes))
    assert bpy.ops.custom_export.export_mhw_mod3(filepath=str(a),**export_opts)=={'FINISHED'}
    assert counts==(len(bpy.data.objects),len(bpy.data.meshes))
    assert before==[(obj.name,obj.matrix_world.copy(),obj.data.name if obj.data else None) for obj in bpy.context.scene.objects]
    assert bpy.ops.custom_import.import_mhw_mod3(filepath=str(a),**import_opts)=={'FINISHED'}
    assert check_scene(parse(a.read_bytes()))==scene_evidence
    assert bpy.ops.custom_export.export_mhw_mod3(filepath=str(b),**export_opts)=={'FINISHED'}
    sa,sb=semantic(parse(a.read_bytes())),semantic(parse(b.read_bytes()))
    assert sa==sb,'A/B semantic mismatch'
    source_semantic=semantic(original)
    changed=[key for key in sa if sa[key]!=source_semantic[key]]
    # Report original/A differences even if A/B is stable.
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before_hash
    aa,bb=bytearray(a.read_bytes()),bytearray(b.read_bytes());aa[40:48]=bb[40:48]=bytes(8)
    exact = source.read_bytes()==a.read_bytes()==b.read_bytes()
    if original.MeshParts.ownershipState=='unresolved':
        assert exact, 'Opaque preservation must be byte-perfect, including unknown fields'
    normal_status='FAIL' if scene_evidence['nondegenerate_normal_mismatches'] else ('PARTIAL' if scene_evidence['degenerate_normal_mismatches'] else 'PASS')
    # Finish preservation checks even when an independent scene-fidelity check
    # failed; keep that failure visible and return a nonzero process exit below.
    return {"name":label,"status":"FAIL" if normal_status=='FAIL' else "PASS",
            "preservation_status":"PASS","scene_normals_status":normal_status,
            "A_B_semantic":True,"A_B_binary_except_creationDate":aa==bb,
            "source_A_B_binary_identical":exact,"bbox_raw_preserved":sa['global_bbox_raw']==source_semantic['global_bbox_raw'],
            "offset_41_preserved":[m.rawHeader[41] for m in original.MeshParts]==[m.rawHeader[41] for m in parse(a.read_bytes()).MeshParts],
            "scene_evidence":scene_evidence,"original_A_changed_fields":changed}

results=[]
for block in Mod3Vertex.blocklist:
    source=out/('synthetic-%08x.mod3'%block);source.write_bytes(fixture(block).serialize())
    try:results.append(run(source,'synthetic-%08x'%block))
    except Exception:results.append({"name":str(block),"status":"FAIL","error":traceback.format_exc()})
for block in [0xf637401c,0x81f58067]:
    source=out/('flags-%08x.mod3'%block);source.write_bytes(fixture(block, weight_bits=2).serialize())
    try:results.append(run(source,'flags-%08x'%block))
    except Exception:results.append({"name":'flags-%08x'%block,"status":"FAIL","error":traceback.format_exc()})
if opts.samples:
    for source in sorted(Path(opts.samples).rglob('*.mod3')):
        try:results.append(run(source,source.stem))
        except Exception:results.append({"name":source.name,"status":"FAIL","error":traceback.format_exc()})
(out/'results.json').write_text(json.dumps({"blender":bpy.app.version_string,"python":sys.version,"results":results},indent=2),encoding='utf-8')
addon.unregister()
print(json.dumps(results,indent=2))
if any(row['status']=='FAIL' for row in results):raise RuntimeError('Round-trip failures; see results.json')
