import sys,importlib,itertools
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root.parent));sys.dont_write_bytecode=True
api=importlib.import_module(root.name+".blender.BlenderMod3Exporter").BlenderExporterAPI
estimate=importlib.import_module(root.name+".boundingbox.boundingBoxCalculations").estimateBoundingBox
complete=importlib.import_module(root.name+".boundingbox.linalg").completeBasis
for n in [(1,2,3),(0,1,0),(1,0,0)]:assert abs(Vector(n).dot(complete(n)))<1e-6
sets=[[(2,3,4)],[(2,3,4),(4,5,6)],[(2,3,4),(4,3,4),(2,6,4)], list(itertools.product((2,4),(3,6),(4,8)))]
for points in sets:
    vertices=[Vector(p) for p in points]
    minimum,maximum,center=api.calculateAABB(vertices)
    assert all(abs(center[i]-(minimum[i]+maximum[i])/2)<1e-6 for i in range(3))
    matrix,extent=estimate(vertices)
    for p in vertices:
        local=matrix.inverted() @ p
        assert all(abs(local[i])<=extent[i]+1e-5 for i in range(3)),(points,local,extent)
print("PASS: orthogonal basis, offset AABB, degenerate and 3D OABB containment")
