# Validation record — historical phases

Current scoped results (2026-10-04): [OPAQUE_BBOX_PRESERVATION.md](OPAQUE_BBOX_PRESERVATION.md). 18 binary/texture tests pass; both Blender versions pass API suites, 16 generated exports, 16 synthetic replays and five real byte-perfect replays. The complete real scene-fidelity runner exits nonzero due to body corner normals; arm has a degenerate-face limitation. The table below records the earlier pre-preservation phase and is retained as history.

| Check | Environment | Result |
|---|---|---|
| Binary / texture unit tests | Python 3.13, Windows | 13 passed |
| Half-float encoding | All 65,536 bit patterns, standard-library reference | Passed; NaN payloads are not promised unchanged |
| Full MOD3 parse/serialize | 14 known vertex block types | Passed |
| Add-on registration | Blender 4.4.3 / Python 3.11.11 | Repeated register/unregister and reload passed |
| Mesh/UV/custom normals/empty skeleton | Blender 4.4.3 | Passed; invalid normals rejected |
| Bounding geometry | Blender 4.4.3 | 0D/1D/2D/3D and translated containment passed |
| Export safety | Blender 4.4.3 | Failure preserves output; source transforms/data unchanged; UV conflicts and MOD3 Armature rejected |
| Shader nodes | Blender 4.4.3 | Named channels/sockets and image color spaces passed |
| Real Blender operator round-trip | Blender 4.4.3 | 16 synthetic complete files passed, including four/eight-weight high flags |
| User MOD3 import/round-trip | Blender 4.4.3 and 5.2.2 | Current branch rejects all five before mesh creation; old 4.4.3 plugin imports geometry; no round-trip completed |
| User MRL3 parser | Python 3.13 and Blender 5.2.2 Python 3.13.13 | 3 passed, each 5 materials / 12 textures |
| Blender 5.2 runtime | Blender 5.2.2 LTS / Python 3.13.13 | Registration, API/safety/material and synthetic tests PASS; five real MOD3 files fail at bbox association |
| EXE texture conversion | Not executed | NOT TESTED |
| In-game use / complex edited production scene | Not available | NOT TESTED |

All 16 successful cases have no original/A semantic changes; A/B semantic equality and binary equality excluding creationDate bytes 40:48 both passed. The semantic comparator covers header fields, float/byte sections, global bounds, group/material tables, skeleton hierarchy/index/matrices/remap, mesh properties (including material IDs and LOD), vertex serialized attributes (positions, normals, UV, colors and weights), faces, per-mesh bounds, and trailing bytes. It does not prove correctness for unknown block types or unknown game semantics. Fixtures are generated MOD3 files consumed by real bpy import/export operators, not mock Blender objects; nevertheless they are not original game files.

## Real sample failure evidence

| Sample | Mesh bbox references | Table count | Outcome |
|---|---|---|---|
| arm | 0 | 23 | Explicit rejection |
| body | 60 | 23 | Explicit rejection |
| helm | 12 | 195 | Explicit rejection |
| leg | 12 | 195 | Explicit rejection |
| waist | 0 | 23 | Explicit rejection |

The suite correctly exits nonzero for these failures. A bbox mismatch under the current parser is not evidence that a user asset is universally invalid. It may represent a format variant or previously tolerated inconsistency. Do not remove the check merely to get a green result. Confirm mapping semantics and add a real regression before enabling it.

Full logs and JSON are under the workspace sibling `audit-artifacts/` (excluded from repository and distribution); assets remain at the user's supplied directory. No game files are committed or downloaded.

## Blender 5.2 static and runtime checks

Official source: [Principled declarations](https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/nodes/shader/nodes/node_shader_bsdf_principled.cc), [Color nodes](https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/nodes/shader/nodes/node_shader_sepcomb_color.cc), [mesh RNA](https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/makesrna/intern/rna_mesh.cc), [dependency versions](https://github.com/blender/blender/blob/blender-v5.2-release/build_files/build_environment/cmake/versions.cmake). Named Principled inputs and Color RGB channels were checked; bundled Python version is 3.13.13 in that release branch. Blender 5.2.2 is now installed and the documented headless test suites ran successfully on synthetic data. They are not a real-model 5.2 pass: the five user MOD3 files are still rejected at the unresolved bbox association check. See [second-stage evidence](SECOND_STAGE_BBOX_AND_BLENDER52.md).


## Blender 5.2.2 update

Blender 5.2.2 LTS / Python 3.13.13 runtime registration, Import/Export operators, five API/safety/material scripts, 13 binary/MRL tests and all 16 synthetic round-trips passed. Three user MRL3 parsed (5 materials, 12 textures each). The five user MOD3 samples still fail the new per-mesh bbox count invariant; the old 4.4.3 add-on imported their geometry and stored the 144-byte records as opaque `MeshProperty` scene keys. Upstream's parser silently assigns only available records when counts mismatch. See [the three-way comparison and exact offsets](SECOND_STAGE_BBOX_AND_BLENDER52.md).

The material test reports a Blender 5.2 deprecation warning for `Material.use_nodes`; it remains functional in 5.2 but is expected to be removed in Blender 6.0. Texture conversion and game behavior remain untested.
