import sys,importlib
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root.parent));sys.dont_write_bytecode=True
nodes=importlib.import_module(root.name+".blender.BlenderNodesFunctions")
mat=bpy.data.materials.new('shader regression');mat.use_nodes=True;tree=mat.node_tree;tree.nodes.clear()
image=bpy.data.images.new('synthetic',width=1,height=1)
diffuse=nodes.diffuseSetup(tree,image);normal=nodes.normalSetup(tree,image);rmt=nodes.rmtSetup(tree,image)
g=nodes.principledSetup(tree);next(g);g.send(diffuse);g.send(normal);g.send('');g.send(rmt);g.send('');end=next(g);nodes.finishSetup(tree,end)
bsdf=tree.nodes.get('Principled BSDF')
for socket in ['Base Color','Normal','Roughness','Metallic','Subsurface Weight']:assert bsdf.inputs[socket].is_linked,socket
assert not bsdf.inputs['Alpha'].is_linked
assert not bsdf.inputs['IOR'].is_linked
assert all(n.mode=='RGB' for n in tree.nodes if n.bl_idname in ['ShaderNodeSeparateColor','ShaderNodeCombineColor'])
assert tree.nodes['Normal Texture'].image.colorspace_settings.name=='Non-Color'
assert tree.nodes['Diffuse Texture'].image.colorspace_settings.name=='sRGB'
assert tree.nodes.get('Material Output').inputs['Surface'].is_linked
print('PASS: modern RGB node channels, named Principled sockets, independent texture color spaces',bpy.app.version_string)
