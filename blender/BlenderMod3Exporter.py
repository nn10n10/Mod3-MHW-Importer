# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 03:16:11 2019

@author: AsteriskAmpersand
"""


import bpy
import math
import os
import time
import sys
from mathutils import Matrix, Vector
from collections import OrderedDict

try:
    from ..mod3.ModellingApi import ModellingAPI, debugger
    from ..mod3.Mod3DelayedResolutionWeights import BufferedWeight, BufferedWeights
    from ..mod3.Mod3VertexBuffers import Mod3Vertex
    from ..mod3.Mod3Mesh import Mod3BoundingBox
    from ..mod3.Mod3Components import Mod3GroupProperty,Mod3HeaderFloatSegment,Mod3HeaderByteSegment
    from ..blender.BlenderSupressor import SupressBlenderOps
    from ..blender.BlenderNormals import denormalize
    from ..boundingbox.boundingBoxCalculations import estimateBoundingBox
    from ..common.crc import CrcJamcrc
except:
    sys.path.insert(0, r'..\mod3')
    sys.path.insert(0, r'..\common')
    sys.path.insert(0, r'..\blender')
    sys.path.insert(0, r'..\boundingbox')
    from Mod3DelayedResolutionWeights import BufferedWeight, BufferedWeights
    from Mod3VertexBuffer import Mod3Vertex
    from ModellingApi import ModellingAPI, debugger
    from Mod3Mesh import Mod3BoundingBox
    from Mod3Components import Mod3GroupProperty,Mod3HeaderFloatSegment,Mod3HeaderByteSegment   
    from BlenderSupressor import SupressBlenderOps
    from boundingBoxCalculations import estimateBoundingBox
    from crc import CrcJamcrc
    
generalhash =  lambda x:  CrcJamcrc.calc(x.encode())
    
class MeshClone():
    def __init__(self, mesh):
        self.original = mesh
        #self.clone = None
                   
    def __enter__(self):
        if self.original.modifiers:
            raise ValueError("Apply modifiers explicitly before MOD3 export; automatic evaluation is not supported")
        transform = self.original.matrix_world.copy()
        if transform.to_3x3().determinant() <= 1e-12:
            raise ValueError("Mirrored or singular object transforms are not supported")
        self.copy = self.original.copy()
        self.copy.data = self.original.data.copy()
        try:
            normals = [transform.to_3x3().inverted().transposed() @ n.vector
                       for n in self.copy.data.corner_normals]
            self.copy.data.transform(transform)
            self.copy.matrix_world = Matrix.Identity(4)
            if normals:
                self.copy.data.normals_split_custom_set(normals)
            return self.copy
        except Exception:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, exc_type, exc_value, exc_traceback):
        data = self.copy.data
        bpy.data.objects.remove(self.copy, do_unlink=True)
        bpy.data.meshes.remove(data)
        return False

class SkeletonMap():
    def __init__(self,*args):
        self.boneNamesToIndices = {}
        self.boneNamesToBoneObject = {}
        self.boneIndexToBone = {}
    def __getitem__(self,key):
        return self.boneNamesToIndices[key]
    def __setitem__(self,key,value):
        cix,bone = value
        self.boneNamesToIndices[key] = cix
        self.boneNamesToBoneObject[key] = bone
        self.boneIndexToBone[cix] = bone
    def __contains__(self,key):
        return key in self.boneNamesToIndices
    def getBoneByName(self,key):
        return self.boneNamesToBoneObject[key]
    def getBoneByIndex(self,key):
        return self.boneIndexToBone[key]
    def __bool__(self):
        return bool(self.boneNamesToIndices)
    
import re
class BlenderExporterAPI(ModellingAPI):
    MACHINE_EPSILON = 2**-19
    dbg = debugger()

    class SettingsError(Exception):
        pass

    @staticmethod
    def showMessageBox(message = "", title = "Message Box", icon = 'INFO'):
    
        def draw(self, context):
            self.layout.label(text=message)
    
        if bpy.app.background:
            print(title + ": " + message)
        else:
            bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
    
    @staticmethod
    def displayErrors(errors):
        if errors:
            print(errors)
            BlenderExporterAPI.showMessageBox("Warnings have been Raised, check them in Window > Toggle_System_Console", title = "Warnings and Error Log")
# =============================================================================
# Main Exporter Calls
# =============================================================================

    @staticmethod
    def getSceneHeaders(options):
        header = {}
        trail = {}
        options.errorHandler.setSection("Scene Headers")
        BlenderExporterAPI.verifyLoad(bpy.context.scene,"TrailingData",options.errorHandler,trail)
        BlenderExporterAPI.calculateSceneBounds(header,options)
        BlenderExporterAPI.getFloatSegment(header,options)
        BlenderExporterAPI.getByteSegment(header,options)
        header["creationDate"] = int(time.time())
        for prop in ["groupCount", "materialCount","vertexIds"]:
            BlenderExporterAPI.verifyLoad(bpy.context.scene,prop,options.errorHandler,header)
        
        materials = OrderedDict()
        for ix in range(header["materialCount"]):
            BlenderExporterAPI.verifyLoad(bpy.context.scene,"MaterialName%d"%ix,options.errorHandler,materials)
        groupProperties = OrderedDict()
        for ix in range(header["groupCount"]):
            for prop in Mod3GroupProperty.fields:
                BlenderExporterAPI.verifyLoad(bpy.context.scene,"GroupProperty%d:%s"%(ix,prop),options.errorHandler,groupProperties)
        options.executeErrors()
        #bpy.context.scene
        return header,  groupProperties, trail["TrailingData"], list(materials.values())
    
    @staticmethod
    def getSegment(writeDestination,options,dataName,segmentName,fields):
        writeDestination[dataName] = {}
        data = writeDestination[dataName]
        prep = {}
        mapping = {segmentName+":%s"%s:s for s in fields }
        for field in mapping:
            BlenderExporterAPI.verifyLoad(bpy.context.scene,field,options.errorHandler,prep)
        for field in mapping:
            data[mapping[field]] = prep[field]
        return
    
    @staticmethod
    def getFloatSegment(writeDest,options): 
        BlenderExporterAPI.getSegment(writeDest,options,"floatData","FloatSegment",Mod3HeaderFloatSegment.fields)
    @staticmethod
    def getByteSegment(writeDest,options): 
        BlenderExporterAPI.getSegment(writeDest,options,"byteData","ByteSegment",Mod3HeaderByteSegment.fields)
    
    @staticmethod
    def calculateSceneBounds(writeDestination,options):
        meshes = BlenderExporterAPI.listMeshes(options)
        if meshes:
            corners = [mesh.matrix_world @ Vector(corner) for mesh in meshes for corner in mesh.bound_box]
            minBox = Vector([min(point[i] for point in corners) for i in range(3)])
            maxBox = Vector([max(point[i] for point in corners) for i in range(3)])
        else:
            minBox = Vector([0,0,0])
            maxBox = Vector([0,0,0])
        writeDestination["boundingData"] = {}
        writeDestination["boundingData"]["center"] = list((minBox+maxBox)/2)
        writeDestination["boundingData"]["radius"] = ((maxBox-minBox).length/2)
        writeDestination["boundingData"]["minBox"] = list(minBox)+[0]
        writeDestination["boundingData"]["maxBox"] = list(maxBox)+[0]        
        return
    
    @staticmethod
    def getSkeletalStructure(options):
        skeletonMap = SkeletonMap()
        if any(obj.type == 'ARMATURE' and any('boneFunction' in bone for bone in obj.data.bones)
               for obj in bpy.context.scene.objects):
            raise ValueError("MOD3 export supports EmptyTree skeletons; animation Armature export is not implemented")
        options.errorHandler.setSection("Skeleton")
        rootEmpty = BlenderExporterAPI.getRootEmpty()
        root = options.validateSkeletonRoot(rootEmpty)
        protoskeleton = []
        if root is not None:
            BlenderExporterAPI.recursiveEmptyDeconstruct(255, root, protoskeleton, skeletonMap, options.errorHandler)
        for bone in protoskeleton:
            bone["bone"]["child"] = skeletonMap[bone["bone"]["child"]] if bone["bone"]["child"] in skeletonMap else 255
        options.executeErrors()
        return [bone["bone"] for bone in protoskeleton], \
                [bone["LMatrix"] for bone in protoskeleton], \
                [bone["AMatrix"] for bone in protoskeleton], \
                skeletonMap
    
    @staticmethod
    def listMeshes(options):
        return sorted([o for o in bpy.context.scene.objects 
                       if o.type=="MESH" and (options.exportHidden or o.visible_get())
                           and not("Type" in o.data and o.data["Type"]=="MOD3_VM_Mesh")
                           and not("Type" in o.data and o.data["Type"]=="MHW_Ctrl_Structure")
                           and len(o.data.vertices)]
                    ,key=lambda x: x.data.name)

    @staticmethod
    def preservedBinary(options):
        from .BlenderOpaqueBounds import preserved_binary
        return preserved_binary(options)
    
    @staticmethod
    def getMeshparts(options, boneNames, materials):
        options.errorHandler.setSection("Meshes")
        options.errorHandler.attemptLoadDefaults(ModellingAPI.MeshDefaults, bpy.context.scene)
        meshlist = [BlenderExporterAPI.parseMesh(mesh,materials,boneNames,options) 
                    for mesh in BlenderExporterAPI.listMeshes(options)]
        options.validateMaterials(materials)
        options.executeErrors()
        return meshlist, materials
    
# =============================================================================
# Exporter Functions:
# =============================================================================    
        
    @staticmethod
    def getBoneVertices(mesh,options,skeletonMap):
        groups = {}
        groupToBone = {}
        groupName = lambda x: mesh.vertex_groups[x].name
        cannonicalGroupName = lambda w: BlenderExporterAPI.getCannonicalGroupName(w, skeletonMap, options.errorHandler)
        for group in mesh.vertex_groups:
            cannonical = cannonicalGroupName(group.name)
            if cannonical is not None:
                groupToBone[group.name] = cannonical
                groups[skeletonMap[cannonical]]=[]
        for vertex in mesh.data.vertices:
            weightGroups = vertex.groups
            if not len(weightGroups):
                if 255 not in groups:
                    groups[255] = []
                groups[255].append(Vector(vertex.co).freeze())
            for group in weightGroups:
                try:
                    name = groupName(group.group)
                except:
                    continue
                if name in groupToBone:
                    skeletonElement = skeletonMap[groupToBone[name]]
                    boneCoordinates = skeletonMap.getBoneByName(groupToBone[name]).matrix_world.inverted()
                    groups[skeletonElement].append((boneCoordinates @ vertex.co).freeze())
        return {k:list(set(i)) for k,i in groups.items() if len(i)>0}
    
    @staticmethod
    def calculateAABB(verts):
        minbox = Vector([min((v[0] for v in verts)),min((v[1] for v in verts)),min((v[2] for v in verts))])
        maxbox = Vector([max((v[0] for v in verts)),max((v[1] for v in verts)),max((v[2] for v in verts))])
        center = (maxbox+minbox)/2
        return list(minbox)+[0],list(maxbox)+[0],center
    
    @staticmethod
    def calculateMVBB(verts):
        mat,vec = estimateBoundingBox(verts)
        return [e for v in mat.transposed() for e in v],list(vec)+[0], Vector(vec).length
    
    @staticmethod
    def calculateBoundingBoxes(mesh,options,skeletonMap):
        boneCoordinates = BlenderExporterAPI.getBoneVertices(mesh,options,skeletonMap)
        boxes = []
        for coord in boneCoordinates:
            box = {}
            boxVert = boneCoordinates[coord]
            box["aabbMin"],box["aabbMax"],box["aabbCenter"] = BlenderExporterAPI.calculateAABB(boxVert)
            box["oabbMatrix"],box["oabbVector"],box["radius"]  = BlenderExporterAPI.calculateMVBB(boxVert)
            box["boneIndex"] = coord
            if box["radius"]:
                boxes.append(box)
        return sorted(boxes,key = lambda x:  x["boneIndex"] if x["boneIndex"] != 255 else -1)
    
    @staticmethod
    def getBoxBone(box,bones,options):
        constraints = [c for c in box.constraints if c.type == "CHILD_OF"]
        if len(constraints) != 1:
            raise ValueError("Bounding box needs one CHILD_OF constraint: " + box.name)
        bone = constraints[0].target
        if bone is None:
            return box.get("bone_index", 255), None
        if bone.get("Type") == "MOD3_SkeletonRoot":
            return 255, bone
        if bone.name not in bones:
            raise ValueError("Bounding box target is not in exported skeleton")
        return bones[bone.name], bone

    @staticmethod
    def getBoxClass(mesh, options, bones, boxclass):
        result = {}
        for box in mesh.children:
            if box.type != "LATTICE" or box.data.get("Type") != boxclass:
                continue
            boneIndex, bone = BlenderExporterAPI.getBoxBone(box, bones, options)
            if boneIndex in result:
                raise ValueError("Duplicate explicit bounding box bone index")
            result[boneIndex] = box
        return result

    @staticmethod
    def boxFromPair(bone, aabb, mvbb):
        # Import creates 2x2x2 lattices with coordinates [-.5, .5].
        corners = [aabb.matrix_world @ Vector(point.co_deform) for point in aabb.data.points]
        minimum, maximum, center = BlenderExporterAPI.calculateAABB(corners)
        matrix = mvbb.matrix_world.copy()
        # Boxes are expressed in the target bone's local coordinate system.
        constraints = [c for c in mvbb.constraints if c.type == 'CHILD_OF']
        if constraints and constraints[0].target is not None:
            inverse = constraints[0].target.matrix_world.inverted()
            matrix = inverse @ matrix
            corners = [inverse @ v for v in corners]
            minimum, maximum, center = BlenderExporterAPI.calculateAABB(corners)
        location, rotation, scale = matrix.decompose()
        extent = Vector([abs(value)/2 for value in scale])
        unscaled = rotation.to_matrix().to_4x4()
        unscaled.translation = location
        metadata = mvbb.get("mod3_metadata", {})
        minimum[3] = metadata.get("aabbMin", [0]*4)[3]
        maximum[3] = metadata.get("aabbMax", [0]*4)[3]
        return {"boneIndex": bone, "aabbCenter": list(center), "radius": metadata.get("radius", extent.length),
                "aabbMin": minimum, "aabbMax": maximum,
                "spacer": list(metadata.get("spacer", [0xCD]*12)),
                "oabbMatrix": [v for col in unscaled.transposed() for v in col],
                "oabbVector": list(extent)+[metadata.get("oabbVector", [0]*4)[3]]}

    @staticmethod
    def getLatticeBoxes(mesh, options, boneNames):
        mvbb = BlenderExporterAPI.getBoxClass(mesh, options, boneNames, "MOD3_BoundingBox_MVBB")
        aabb = BlenderExporterAPI.getBoxClass(mesh, options, boneNames, "MOD3_BoundingBox_AABB")
        if set(mvbb) != set(aabb):
            raise ValueError("Missing AABB/MVBB pair")
        return [BlenderExporterAPI.boxFromPair(bone, aabb[bone], mvbb[bone])
                for bone in sorted(aabb, key=lambda value: -1 if value == 255 else value)]

    @staticmethod
    def getRootEmpty():
        childless = []
        childed = []
        hiddenExplicitRoot = []
        explicitRoot = []
        rankings = {1:childless,2:childed,3:hiddenExplicitRoot,4:explicitRoot}
        for o in bpy.context.scene.objects:
            hierarchy = BlenderExporterAPI.isCandidateRoot(o)
            if hierarchy:
                rankings[hierarchy].append(o)
        return explicitRoot if explicitRoot else hiddenExplicitRoot if hiddenExplicitRoot else childed if childed else childless
    
    @staticmethod
    def isCandidateRoot(rootCandidate):
        if rootCandidate.type !="EMPTY" or rootCandidate.parent:
            return 0
        if "Type" in rootCandidate:
            if rootCandidate["Type"] == "MOD3_SkeletonRoot":
                if rootCandidate.hide_get():
                    return 3
                return 4
            else:
                return 0        
        if "boneFunction" in rootCandidate:
            return 0
        if rootCandidate.children:
            return any(("boneFunction" in child for child in rootCandidate.children))*2
        else:
            return 1

    @staticmethod
    def verifyLoad(source, accessPropertyName, errorHandler, storage, errorPropertyName = None):
        if errorPropertyName is None: errorPropertyName = accessPropertyName
        if accessPropertyName in source:
            prop = source[accessPropertyName]
            if hasattr(prop, "to_list"):
                prop = prop.to_list()
            elif hasattr(prop, "to_dict"):
                prop = prop.to_dict()
        else:
            prop = errorHandler.propertyMissing(errorPropertyName)
        if accessPropertyName in storage:
            errorHandler.propertyDuplicate(accessPropertyName, storage, prop)
        else:
            storage[accessPropertyName]=prop
        return
    
    @staticmethod
    def verifyBone(bone,errorHandler):        
        if "boneFunction" in bone:
            if type(bone["boneFunction"]) is not int:
                errorHandler.boneFunctionFailure(bone["name"],bone["boneFunction"])
                bone["boneFunction"] = errorHandler.propertyMissing("boneFunction")
    
    @staticmethod
    def hintCalc(child):
        if "indexHint" in child:
            hint = child["indexHint"] if child["indexHint"]>= 0 else 1024  
        else:
            hint = 1024
        return hint
    
    @staticmethod
    def recursiveEmptyDeconstruct(pix, current, storage, skeletonMap, errorHandler):
        for child in sorted(current.children,key = BlenderExporterAPI.hintCalc):
            bone = {"name":child.name}
            for prop in ["boneFunction","unkn2"]:
                BlenderExporterAPI.verifyLoad(child, prop, errorHandler, bone)
            BlenderExporterAPI.verifyBone(bone,errorHandler)
            #Check Child Constraint
            bone["child"] = BlenderExporterAPI.getTarget(child, errorHandler)
            if "boneFunction" not in child:
                raise ValueError("Non-bone child inside MOD3 skeleton: " + child.name)
            LMatrix= child.matrix_local.copy()
            if pix == 255:
                LMatrix = current.matrix_world @ LMatrix
            AMatrix= LMatrix.inverted() @ (storage[pix]["AMatrix"] if len(storage) and pix != 255  else Matrix.Identity(4))
            bone["x"], bone["y"], bone["z"] = (LMatrix[i][3] for i in range(3))
            bone["parentId"] = pix
            bone["length"]=math.sqrt(bone["x"]**2 +bone["y"]**2+ bone["z"]**2)
            cix = len(storage)
            storage.append({"bone":bone,"AMatrix":AMatrix,"LMatrix":LMatrix})
            skeletonMap[child.name] = cix,child
            BlenderExporterAPI.recursiveEmptyDeconstruct(cix, child, storage, skeletonMap, errorHandler)
       
    @staticmethod
    def getTarget(bone, errorHandler):
        return None if not (hasattr(bone,"MHW_Symmetric_Pair") and bone.MHW_Symmetric_Pair) else bone.MHW_Symmetric_Pair.name
        
    @staticmethod
    def parseMesh(basemesh, materials, skeletonMap, options):
        options.errorHandler.setMeshName(basemesh.name)
        with MeshClone(basemesh) as mesh:
            meshProp = {}
            for prop in ["shadowCast","visibleCondition","lod","weightDynamics","unkn3",
                         "blockLabel", "mapData", "intUnknown", "unknownIndex",
                        "material"]:
                BlenderExporterAPI.verifyLoad(mesh.data, prop, options.errorHandler, meshProp)
            if options.setHighestLoD:
                meshProp["lod"] = 0xFFFF
            if len({face.material_index for face in mesh.data.polygons}) > 1:
                raise ValueError("Split multiple polygon materials into separate meshes before export")
            meshProp["blocktype"] = BlenderExporterAPI.invertBlockLabel(meshProp["blockLabel"], options.errorHandler)
            groupName = lambda x: mesh.vertex_groups[x].name            
            loopNormals, loopTangents = BlenderExporterAPI.loopValues(mesh.data, options.splitNormals, options.errorHandler)
            uvMaps = BlenderExporterAPI.uvValues(mesh.data, options.errorHandler)
            colour = BlenderExporterAPI.colourValues(mesh, options.errorHandler)
            pymesh = []
            if len(mesh.data.vertices)>65535:
                options.errorHandler.vertexCountOverflow()
            for vertex in mesh.data.vertices:
                vert = {}
                vert["position"] = vertex.co.copy()
                bits = mesh.data.attributes.get("MOD3_weight_bits")
                vert["weightBits"] = bits.data[vertex.index].value if bits is not None else 0
                vert["weights"] = BlenderExporterAPI.weightHandling(vertex.groups, skeletonMap, groupName, options.errorHandler)
                #Normal Handling
                options.errorHandler.verifyLoadLoop("normal", vert, vertex, loopNormals, mesh)#vert["normal"] = loopNormals[vertex.index]
                #Tangent Handling
                options.errorHandler.verifyLoadLoop("tangent", vert, vertex, loopTangents, mesh)#vert["tangent"] = loopTangents[vertex.index]
                #UV Handling
                vert["uvs"] = [uvMap[vertex.index] if vertex.index in uvMap else options.errorHandler.missingUV(vertex.index, uvMap) for uvMap in uvMaps]
                if not len(vert["uvs"]):
                    options.errorHandler.uvLayersMissing(vert)
                if len(vert["uvs"])>4:
                    options.errorHandler.uvCountExceeded(vert)
                #Colour Handling if present
                if colour:
                    options.errorHandler.verifyLoadLoop("colour", vert, vertex, colour, mesh)
                pymesh.append(vert)
            faces = []
            for face in mesh.data.polygons:
                if len(face.vertices)>3:
                    faces += options.polyfaces(face)
                else:
                    faces.append({v:vert for v,vert in zip(["v1","v2","v3"],face.vertices)})
            if len(faces)>4294967295:
                options.errorHandler.faceCountOverflow()
            meshProp["materialIndexHint"] = basemesh.data.get("materialIndexHint", -1)
            meshProp["materialIdx"] = options.updateMaterials(meshProp,materials) 
            if options.calculateBoundingBox:
                boundingboxes = BlenderExporterAPI.calculateBoundingBoxes(mesh,options,skeletonMap)
            else:
                boundingboxes = BlenderExporterAPI.getLatticeBoxes(basemesh,options,skeletonMap)
        return {"mesh":pymesh, "faces":faces, "properties":meshProp, "meshname":basemesh.name,
                "boundingBoxes":boundingboxes}
    
    @staticmethod
    def invertBlockLabel(blockLabel, errorHandler):
        blockhash = generalhash(blockLabel) if blockLabel else None
        if blockhash and blockhash not in Mod3Vertex.blocklist:
            blockhash = errorHandler.uninversibleBlockLabel()  
        return blockhash
    
    @staticmethod
    def loopValues(mesh, useSplit, errorHandler):
        if not useSplit:
            mesh.normals_split_custom_set_from_vertices([vert.normal for vert in mesh.vertices])
        if not mesh.uv_layers:
            raise ValueError("A UV map is required to compute MOD3 tangents")
        mesh.calc_tangents(uvmap=mesh.uv_layers[0].name)
        normals = {}
        tangents = {}
        for loop in mesh.loops:
            vNormal = denormalize(mesh.corner_normals[loop.index].vector)
            vTangent = list(map(round, loop.tangent*127)) + [int(loop.bitangent_sign)*127]
            if loop.vertex_index in normals and \
                any([not (-1<=(c0-c1)<=1) for c0,c1 in zip(normals[loop.vertex_index],vNormal) ]):
                raise ValueError("Conflicting corner normals at vertex %d; split seams before export" % loop.vertex_index)
            elif loop.vertex_index in tangents and tangents[loop.vertex_index] != vTangent:
                raise ValueError("Conflicting corner tangents at vertex %d; split seams before export" % loop.vertex_index)
            else:
                normals[loop.vertex_index] = vNormal
                tangents[loop.vertex_index] = vTangent
        return normals, tangents
    
    @staticmethod    
    def uvValues(mesh, errorHandler):
        uvList = []
        for layer in mesh.uv_layers:
            uvMap = {}
            for loop,loopUV in zip(mesh.loops, layer.data): #.uv
                uvPoint = (loopUV.uv[0],1-loopUV.uv[1])
                if loop.vertex_index in uvMap and uvMap[loop.vertex_index] != uvPoint:
                    raise ValueError("Conflicting corner UVs; split seams before export")
                else:
                    uvMap[loop.vertex_index] = uvPoint
            uvList.append(uvMap)
        return uvList#int(bitangent_sign)*127
    
    @staticmethod
    def colourValues(mesh, errorHandler):
        layers = list(mesh.data.color_attributes)
        if not layers:
            return None
        if len(layers) > 1:
            raise ValueError("Only one MOD3 color attribute is supported")
        layer = layers[0]
        if layer.domain not in {'POINT', 'CORNER'}:
            raise ValueError("Unsupported color attribute domain")
        vertColor = {}
        for loop in mesh.data.loops:
            entry = layer.data[loop.vertex_index if layer.domain == 'POINT' else loop.index]
            values = entry.color_srgb
            if not all(math.isfinite(value) for value in values):
                raise ValueError("Non-finite vertex color")
            color = [round(max(0, min(1, value))*255) for value in values]
            if loop.vertex_index in vertColor and color != vertColor[loop.vertex_index]:
                raise ValueError("Conflicting corner colors; split seams before export")
            vertColor[loop.vertex_index] = color
        return vertColor


    @staticmethod    
    def weightHandling(weightGroups, skeletonMap, groupNameFunction, errorHandler):
        parsedGroups = [(groupNameFunction(group.group), group.weight) for group in weightGroups if errorHandler.testGroupFunction(groupNameFunction,group.group) ]
        validGroupName = lambda w: BlenderExporterAPI.validGroupName(w, skeletonMap, errorHandler)
        if any(not math.isfinite(value) for _, value in parsedGroups):
            raise ValueError("Non-finite vertex weight")
        weights = BufferedWeights([BufferedWeight(weightName,skeletonMap,weightVal) for weightName, weightVal in parsedGroups if validGroupName(weightName) and math.isfinite(weightVal)],errorHandler)
        if len(weights) > 8:
            raise ValueError("More than eight vertex weights cannot be represented")
        return weights
        #Handle Cases    
        #            preliminaryGroups = [(groupName(group.group),group.weight) for group in vertex.groups if BlenderExporterAPI.validGroupName(groupName(group.group), skeletonMap, options.errorHandler)]
        #     = BlenderExporterAPI.weightReorganize(preliminaryGroups, skeletonMap, options.errorHandler)
        
        
    weightCaptureGroup = BufferedWeight.weightCaptureGroup  
    @staticmethod
    def validGroupName(*args):
        return BlenderExporterAPI.getCannonicalGroupName(*args) is not None
        
    @staticmethod
    def getCannonicalGroupName(weightName,skeletonNames,errorHandler):
        if weightName in skeletonNames:
            return weightName
        match = re.match(BlenderExporterAPI.weightCaptureGroup,weightName)
        if match and match.group(1)+match.group(2) in skeletonNames:
            return match.group(1)+match.group(2)
        else:
            raise ValueError("Vertex group is not associated with an exported bone: " + weightName)