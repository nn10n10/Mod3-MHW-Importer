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
- Guard tests cover 0+0/23, 0+60/23, 12/195, duplicate bones, edited positions/topology/weights/order/identity/count/LOD/UV/colors/normals, bone hierarchy/index/rest/pose, transforms/modifiers/instancing, unknown properties, damaged/missing baseline and incomplete imports. Synthetic save/close/reopen succeeds in separate processes in both versions; editing reopened geometry refuses export. Blender 5.2 additionally passes real-model save/close/reopen with 195 records.
- No converters executed, no assets downloaded, no private asset or `.blend` committed.

Real-file results are identical on both tested versions:

| Sample | Meshes | Bones | Vertices | Faces | Global records | Source=A=B full bytes | Scene normals |
|---|---:|---:|---:|---:|---:|---|---|
| arm | 2 | 135 | 9,078 | 11,972 | 23 | PASS | PARTIAL: one zero-area corner mismatch |
| body | 2 | 135 | 8,767 | 13,669 | 23 | PASS | FAIL: four non-degenerate corner mismatches |
| helm | 1 | 90 | 8,566 | 13,675 | 195 | PASS | PASS |
| leg | 1 | 90 | 8,566 | 13,675 | 195 | PASS | PASS |
| wst | 1 | 58 | 994 | 1,799 | 23 | PASS | PASS |

Global raw table, full original mesh headers and byte 41 are explicitly compared. Whole-file equality also proves parsed positions/normals/UV/colors/weights/skeleton/materials/LOD/bounds/header fields unchanged; no timestamp exclusion is needed for replay. Scene checks independently compare geometry, hierarchy/functions, weights and UV/colors against the existing import representation. Slash's representation of an implicit negative final weight is not a claim that Blender displays raw signed weights literally.

## New finding M-21: real scene normal fidelity

Body has four mismatches on two nonzero-area polygons (~0.010880956 and ~0.010880955). One source direction is `[0, 0.333984524, -0.942578554]`; Blender reports approximately `[-0.000016338, 0.003574392, 0.001251254]`. The root cause is not determined here. Arm has one mismatch on a zero-area polygon. Both reproduce in 4.4.3 and 5.2.2. This implementation does not change the normal API or weaken the comparison threshold.

The runner completes all file-preservation checks, records `preservation_status = PASS` independently, marks body's scene-normal check FAIL and then exits nonzero. The complete real-file suite is therefore **not all PASS**. Original packed normals remain byte-perfect on replay; edited unresolved scenes cannot invoke reconstruction. This finding is a scene-fidelity issue, not newly accepted bbox ownership or demonstrated corruption of exported replay files.

## Feature matrix

| Feature | 4.4.3 | 5.2.2 | Evidence / boundary |
|---|---|---|---|
| Registration / menus | PASS | PASS | Existing runtime suite |
| Physical MOD3 parsing | PASS | PASS | All five samples and synthetic tests |
| Mesh import | PASS | PASS | Scene topology/positions/counts checked |
| Skeleton import | PASS | PASS | Real EmptyTree indices/hierarchy/functions checked; Armature synthetic |
| Weights / UV / colors | PASS | PASS | Raw file preservation plus scene representation comparisons |
| Normals | PARTIAL | PARTIAL | Body non-degenerate scene check FAIL; raw exported bytes PASS |
| Global bbox preservation | PASS | PASS | Raw records/order/full source exact |
| Bbox ownership / editable reconstruction | UNTESTED | UNTESTED | Unknown; no mapping inferred, edits refused |
| MRL3 parsing | PASS | PASS | Earlier three real files; unchanged by this patch |
| Material node construction | PASS | PASS | Existing synthetic runtime suite |
| Texture conversion | UNTESTED | UNTESTED | EXEs not run |
| MOD3 generated export | PARTIAL | PARTIAL | 16 synthetic reconstructions PASS; real edited reconstruction blocked |
| Synthetic operator round-trip | PASS | PASS | 16 replay cases; encoder tested separately |
| Real unchanged-file round-trip | PASS | PASS | Five complete binary-identical source/A/B files |
| Game-side validation | UNTESTED | UNTESTED | No game execution |

## PR gates and remaining work

Registration, synthetic encoder/replay, real import, unchanged real semantic stability, private-asset exclusion and accurate README gates pass for this scoped preservation path. No known newly introduced HIGH/CRITICAL silent-write issue was observed in it; this is not certification of arbitrary reconstructed scenes. **NOT PR-ready:** M-21 remains an explicit failing real scene-fidelity test, and the new fingerprint/guard policy needs independent final review. Ownership is still uncertain; editable real-file export remains intentionally unsupported until independently justified.

Next work is a separate normal-fidelity investigation/review and final correctness review of this diff. Converter/game checks and redistribution-license questions remain release limitations. No push or PR was performed. Historical second-stage findings are retained in SECOND_STAGE_BBOX_AND_BLENDER52.md; this report supersedes its current-status statements.
