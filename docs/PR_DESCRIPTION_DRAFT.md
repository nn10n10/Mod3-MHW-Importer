# Draft title

Add Blender 5.2 compatibility with safe unresolved MOD3 metadata preservation

# Draft description

This change prepares the legacy add-on for Blender 5.2.2 LTS while retaining Blender 4.4.3 compatibility. It adds a conservative path for real MOD3 files whose global bounding-box records have unknown mesh ownership.

Real MOD3 samples have complete global bbox tables whose mesh ownership is not established. The importer now retains ordered raw records and complete original mesh headers, including byte 41, without assigning guessed ownership. Geometry import continues. A packed, content-addressed import baseline permits byte-perfect whole-source replay only for an unchanged, complete scene; edits or missing/damaged metadata refuse export before replacing the target. No unknown bbox reconstruction or override is provided.

Validation: 18 Python tests; Blender 4.4.3 and 5.2.2 registration, importer API, bounds, export-safety, material and 16 generated-export suites; 31 opaque preservation/guard cases (including real save/reopen) and 21 round-trip cases per version. All five private real models import and unchanged source → A → B outputs are byte-identical, including opaque bbox/header bytes. Failed imports retain an incomplete baseline and cannot export even after the unfinished mesh is deleted. No game asset is included or committed.

The supported real-file export path replays the complete source only for an unchanged, complete import. Geometry, weights, hierarchy, ordering, metadata edits and unverifiable scenes fail closed before the destination is replaced. This PR does not infer bbox ownership or regenerate unknown records. Synthetic generated export remains tested separately.

Known limits: arm has one scene-normal mismatch on a zero-area face (PARTIAL); actual TEX conversion and game-side validation were not run. Upstream has no top-level license declaration, so this change does not grant redistribution rights. No push or PR was performed as part of this work.

This is a local draft. Current evidence and functional boundaries: [OPAQUE_BBOX_PRESERVATION.md](OPAQUE_BBOX_PRESERVATION.md).
