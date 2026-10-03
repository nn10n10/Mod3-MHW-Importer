# Draft title

Modernize Blender APIs and preserve unresolved MOD3 metadata safely

# Draft description

The legacy add-on uses Blender 2.79 APIs and can silently discard data during import/export. This branch updates integration for tested Blender 4.4.3 and 5.2.2 LTS and adds explicit refusal of unsupported operations.

Real MOD3 samples have complete global bbox tables whose mesh ownership is not established. The importer now retains ordered raw records and complete original mesh headers, including byte 41, without assigning guessed ownership. Geometry import continues. A packed, content-addressed import baseline permits byte-perfect whole-source replay only for an unchanged, complete scene; edits or missing/damaged metadata refuse export before replacing the target. No unknown bbox reconstruction or override is provided.

Validation: 18 Python tests, five Blender API/safety/material suites, 16 synthetic reconstructed exports, 16 synthetic opaque replays, and five real source/A/B byte-identical preservation cases. Guard tests cover geometry/weights/bones/order/metadata changes, parsed-model serialization and save/close/reopen in a separate process; Blender 5.2 also tests a 195-record real snapshot. No game asset is included, no converters were executed and no push/PR was performed.

**NOT PR-ready.** The complete real scene-fidelity runner intentionally returns nonzero: body has four non-degenerate corner-normal mismatches, and arm has one degenerate-face limitation, on both Blender versions. Source replay preserves original normal bytes but does not fix the scene discrepancy. Independently review the baseline/guard policy and investigate this normal issue before submitting. Editable real-file reconstruction remains unsupported while ownership is unknown. Actual conversion, game-side validation and redistribution licensing remain unverified.

This is a local draft. Current evidence and functional boundaries: [OPAQUE_BBOX_PRESERVATION.md](OPAQUE_BBOX_PRESERVATION.md).
