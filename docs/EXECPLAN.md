# Execution plan: conservative Blender 5.2 compatibility PR

## Goal and scope

Prepare `blender-5.2-compat` for an upstream contribution supporting Blender 5.2 import and safe unchanged-file round-trip. Bounding-box (bbox) ownership in real MOD3 files remains unknown. Do not infer it or attempt further reverse engineering without new evidence. Real imported files may be exported only by exact replay of the unchanged, complete source; edits that could invalidate opaque data must fail before writing. Document the limits. Do not push or create a PR without explicit authorization.

## Current evidence

- Branch: `blender-5.2-compat`; final-review baseline: `4855dc1`.
- Blender 4.4.3 / Python 3.11.11 and Blender 5.2.2 LTS / Python 3.13.13 pass registration, importer/API, bounds, export-safety and material suites, plus 16 generated-export cases.
- On each Blender version, 31 opaque-preservation/guard cases pass (including the optional real save/reopen check) and 21 round-trip cases pass. Five private real MOD3 source -> A -> B outputs are full-file byte-identical; checks include global bbox bytes and original mesh headers/byte 41.
- All five real files import in both tested Blender versions. Body and three other samples pass scene-normal checks. Arm retains one scene-normal mismatch on a zero-area face (PARTIAL); its opaque source replay remains byte-perfect.
- The ordinary Python suite passes 18 tests. Blender 5.2's material suite reports the existing `Material.use_nodes` deprecation warning.
- No game assets are committed. TEX conversion and game-side validation were not run. The upstream repository has no top-level license declaration.

## Work sequence and status

1. **Set the conservative PR contract — complete.** Import files when the global bbox table is physically valid; preserve its raw ordered records and unknown mesh fields; replay only unchanged complete imports; reject uncertain edited exports. Unknown ownership remains unresolved, with no guessing or silent truncation.
2. **Implement and regression-test — complete.** Opaque metadata is preserved for serialization. Blender scene fingerprints gate exact full-source replay; edits, incomplete imports or damaged baselines refuse export before replacement. The targeted body normal issue is fixed without changing MOD3 format data; the arm degenerate-face mismatch remains documented.
3. **Runtime and real-file validation — complete.** Both Blender versions pass the suites and five real source/A/B replay runs listed above. Tests retain the arm `PARTIAL` result; thresholds were not relaxed.
4. **Focused review and documentation reconciliation — complete.** Reviewed the export guard and pre-write refusal tests. README, validation record, opaque-preservation report, fix status and PR draft now agree on scope, evidence and limitations. Historical pre-preservation rejection results are explicitly labeled historical. No bbox ownership inference was attempted.
5. **Readiness and repository hygiene — complete for the stated scope.** The branch is PR-ready for conservative Blender 5.2 import and unchanged real-file preservation, not for edited real MOD3 reconstruction. `git diff --check` and the ordinary Python suite pass. The final review fix, regression and updated evidence form a separate local commit; existing logical history is preserved. No push or PR has been made.

## Explicit limitations

The arm sample has one zero-area-face corner-normal mismatch. Edited real-file reconstruction is disabled while bbox ownership is unknown. TEX conversion, game-side appearance, and upstream license clarification remain unverified or outstanding. These are disclosed boundaries; none is represented as tested functionality. See [OPAQUE_BBOX_PRESERVATION.md](OPAQUE_BBOX_PRESERVATION.md) for the evidence and detailed feature matrix.

## Final upstream review

**Complete.** Upstream master remains `364c260` (verified with `git ls-remote`). Scope is unchanged. Found and reproduced H-21: interrupted unresolved imports left unguarded scene objects; removing the unfinished mesh allowed reconstruction and target replacement. Fixed the root cause by capturing an incomplete baseline in `finally`, establishing the guard before snapshot work and preserving the original import exception. Added a real Blender regression verifying source retention, export refusal and unchanged destination.

Reran 18 ordinary Python tests and, on each Blender version, registration/API/bounds/export-safety/material tests, 16 generated-export cases, 31 opaque preservation/guard cases and 21 synthetic/real round-trips: all pass with the documented arm normal PARTIAL. Directly compared all five source/A/B complete files as well as the runner's raw bbox/header checks. Save/reopen children now use `--factory-startup`; the previously installed user add-on no longer contaminates these tests. Only the expected negative-test import traceback/refusal and the documented 5.2 `Material.use_nodes` deprecation remain. Local logs/results are outside Git under `../final-pr-review-44/` and `../final-pr-review-52/`.

Reviewed the contribution diff, logical commits, documentation boundaries and asset exclusion; no further release-blocking issue was found in the stated scope. The branch is ready for a user-authorized push to a personal fork. No personal fork remote has been configured and no push or PR was performed.
