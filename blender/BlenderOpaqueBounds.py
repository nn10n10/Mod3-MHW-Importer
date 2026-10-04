"""Fail-closed source replay for imported bbox tables with unknown ownership.

The baseline is a content-addressed Text datablock, packed in the .blend file.
Custom properties are only references/guards, never the baseline itself. This
protects against ordinary edits and damaged metadata, not deliberate removal of
every guard or fabrication of a new baseline by arbitrary Python code.
"""
import base64
import hashlib
import json
import uuid
import zlib

import bpy

PREFIX = ".MOD3Opaque."
LINK = PREFIX + "baseline"
GUARD = PREFIX + "ownership"
IDENTITY = PREFIX + "identity"
_baselines = {}  # immutable strings, not mutable scene properties


def _name(encoded):
    # Blender 4.4 ID names allow only 63 bytes. A 160-bit content address fits;
    # the geometry fingerprint still uses the full SHA-256 digest.
    return PREFIX + hashlib.sha256(encoded.encode('utf-8')).hexdigest()[:40]


def _value(value):
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return value.hex()  # don't hide small changes with rounding
    if isinstance(value, bpy.types.ID):
        return [value.bl_rna.identifier, value.name_full,
                value.library.filepath if value.library else None]
    if hasattr(value, "to_dict"):
        return _value(value.to_dict())
    if isinstance(value, dict):
        return {str(key): _value(val) for key, val in value.items()}
    return [_value(item) for item in value]


def _properties(owner):
    return {key: _value(owner[key]) for key in owner.keys()
            if not key.startswith(PREFIX) and key != 'MHW_Symmetric_Pair'}


def _rna(owner):
    # Only scalar/array settings and ID references; nested collections are
    # explicitly handled below. Unreadable settings fail closed.
    result = {"rna": owner.bl_rna.identifier}
    for prop in owner.bl_rna.properties:
        if prop.identifier == "rna_type" or prop.type == 'COLLECTION' or prop.is_readonly:
            continue
        value = getattr(owner, prop.identifier)
        if prop.type == 'POINTER' and value is not None and not isinstance(value, bpy.types.ID):
            raise ValueError("Opaque export cannot snapshot setting: " + prop.identifier)
        result[prop.identifier] = _value(value)
    return result


def _settings(owner):
    for prop in owner.bl_rna.properties:
        if prop.type == 'COLLECTION' and len(getattr(owner, prop.identifier)):
            raise ValueError("Opaque preservation cannot verify nested settings: " + prop.identifier)
    return _rna(owner)


def _mesh(mesh):
    if mesh.shape_keys or mesh.animation_data:
        raise ValueError("Opaque bbox preservation does not support animated mesh data or shape keys")
    attrs = []
    for attr in mesh.attributes:
        # Selection is a UI operation, not a MOD3 edit.
        if attr.name.startswith('.select'):
            continue
        attrs.append([attr.name, attr.domain, attr.data_type,
                      [_rna(item) for item in attr.data]])
    return {"vertices": [[_value(v.co), [[g.group, _value(g.weight)] for g in v.groups]] for v in mesh.vertices],
            "edges": [list(e.vertices) for e in mesh.edges],
            "faces": [[list(p.vertices), p.material_index, p.use_smooth] for p in mesh.polygons],
            "loops": [[loop.vertex_index, loop.edge_index] for loop in mesh.loops],
            "normals": [_value(n.vector) for n in mesh.corner_normals],
            "custom_normals": mesh.has_custom_normals, "attributes": attrs,
            "materials": [_value(mat) for mat in mesh.materials]}


def _material(mat):
    if mat.animation_data or (mat.node_tree and mat.node_tree.animation_data):
        raise ValueError("Opaque preservation does not support animated materials")
    result = {"name": mat.name_full, "properties": _properties(mat),
              "settings": _rna(mat)}
    if mat.node_tree:
        nodes = []
        for node in mat.node_tree.nodes:
            nodes.append([_rna(node), _properties(node),
                          [[sock.identifier, _value(sock.default_value) if hasattr(sock, 'default_value') else None]
                           for sock in (*node.inputs, *node.outputs)]])
            if node.type == 'GROUP':
                raise ValueError("Opaque preservation does not support nested material node groups")
        result["nodes"] = nodes
        result["links"] = [[link.from_node.name, link.from_socket.identifier,
                            link.to_node.name, link.to_socket.identifier] for link in mat.node_tree.links]
    return result


def fingerprint(scene):
    bpy.context.view_layer.update()
    objects = []
    materials = set()
    for obj in scene.objects:
        if obj.animation_data or obj.type not in {'MESH', 'EMPTY', 'ARMATURE', 'LATTICE'}:
            raise ValueError("Opaque preservation does not support animated/unsupported scene objects")
        if obj.instance_type != 'NONE' or obj.instance_collection is not None:
            raise ValueError("Opaque preservation does not support object/collection instancing")
        state = {"identity": obj.get(IDENTITY), "name": obj.name_full, "type": obj.type,
                 "parent": _value(obj.parent), "parent_type": obj.parent_type, "parent_bone": obj.parent_bone,
                 "world": _value(obj.matrix_world), "local": _value(obj.matrix_local),
                 "parent_inverse": _value(obj.matrix_parent_inverse),
                 "properties": _properties(obj), "collections": sorted(c.name_full for c in obj.users_collection),
                 "groups": [group.name for group in obj.vertex_groups],
                 "modifiers": [_settings(mod) for mod in obj.modifiers],
                 "constraints": [_settings(con) for con in obj.constraints],
                 "hidden": [obj.hide_viewport, obj.hide_render, obj.hide_get()],
                 "symmetric_pair": _value(getattr(obj, 'MHW_Symmetric_Pair', None))}
        if obj.data:
            state["data"] = [_value(obj.data), _properties(obj.data)]
        if obj.type == 'MESH':
            state["mesh"] = _mesh(obj.data)
            materials.update(mat for mat in obj.data.materials if mat is not None)
        elif obj.type == 'ARMATURE':
            if obj.data.animation_data:
                raise ValueError("Opaque preservation does not support animated armatures")
            state["bones"] = [[bone.name, bone.parent.name if bone.parent else None,
                               _value(bone.matrix_local), _value(bone.head_local), _value(bone.tail_local),
                               bone.use_connect, bone.use_deform, bone.inherit_scale, _properties(bone)]
                              for bone in obj.data.bones]
            state["pose"] = [[bone.name, _value(bone.matrix_basis), [_settings(c) for c in bone.constraints]]
                             for bone in obj.pose.bones]
        elif obj.type == 'LATTICE':
            state["lattice"] = [_value(point.co_deform) for point in obj.data.points]
        objects.append(state)
    data = {"scene": _properties(scene), "objects": objects,
            "materials": [_material(mat) for mat in sorted(materials, key=lambda m: m.name_full)]}
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def capture(source, context, complete):
    scene = bpy.context.scene
    scene[GUARD] = "unresolved"
    # Establish the guard before any snapshot work can fail.
    scene[LINK] = "missing"
    for obj in scene.objects:
        obj[IDENTITY] = uuid.uuid4().hex
    payload = {"version": 1, "complete": complete, "source": base64.b64encode(source).decode('ascii')}
    try:
        payload["fingerprint"] = fingerprint(scene)
    except (ValueError, TypeError, RuntimeError) as exc:
        # Inability to prove safe export must never discard the source table.
        payload.update(complete=False, fingerprint=None, blocked_reason=str(exc))
        print("MOD3: original bytes retained; opaque export blocked: %s" % exc)
    encoded = base64.b64encode(zlib.compress(json.dumps(payload, sort_keys=True).encode('utf-8'))).decode('ascii')
    name = _name(encoded)
    text = bpy.data.texts.get(name) or bpy.data.texts.new(name)
    text.clear()
    text.write(encoded)
    text.use_fake_user = True
    scene[LINK] = text.name
    for obj in context.meshes:
        obj[GUARD] = "unresolved"
    _baselines[name] = encoded


def preserved_binary(options):
    scene = bpy.context.scene
    marked = any(obj.get(GUARD) == 'unresolved' for obj in scene.objects)
    if GUARD not in scene and LINK not in scene and not marked:
        return None
    name = scene.get(LINK, '')
    text = bpy.data.texts.get(name)
    if not text or not name.startswith(PREFIX):
        raise ValueError("Unresolved bbox export refused: original baseline is missing")
    encoded = text.as_string()
    if name != _name(encoded) or (
            name in _baselines and _baselines[name] != encoded):
        raise ValueError("Unresolved bbox export refused: baseline metadata was modified")
    try:
        payload = json.loads(zlib.decompress(base64.b64decode(encoded, validate=True)))
        source = base64.b64decode(payload['source'], validate=True)
    except (ValueError, KeyError, zlib.error) as exc:
        raise ValueError("Unresolved bbox export refused: damaged baseline") from exc
    if payload.get('version') != 1 or not payload.get('complete'):
        raise ValueError("Unresolved bbox export refused: import omitted meshes, LODs, skeleton or weight information")
    if options.setHighestLoD or not options.exportHidden or not options.splitNormals:
        raise ValueError("Unresolved bbox export requires unchanged LOD, all meshes and custom normals")
    try:
        current = fingerprint(scene)
    except (TypeError, RuntimeError) as exc:
        raise ValueError("Unresolved bbox export refused: scene settings cannot be verified") from exc
    if current != payload['fingerprint']:
        raise ValueError("Unresolved bbox export refused: scene differs from its immutable import baseline")
    print("MOD3: unresolved bbox ownership; replaying complete original bytes. No bounds or weights are recalculated.")
    return source
