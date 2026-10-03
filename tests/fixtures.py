"""Synthetic format fixtures only; no game assets are distributed."""
import sys, types, copy, math
from pathlib import Path
root=Path(__file__).resolve().parents[1]
pkg=types.ModuleType("mod3_fixture_pkg");pkg.__path__=[str(root)];sys.modules[pkg.__name__]=pkg
from mod3_fixture_pkg.mod3.Mod3 import Mod3
from mod3_fixture_pkg.mod3.Mod3VertexBuffers import Mod3Vertex
from mod3_fixture_pkg.mod3.Mod3ExporterErrorHandler import ErrorHandler
from mod3_fixture_pkg.common.FileLike import FileLike

def fixture(blocktype=0xf637401c, weight_bits=0):
    defaults=copy.deepcopy(ErrorHandler.propertyDefaults)
    header={"vertexIds":12,"groupCount":0,"materialCount":1,"creationDate":123,
            "boundingData":{"center":[.5,.5,0],"radius":math.sqrt(.5),"minBox":[0,0,0,0],"maxBox":[1,1,0,0]},
            "floatData":{k.split(':')[1]:v for k,v in defaults.items() if k.startswith('FloatSegment:')},
            "byteData":{"unkn1":[0]*64}}
    skeleton=[{"boneFunction":i,"parentId":255 if i==0 else i-1,"child":255,"unkn2":0,"length":0,"x":0,"y":0,"z":0} for i in range(8)]
    matrices=[[[int(r==c) for c in range(4)] for r in range(4)] for _ in skeleton]
    properties={k:defaults[k] for k in ['shadowCast','visibleCondition','lod','weightDynamics','unkn3','mapData','unknownIndex','intUnknown']}
    properties.update(blocktype=blocktype,materialIdx=0)
    layout=Mod3Vertex.blocklist[blocktype]; count=layout.get('weights',0)
    weights=[(i, 0.1 if i<count-1 else 1-0.1*(count-1)) for i in range(count)]
    vertices=[{"position":pos,"weightBits":weight_bits,"normal":[0,0,127,0],"tangent":[127,0,0,127],"uvs":[uv]*layout['uvs'],"weights":weights[:],"colour":[32,64,128,255]} for pos,uv in zip([(0,0,0),(1,0,0),(0,1,0)],[(0,1),(1,1),(0,0)])]
    box={"boneIndex":255,"aabbCenter":[.5,.5,0],"radius":1,"aabbMin":[0,0,0,0],"aabbMax":[1,1,0,0],"oabbMatrix":[1,0,0,0,0,1,0,0,0,0,1,0,.5,.5,0,1],"oabbVector":[.5,.5,0,0]}
    mesh={"properties":properties,"mesh":vertices,"faces":[{"v1":0,"v2":1,"v3":2}],"boundingBoxes":[box]}
    model=Mod3();model.construct(header,[{"materialName":"Synthetic"}],{},skeleton,matrices,matrices,[mesh],[1,2,3])
    return model

def parse(data):
    model=Mod3();model.marshall(FileLike(data));return model


def opaque_fixture(mesh_fields=(0, 60), record_count=23):
    """Independent ownership mismatches; repeated bones and opaque spacers."""
    model = fixture()
    original = model.MeshParts.Meshes[0]
    model.MeshParts.Meshes = [copy.deepcopy(original) for _ in mesh_fields]
    box = model.MeshParts.BoundingBoxes.BoundingBoxes[0].sceneProperties()
    box['boneIndex'] = 0
    box['spacer'] = list(range(12))
    model.MeshParts.BoundingBoxes.construct([copy.deepcopy(box) for _ in range(record_count)])
    for mesh, value in zip(model.MeshParts, mesh_fields):
        mesh.Header.boundingBoxCount = value
        mesh.Header.NULL_1 = 12345
    model.calculateCountsOffsets()
    model.MeshParts.realignFaces()
    return model.serialize()
