# Changelog

## Unreleased — blender-5.2-compat maintenance branch

- Modern legacy add-on registration, annotation properties, collection/selection/armature/UV/normal APIs.
- File-section, hierarchy and output checks; correct IEEE half-float encoding and per-instance state.
- Correct bounds centers, bases and half extents; preserve explicit metadata.
- Export without source transforms/deletions; atomic destination replacement; reject unsupported or lossy scenes.
- Preserve material ordering and packed weight flags; named Principled sockets and RGB Color nodes.
- Strict MRL3 lookups; visible converter failures, argv paths and bounded execution.
- Runnable binary tests and real Blender operator regression suite.

Verified on Blender 4.4.3; Blender 5.2 is a static-audit target, not verified support. Five supplied real MOD3 models fail bbox consistency interpretation, blocking release. Converter binaries and game behavior remain untested. See docs/FIX_STATUS.md and docs/VALIDATION.md. No license grant is added.
