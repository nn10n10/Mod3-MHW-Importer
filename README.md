# MHW MOD3 Importer — Blender 5.2 maintenance fork

This repository is the compatibility-maintenance fork at [nn10n10/Mod3-MHW-Importer](https://github.com/nn10n10/Mod3-MHW-Importer), based on the original [AsteriskAmpersand/Mod3-MHW-Importer](https://github.com/AsteriskAmpersand/Mod3-MHW-Importer). The original project and its format research remain credited to their authors; this fork maintains Blender compatibility independently.

## Maintenance status

- **Blender 5.2 LTS compatibility:** tested with Blender 5.2.2 LTS on Windows. Blender 4.4.3 is also retained as a tested compatibility version.
- **Real MOD3 files:** import and unchanged, complete-file round-trip have been tested. An unchanged import is exported by replaying the original file bytes.
- **Edited real files:** full MOD3 edit/export support is not claimed. While bbox record ownership is unresolved, edits that could invalidate preserved data are refused before writing.
- **Known limitation:** one arm sample has a corner-normal mismatch on a zero-area face.
- **Not validated:** bundled TEX conversion and in-game loading or appearance.

For a preservation-capable import, installation and option details, regression commands, evidence, and remaining limits, see [docs/OPAQUE_BBOX_PRESERVATION.md](docs/OPAQUE_BBOX_PRESERVATION.md), [tests/README.md](tests/README.md), and [docs/VALIDATION.md](docs/VALIDATION.md).

## Install

For **Install from Disk**, first make a ZIP whose top level is one add-on folder containing `__init__.py`, `blender/`, `operators/`, `mod3/`, `mrl3/`, `common/` and `boundingbox/`; select that ZIP in Blender Preferences → Add-ons → Install from Disk, then enable the add-on. Alternatively, place that folder in Blender's user `scripts/addons` directory and restart Blender. This is a legacy add-on, not a Blender Extensions package.

## Compatibility review

The comparison with public Blender 4.5.3 and 5.0.1 compatibility forks is recorded in [docs/FORK_COMPARISON.md](docs/FORK_COMPARISON.md). The upstream master remains the original AsteriskAmpersand repository's `master` branch.

Original feature documentation and acknowledgements are in the [upstream README](https://github.com/AsteriskAmpersand/Mod3-MHW-Importer#readme). No license terms are added by this compatibility fork; see the documented licensing limitation before redistribution.
