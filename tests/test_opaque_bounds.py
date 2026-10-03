import struct
import unittest

from fixtures import opaque_fixture, parse


class OpaqueBoundsTests(unittest.TestCase):
    def test_unresolved_global_table_and_raw_headers(self):
        for fields, count in [((0, 0), 23), ((0, 60), 23), ((12,), 195)]:
            with self.subTest(fields=fields):
                source = opaque_fixture(fields, count)
                model = parse(source)
                meshes = model.MeshParts
                self.assertEqual(meshes.ownershipState, 'unresolved')
                self.assertIsNone(meshes.ownershipMapping)
                self.assertTrue(all(not m.BoundingBoxes for m in meshes))
                self.assertEqual([m.rawHeader[41] for m in meshes], list(fields))
                self.assertEqual(len(meshes.BoundingBoxes.rawRecords), count * 144)
                self.assertEqual([b.boneIndex for b in meshes.BoundingBoxes.BoundingBoxes], [0] * count)
                self.assertEqual(model.serialize(), source)

    def test_header_rewrite_refused(self):
        model = parse(opaque_fixture())
        model.MeshParts.Meshes[0].Header.boundingBoxCount = 1
        with self.assertRaisesRegex(ValueError, 'offset-41'):
            model.serialize()

    def test_bbox_rewrite_refused(self):
        model = parse(opaque_fixture())
        model.MeshParts.BoundingBoxes.BoundingBoxes[0].radius = 42
        with self.assertRaisesRegex(ValueError, 'unresolved ownership'):
            model.serialize()

    def test_parsed_geometry_edit_refused(self):
        model = parse(opaque_fixture())
        model.MeshParts.Meshes[0].Vertices[0].position.x += 1
        with self.assertRaisesRegex(ValueError, 'edited parsed MOD3'):
            model.serialize()

    def test_physical_corruption_remains_rejected(self):
        source = opaque_fixture()
        model = parse(source)
        start = model.Header.meshOffset + model.Header.meshCount * 80
        for count in [0, 22, 24, 0xffffffff]:
            corrupt = bytearray(source)
            struct.pack_into('<I', corrupt, start, count)
            with self.subTest(count=count), self.assertRaises((ValueError, IndexError)):
                parse(corrupt)
        with self.assertRaises((ValueError, IndexError)):
            parse(source[:model.Header.vertexOffset - 1])


if __name__ == '__main__':
    unittest.main()
