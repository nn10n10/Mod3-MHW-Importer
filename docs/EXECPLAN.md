# Active execution plan

Goal: resolve the outstanding real-file scene-normal mismatch, preserve the approved unresolved-bbox safety model, and complete evidence-based PR readiness checks. No push or PR.

## Current state

- Branch: `blender-5.2-compat`; baseline commit: `6b6dcb8`.
- Blender 4.4.3 and 5.2.2 LTS both pass registration, synthetic import/export and opaque-preservation suites.
- Five private real MOD3 files import and unchanged source → A → B replay is byte-identical in both versions.
- Initial scene-normal evidence isolated the four body mismatches to two coincident, oppositely wound triangle pairs; arm has one mismatch on a zero-area polygon. The comparison threshold is unchanged.
- Bbox ownership remains unresolved by design; edited real-file export remains blocked. Do not infer ownership or weaken export guards.

## Work sequence

1. **Reproduce and isolate scene-normal mismatch — complete** — the mismatched body loops are on coincident, opposite-winding triangles sharing vertices. Both Blender versions reproduce loss of custom corner normals in a minimal mesh; sharp perimeter edges restore them. A probe marking all edges around zero-area polygons worsened the arm result and was rejected.
2. **Make the smallest justified correction — implemented** — importer marks edges sharp only for exactly two coincident triangles with the same vertex set and reversed directed edges. A Blender regression checks the resulting full corner-normal direction and the sharp perimeter. No MOD3 encoding or threshold change.
3. **Run validation — complete** — all 18 Python tests pass. Registration, importer API, bounds, export safety, materials and 16 generated exports pass on Blender 4.4.3 / Python 3.11.11 and 5.2.2 LTS / Python 3.13.13; 29 opaque guard cases pass per version. All 21 real-runner cases pass per version, including five source → A → B exact-byte replays; body normals PASS and arm remains PARTIAL for one zero-area-face loop. No threshold was relaxed.
4. **Review and commit — complete** — reviewed the focused code/test/docs diff, ran `git diff --check`, staged only ten intended files (no private assets), and created local commit `30152be`.
5. **Final readiness — complete** — NOT PR-ready. Real-file edited export remains blocked because bbox ownership is unknown; arm has one zero-area-face scene-normal limitation; opaque baseline/guard needs independent review; TEX conversion, in-game validation and license status remain unresolved.

## Active step

No further implementation is safe without new format evidence or reviewer disposition. No push or PR was made. Reopen this plan when evidence becomes available or an explicit scope decision resolves the remaining blockers.
