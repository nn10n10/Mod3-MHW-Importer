# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 13:38:47 2019

@author: AsteriskAmpersand
"""
#from .dbg import dbg_init
#dbg_init()

bl_info = {
    "name": "MHW Mod3 Model Importer",
    "category": "Import-Export",
    "author": "AsteriskAmpersand (Code) & CrazyT (Structure)",
    "location": "File > Import-Export > Mod3/MHW",
    "version": (2,1,1),
    "blender": (4, 4, 0),
}
 
import bpy

from .operators.mod3properties import symmetricPair
from .operators.mod3import import ImportMOD3
from .operators.mod3export import ExportMOD3
from .operators.mod3import import menu_func_import as mhw_model_menu_func_import
from .operators.mod3export import menu_func_export as mhw_model_menu_func_export

classes = (ImportMOD3, ExportMOD3)
_registered_classes = []
_menu_callbacks = []


def register():
    if _registered_classes:
        return
    try:
        for cls in classes:
            bpy.utils.register_class(cls)
            _registered_classes.append(cls)
        bpy.types.Object.MHW_Symmetric_Pair = symmetricPair
        for menu, callback in ((bpy.types.TOPBAR_MT_file_import, mhw_model_menu_func_import),
                               (bpy.types.TOPBAR_MT_file_export, mhw_model_menu_func_export)):
            menu.append(callback)
            _menu_callbacks.append((menu, callback))
    except Exception:
        unregister()
        raise


def unregister():
    while _menu_callbacks:
        menu, callback = _menu_callbacks.pop()
        menu.remove(callback)
    if hasattr(bpy.types.Object, "MHW_Symmetric_Pair"):
        del bpy.types.Object.MHW_Symmetric_Pair
    while _registered_classes:
        bpy.utils.unregister_class(_registered_classes.pop())


if __name__ == "__main__":
    register()
