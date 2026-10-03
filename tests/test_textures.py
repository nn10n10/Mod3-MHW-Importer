import unittest,importlib.util,tempfile,shutil,sys,types
from pathlib import Path
root=Path(__file__).resolve().parents[1]
pkg=types.ModuleType('texture_test_pkg');pkg.__path__=[str(root)];sys.modules[pkg.__name__]=pkg
from texture_test_pkg.mrl3 import TextureConverter as converter
from texture_test_pkg.mrl3.Mrl3 import MRL3,MRL3Material,MRL3Texture
from texture_test_pkg.common.FileLike import FileLike

class TextureTests(unittest.TestCase):
    def test_arguments_spaces_unicode(self):
        path=Path(tempfile.gettempdir())/'texture space'/'\u4e59\u5b97_NM.dds'
        args=converter.conversionArguments('dds',path)
        self.assertEqual(args[1],str(path.resolve()))
        self.assertEqual(args[-1],str(path.parent.resolve()))
        self.assertIn('-sepalpha',args)
        self.assertNotIn('"',args[1])
    def test_missing_executable_without_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'TextureConverter.py';shutil.copyfile(root/'mrl3/TextureConverter.py',file)
            spec=importlib.util.spec_from_file_location('missing_converter',file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            with self.assertRaises(FileNotFoundError):module.convertDDSToPNG(str(file.with_suffix('.dds')))
    def test_truncated_mrl3(self):
        with self.assertRaises(IndexError):MRL3().marshall(FileLike(bytes(4)))
    def test_missing_map_is_not_first_texture(self):
        self.assertEqual(MRL3Material().getMapIndex('Albedo'),-1)

    def test_texture_index_upper_bound(self):
        from texture_test_pkg.mrl3.Mrl3 import MRL3ResourceBinding, generalhash
        model=MRL3();material=MRL3Material();material.Header.materialNameHash=generalhash('test')
        resource=MRL3ResourceBinding();resource.mapTypeName='Albedo';resource.texIdx=2
        material.resourceBindings=[resource];model.Materials=[material];model.Textures=[MRL3Texture()]
        with self.assertRaises(KeyError):model['test']

if __name__=='__main__':unittest.main()
