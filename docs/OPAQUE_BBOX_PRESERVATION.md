# Unresolved bbox compatibility — 2026-10-04

## Scope and representation

This implements the reviewer-approved preservation architecture, not a new ownership theory. A nonempty parsed table is `ownershipState = "unresolved"`, `ownershipMapping = None`; matching byte-41 totals are not proof. A zero table with zero mesh bytes is `empty`. Global records remain an ordered list, never a dictionary keyed by bone index. Mesh `BoundingBoxes` are empty unless explicitly supplied by a synthetic scene builder; parsed records are never sliced into them.

`Mod3BoundingBoxes.rawRecords` retains immutable record bytes; decoded records are a view. Serialization refuses modifications to that view instead of silently rewriting the raw table. Each parsed mesh retains its full original 80-byte `rawHeader`; attempts to rewrite byte 41 through parsed-model serialization fail. Parsed unresolved `Mod3.serialize()` also checks an immutable post-parse serialization baseline, refuses any detected edits and returns the original full file when unchanged, preventing a lower-level caller from bypassing Blender guards. Physical table bounds are checked against the vertex-section start before allocating records; the end must match that boundary exactly. Unknown padding/layout variants remain unsupported.

## Export architecture and baseline

The safe opaque path writes the entire original source file, not a newly assembled model. This preserves all unknown fields, alignment, offsets, padding, record order and creation time without assuming unknown references can be relocated. There is no automatic bbox recalculation or override for edited unresolved scenes.

The baseline contains compressed/base64 source bytes, a complete-import flag, schema version and a full SHA-256 scene fingerprint. It is saved as a fake-user Text datablock. Its name is a 160-bit content address that fits Blender 4.4's 63-byte ID-name limit. Its content is checked on each export; in-process immutable strings provide another check. Editable custom properties are links/guards, not the original source or comparison baseline. The original file may disappear after import without invalidating replay.

The fingerprint includes object identities/order/names, mesh data identity, vertices/topology/edges/loops, positions, normals, UV/color/custom attributes, groups and weights, material slots/settings/node links/socket values, object and parent matrices, collection membership, visibility, LOD/other custom metadata, bone indices/hierarchy/rest matrices/head/tail/deform settings and pose matrices. UI selection is excluded. Unsupported animation, shape keys, instancing or nested settings fail closed. Registered symmetric-pair pointers are fingerprinted explicitly; their lazily initialized ID-property backing is excluded to avoid a false change on Blender 4.4.

If scene fingerprinting cannot prove safety, a blocked snapshot still retains every source byte and records the reason. Failure to write the snapshot leaves export guards in place and reports the error. Mesh/LOD filtering, missing skeleton, lossy weight modes, preexisting scene objects or missing mesh parts make the baseline incomplete. Omit-unused-weights is disabled for unresolved imports. Scene-header/bbox display options cannot discard the baseline. Missing or tampered metadata blocks export. This is protection against ordinary edits and damaged metadata, not arbitrary scripts deliberately fabricating a new baseline or stripping every guard.

All checks finish before atomic output writing. Refusal tests confirm existing destination bytes and absence of leaked temporary files. The raw replay path is deliberately more restrictive than necessary; it accepts no edits requiring assumptions about bbox dependencies.

## Test results

- 18 ordinary-Python tests PASS; also PASS inside Blender 5.2.2 Python 3.13.13.
- Five existing Blender API/safety/material suites PASS in Blender 4.4.3 and 5.2.2.
- Separate generated-export test: 16 synthetic scenes with explicitly supplied fixture ownership reconstruct byte-identically except creationDate in both versions. This exercises the actual encoder, not replay, without inferring ownership from input byte 41.
- Opaque replay: 16 synthetic operator source→A→B cases PASS in both versions.
- Guard tests cover 0+0/23, 0+60/23, 12/195, duplicate bones, edited positions/topology/weights/order/identity/count/LOD/UV/colors/normals, bone hierarchy/index/rest/pose, transforms/modifiers/instancing, unknown properties, damaged/missing baseline and incomplete or interrupted imports. The suite has 30 default cases; both versions pass 31 cases when the optional 195-record real-model save/close/reopen test is included. Synthetic and real save/reopen succeed in separate processes; editing reopened geometry refuses export.
- No converters executed, no assets downloaded, no private asset or `.blend` committed.

Real-file results are identical on both tested versions:

| Sample | Meshes | Bones | Vertices | Faces | Global records | Source=A=B full bytes | Scene normals |
|---|---:|---:|---:|---:|---:|---|---|
| arm | 2 | 135 | 9,078 | 11,972 | 23 | PASS | PARTIAL: one zero-area corner mismatch |
| body | 2 | 135 | 8,767 | 13,669 | 23 | PASS | PASS: opposing duplicate-face pairs isolated with sharp edges |
| helm | 1 | 90 | 8,566 | 13,675 | 195 | PASS | PASS |
| leg | 1 | 90 | 8,566 | 13,675 | 195 | PASS | PASS |
| wst | 1 | 58 | 994 | 1,799 | 23 | PASS | PASS |

These are five local file paths, not five unique binary fixtures: helm and leg have identical source bytes.

Global raw table, full original mesh headers and byte 41 are explicitly compared. Whole-file equality also proves parsed positions/normals/UV/colors/weights/skeleton/materials/LOD/bounds/header fields unchanged; no timestamp exclusion is needed for replay. Scene checks independently compare geometry, hierarchy/functions, weights and UV/colors against the existing import representation. Slash's representation of an implicit negative final weight is not a claim that Blender displays raw signed weights literally.

## M-21: real scene normal fidelity

Body's four mismatches were on two coincident triangles with exactly reversed winding and shared vertices. Blender 4.4.3 and 5.2.2 both reproduce the issue in a minimal mesh: the shared split-normal fan cannot represent the supplied loop normals, while marking the pair's perimeter sharp makes every corner match. The importer now detects only triangle pairs with the same three vertex indices, exactly two faces for that key, and reversed directed edges; it marks those perimeter edges sharp before applying custom normals. The real body sample then has zero normal mismatches. The threshold is unchanged.

Arm still has one corner-normal mismatch on a zero-area polygon in both versions. Marking all edges around zero-area polygons sharp made the problem worse in a probe, so the importer does not apply that broader workaround. The real runner reports arm scene normals as `PARTIAL`, with no nondegenerate mismatches. All five source → A → B runs preserve complete source bytes, raw bbox table and byte-41 mesh fields; geometry, skeleton, weights, UV/color and normal comparisons otherwise match. The runner exits successfully while retaining the arm PARTIAL status. Original packed normals remain byte-perfect on replay; edited unresolved scenes cannot invoke reconstruction.

## Feature matrix

| Feature | 4.4.3 | 5.2.2 | Evidence / boundary |
|---|---|---|---|
| Registration / menus | PASS | PASS | Existing runtime suite |
| Physical MOD3 parsing | PASS | PASS | All five samples and synthetic tests |
| Mesh import | PASS | PASS | Scene topology/positions/counts checked |
| Skeleton import | PASS | PASS | Real EmptyTree indices/hierarchy/functions checked; Armature synthetic |
| Weights / UV / colors | PASS | PASS | Raw file preservation plus scene representation comparisons |
| Normals | PARTIAL | PARTIAL | Body PASS after opposing-face edge split; arm has one zero-area-face mismatch; raw exported bytes PASS |
| Global bbox preservation | PASS | PASS | Raw records/order/full source exact |
| Bbox ownership / editable reconstruction | UNTESTED | UNTESTED | Unknown; no mapping inferred, edits refused |
| MRL3 parsing | PASS | PASS | Earlier three real files; unchanged by this patch |
| Material node construction | PASS | PASS | Existing synthetic runtime suite |
| Texture conversion | UNTESTED | UNTESTED | EXEs not run |
| MOD3 generated export | PARTIAL | PARTIAL | 16 synthetic reconstructions PASS; real edited reconstruction blocked |
| Synthetic operator round-trip | PASS | PASS | 16 replay cases; encoder tested separately |
| Real unchanged-file round-trip | PASS | PASS | Five complete binary-identical source/A/B files |
| Game-side validation | UNTESTED | UNTESTED | No game execution |

## H-21: interrupted-import export bypass (fixed)

The final review reproduced a HIGH-severity failure path on Blender 5.2.2. A synthetic two-mesh source with valid global bbox layout and a zero-length normal in its second mesh failed during scene construction. The old guard was created only after all import steps succeeded. Removing the unfinished mesh then allowed the remaining partial scene to reconstruct and replace an existing output file, discarding the unresolved global metadata.

Affected code: `mod3/Mod3ImporterLayer.py`, `Mod3ToModel.execute`, and the guard ordering in `blender/BlenderOpaqueBounds.py`, `capture`. Blender 4.4.3 uses the same exposed execution path; the pre-fix overwrite was directly reproduced on 5.2.2. Silent data loss was possible. Both versions now have a passing regression in `tests/blender_opaque_bounds.py` (`failed_import_partial_scene`).

Import execution now captures its baseline in `finally`; a failed import is always incomplete. Snapshot capture establishes the scene guard before assigning identities or fingerprinting. The original import exception propagates. The Blender regression asserts that all source bytes survive, then deletes the unfinished mesh and checks that export is refused, existing destination bytes are unchanged and no temporary output is leaked. Both tested Blender versions pass this regression. No ownership interpretation was changed.

Final test artifacts are outside the repository in workspace siblings `final-pr-review-44/` and `final-pr-review-52/`. Reopen subprocesses use factory startup so the user's separately installed add-on cannot replace operators or introduce shutdown errors. The deliberately invalid normal regression emits an expected import traceback; it is not a successful-import failure. The Blender 5.2 material deprecation warning remains documented.

## PR gates and remaining work

The conservative compatibility PR gates pass:

- **Blender 5.2 add-on registration:** PASS — repeated register/unregister/reload and operators.
- **Synthetic import/export round-trip:** PASS — 16 generated scenes and 16 opaque replay cases; 31 preservation/guard cases with optional real save/reopen.
- **Real MOD3 import:** PASS — all five local samples import on Blender 4.4.3 and 5.2.2.
- **Unchanged real-file round-trip:** PASS — source, A and B are byte-identical for all five samples; bbox records and raw mesh headers are checked.
- **Fail-closed edited export:** PASS — geometry, weights, bones, ordering, metadata, incomplete import, damaged baseline and save/reopen edits are refused before destination replacement.
- **No known HIGH/CRITICAL silent-write issue in the scoped path:** PASS — unresolved real-file edits do not reach reconstruction; unknown records are replayed only from the unchanged full source. Arbitrary scripts that remove or fabricate all guards are outside the documented threat model.
- **No private game assets committed / limitations documented:** PASS.

**PR-ready for this conservative compatibility scope; not a claim that edited real MOD3 reconstruction is supported.** The arm zero-area-face normal mismatch is documented as PARTIAL, and no threshold was relaxed. TEX conversion, game-side validation and upstream license clarification remain release/maintenance limitations. No push or PR was performed. Historical second-stage findings are retained in SECOND_STAGE_BBOX_AND_BLENDER52.md; this report supersedes its current-status statements.
