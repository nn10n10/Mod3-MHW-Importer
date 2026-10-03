import unittest, struct, math, types, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
pkg=types.ModuleType("mod3_binary_test");pkg.__path__=[str(root)];sys.modules[pkg.__name__]=pkg
from mod3_binary_test.common.Cstruct import minifloatDeserialize, minifloatSerialize, Cstruct
from mod3_binary_test.common.FileLike import FileLike
from mod3_binary_test.mod3.Mod3VertexBuffers import Mod3VertexWeightExtended
from mod3_binary_test.mod3.Mod3Mesh import Mod3MeshCollection

class BinaryTests(unittest.TestCase):
    def test_half_all_bit_patterns(self):
        for bits in range(65536):
            data=struct.pack('<H',bits); expected=struct.unpack('<e',data)[0];actual=minifloatDeserialize(data)
            if math.isnan(expected): self.assertTrue(math.isnan(actual))
            else:
                self.assertEqual(actual,expected)
                self.assertEqual(minifloatSerialize(actual),data)
    def test_eight_weights_independent_fixture(self):
        data=struct.pack('<I4B', 256 | (128<<10) | (64<<20) | (2<<30), 10,20,30,40)
        weight=Mod3VertexWeightExtended();weight.marshall(FileLike(data))
        self.assertAlmostEqual(weight.weights[-1],1-(256+128+64)/1023-100/255)
        self.assertEqual(weight.serialize(),data)
    def test_file_bounds(self):
        for pos in (-1,5):
            with self.assertRaises(IndexError):FileLike(b'1234').seek(pos)
        with self.assertRaises(IndexError):FileLike(b'1').read(2)
    def test_array_size(self):
        for values in ([1],[1,2,3]):
            with self.assertRaises(ValueError): Cstruct({'v':'ushort[2]'}).serialize({'v':values})
    def test_truncated_mesh_not_swallowed(self):
        with self.assertRaises(ValueError):Mod3MeshCollection(1,0,0).marshall(FileLike(bytes(4)))

    def test_all_blocktypes_full_file(self):
        from fixtures import fixture, parse, Mod3Vertex
        for blocktype in Mod3Vertex.blocklist:
            data=fixture(blocktype).serialize()
            self.assertEqual(parse(data).serialize(),data)
    def test_header_and_bbox_rejection(self):
        from fixtures import fixture, parse
        data=fixture().serialize(); model=parse(data)
        for offset,value,fmt in [(0,0,'I'),(32,2**63,'Q'),(int(model.Header.meshOffset)+41,0,'B')]:
            bad=bytearray(data);struct.pack_into('<'+fmt,bad,offset,value)
            with self.assertRaises(ValueError):parse(bad)
        for limit in [0,319,model.Header.vertexOffset,model.Header.facesOffset]:
            with self.assertRaises((ValueError,IndexError,struct.error)):parse(data[:limit])
    def test_bone_map_and_cycles(self):
        from fixtures import fixture
        model=fixture(); bones=model.Skeleton.Skeleton
        bones[0].boneFunction=-1
        with self.assertRaises(ValueError):model.Skeleton.foldSkeletonToMap()
        bones[0].boneFunction=0; bones[1].boneFunction=0
        with self.assertRaises(ValueError):model.Skeleton.foldSkeletonToMap()
        bones[1].boneFunction=1; bones[0].parentId=1
        with self.assertRaises(ValueError):model.Skeleton.validateHierarchy()

if __name__=='__main__':unittest.main()
