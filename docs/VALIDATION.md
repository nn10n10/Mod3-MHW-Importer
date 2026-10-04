# Validation record

## Current conservative-scope results (2026-10-04)

The authoritative current report is [OPAQUE_BBOX_PRESERVATION.md](OPAQUE_BBOX_PRESERVATION.md). The five private real files import in Blender 4.4.3 and 5.2.2; unchanged source -> A -> B replay is byte-identical, including bbox records and original mesh headers. Both runtimes pass the current API/safety/material tests, 16 generated-export cases, 31 opaque preservation/guard cases (including real save/reopen) and 21 round-trip cases. The 18 ordinary Python tests pass. Scene normals are PARTIAL only for one zero-area-face corner in arm; the other four real samples pass. These results establish unchanged-file preservation, not edited real-file reconstruction or game-side correctness.

The sections below are historical records from before opaque bbox preservation was implemented. Their statements that real files were rejected describe that earlier revision and are superseded by the current report linked above.

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
| User MOD3 import/round-trip | Blender 4.4.3 and 5.2.2 | HISTORICAL: the then-current branch rejected all five before mesh creation; superseded by opaque-preservation implementation and current results above |
| User MRL3 parser | Python 3.13 and Blender 5.2.2 Python 3.13.13 | 3 passed, each 5 materials / 12 textures |
| Blender 5.2 runtime | Blender 5.2.2 LTS / Python 3.13.13 | HISTORICAL: registration/API/safety/material and synthetic tests passed; real import had not yet been enabled |
| EXE texture conversion | Not executed | NOT TESTED |
| In-game use / complex edited production scene | Not available | NOT TESTED |

All 16 successful cases have no original/A semantic changes; A/B semantic equality and binary equality excluding creationDate bytes 40:48 both passed. The semantic comparator covers header fields, float/byte sections, global bounds, group/material tables, skeleton hierarchy/index/matrices/remap, mesh properties (including material IDs and LOD), vertex serialized attributes (positions, normals, UV, colors and weights), faces, per-mesh bounds, and trailing bytes. It does not prove correctness for unknown block types or unknown game semantics. Fixtures are generated MOD3 files consumed by real bpy import/export operators, not mock Blender objects; nevertheless they are not original game files.

## Historical: first-pass real sample rejection evidence

This records the pre-preservation parser failure only. It does not describe current behavior; see the current results at the top of this file and in [OPAQUE_BBOX_PRESERVATION.md](OPAQUE_BBOX_PRESERVATION.md).

| Sample | Mesh bbox references | Table count | Outcome |
|---|---|---|---|
| arm | 0 | 23 | Explicit rejection |
| body | 60 | 23 | Explicit rejection |
| helm | 12 | 195 | Explicit rejection |
| leg | 12 | 195 | Explicit rejection |
| waist | 0 | 23 | Explicit rejection |

In that historical revision the suite correctly exited nonzero for these failures. A bbox mismatch under that parser was not evidence that a user asset was universally invalid. The safe response was later implemented: preserve physically valid records opaquely and fail closed on uncertain edits, without assigning ownership.

Full logs and JSON are under the workspace sibling `audit-artifacts/` (excluded from repository and distribution); assets remain at the user's supplied directory. No game files are committed or downloaded.

## Historical: initial Blender 5.2 static and runtime checks

Official source: [Principled declarations](https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/nodes/shader/nodes/node_shader_bsdf_principled.cc), [Color nodes](https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/nodes/shader/nodes/node_shader_sepcomb_color.cc), [mesh RNA](https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/makesrna/intern/rna_mesh.cc), [dependency versions](https://github.com/blender/blender/blob/blender-v5.2-release/build_files/build_environment/cmake/versions.cmake). Named Principled inputs and Color RGB channels were checked; bundled Python version is 3.13.13 in that release branch. This is the initial static/runtime check record; subsequent real-file validation is summarized at the top of this file.


## Historical: Blender 5.2.2 update before opaque preservation

This pre-preservation report recorded the then-current failure of five user MOD3 samples at the per-mesh bbox invariant. That failure was later addressed by preserving valid global tables opaquely and guarding export; consult [the current report](OPAQUE_BBOX_PRESERVATION.md) for the completed results.

The material test reports a Blender 5.2 deprecation warning for `Material.use_nodes`; it remains functional in 5.2 but is expected to be removed in Blender 6.0. Texture conversion and game behavior remain untested.
