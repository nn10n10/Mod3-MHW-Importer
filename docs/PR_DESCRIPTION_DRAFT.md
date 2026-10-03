# Draft title

Modernize Blender APIs and guard MOD3 import/export against data loss

# Draft description

The current add-on uses Blender 2.79 registration and scene APIs and can modify source objects or silently lose loop/bounding-box data during export. This branch updates the Blender integration and rejects unsupported scenes explicitly, while keeping upstream's MOD3 structure rather than copying an older modified fork wholesale.

Changes include rollback-safe registration, modern mesh/armature/UV/normal APIs, named Principled sockets and Color nodes, section/bone validation, half-float corrections, bounds math, preserved material/weight metadata, non-destructive export and atomic output writes. Texture conversion uses explicit arguments and visible failures.

Validation: 13 standalone Python tests; five real Blender 4.4.3 API/safety suites; 16 synthetic complete-file operator round-trips with original/A semantic equality and A/B binary equality excluding creationDate. Three supplied MRL3 files parse successfully. No bundled executables were run; no game assets are included.

**Do not submit as PR-ready yet.** Blender 5.2.2 runtime registration, synthetic import/export and API/safety suites pass. Five real MOD3 files are rejected by a per-mesh bbox association invariant: their global table is physically complete, but ownership is unresolved. The old 4.4.3 add-on imports the mesh geometry and stores those records opaquely; upstream silently truncates some associations. Resolve this without guessing before accepting these files. Game loading, actual texture conversion and licensing also need review. Exporting MOD3 Armatures, unapplied modifiers and conflicting per-corner attributes is deliberately rejected.

Before opening the PR, resolve the bbox blocker in FIX_STATUS.md, complete a real source→A→B round-trip, rerun the real-file suite in Blender 5.2, and update this description with actual results. Upstream should review any desired feature/version policy before release. This document is a local draft: no PR has been opened.
