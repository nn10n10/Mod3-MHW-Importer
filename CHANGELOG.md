# Changelog

## Unreleased — blender-5.2-compat maintenance branch

- Modern legacy add-on registration, annotation properties, collection/selection/armature/UV/normal APIs.
- File-section, hierarchy and output checks; correct IEEE half-float encoding and per-instance state.
- Correct bounds centers, bases and half extents; preserve explicit metadata.
- Export without source transforms/deletions; atomic destination replacement; reject unsupported or lossy scenes.
- Preserve material ordering and packed weight flags; named Principled sockets and RGB Color nodes.
- Strict MRL3 lookups; visible converter failures, argv paths and bounded execution.
- Runnable binary tests and real Blender operator regression suite.
- Split custom-normal fans across coincident oppositely wound triangle pairs; the real body sample now matches source normals in Blender 4.4.3 and 5.2.2.
- Guard interrupted unresolved imports: retain the complete source in an incomplete baseline and refuse partial-scene export before replacing output.

API/safety and synthetic coverage ran on Blender 4.4.3 and 5.2.2 LTS. Five supplied real MOD3 models import and unchanged source/A/B replay preserves complete source bytes. Bbox ownership remains unresolved, so edits still block export; arm also has one zero-area-face normal limitation. Converter binaries and game behavior remain untested. See docs/FIX_STATUS.md and docs/VALIDATION.md. No license grant is added.
