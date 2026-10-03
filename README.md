# Mod3-MHW-Importer
Blender MOD3 importer/exporter for Monster Hunter: World. This maintenance branch is based on upstream master `364c2609562436cbbee8dca3a2c91c1a4fe6bc6c`.

## Compatibility and release status

- Minimum declared Blender version: 4.4. Tested executables: **Blender 4.4.3** (Python 3.11.11) and **Blender 5.2.2 LTS** (Python 3.13.13), Windows.
- Blender 5.2.2 registration, API/safety and shader tests pass; 13 binary/MRL3 tests and 16 synthetic MOD3 operator round-trips also pass in its bundled Python. This is partial runtime coverage, not blanket compatibility for game models.
- **Development branch, not release-ready:** the five supplied real MOD3 files have a physically complete bbox table but do not fit the current per-mesh association assumption. The legacy 4.4.3 version imports their geometry and retains the records as opaque scene properties; upstream silently truncates some associations; this branch refuses them with a clear error. Do not treat the files as corrupt or export around the error. See [bbox investigation](docs/SECOND_STAGE_BBOX_AND_BLENDER52.md), [audit status](docs/FIX_STATUS.md) and [validation](docs/VALIDATION.md).

## Important limitations

- Export supports EmptyTree skeletons. An imported MOD3 animation Armature is rejected on export. Apply modifiers explicitly before export; unapplied modifiers, mirrored/singular transforms, more than eight weights and conflicting per-corner data are rejected.
- MOD3 has per-vertex attributes. Split vertices before export where UV, normal, color or tangent seams require different values for one vertex. Export does not silently choose one loop value.
- Use **Slash** weight mode for preservation tests. Group/Signed weight representations can lose information. Tangents are recomputed; arbitrary packed tangent bytes are not guaranteed to round-trip. Packed weight flags have regression coverage.
- Material node construction was tested on Blender 4.4.3 and 5.2.2. The 5.2 test emits Blender's `Material.use_nodes` deprecation warning (announced for removal in Blender 6.0). Materials approximate supported game shader inputs; alpha handling and visual fidelity are partial/unverified; upstream emission/specular texture paths remain disabled and fur behavior is not validated. Multiple Blender polygon materials on one mesh are unsupported.
- Synthetic automatic-bounds calculations have geometry tests. Real sample bbox ownership is unresolved across legacy and newer table interpretations; these inputs currently fail clearly. Explicit bounds preserve metadata: after editing geometry, check bounds and radius yourself or recalculate; unchanged metadata is not proof of game correctness.
- Texture converters are Windows-only bundled upstream binaries. Invocation paths, Unicode/space arguments and failure handling were tested without running the converters. Actual conversion, game rendering and in-game loading remain untested.
- Shared collections may prevent the optional clear-scene operation. Clear scene defaults off; no global image purge is performed.
- Upstream does not include a top-level license declaration. Clarify the source and bundled executable redistribution licenses with upstream before distributing a release. This branch does not invent a license.

## Tests

See [tests/README.md](tests/README.md) for runnable binary tests and headless Blender regression commands. The round-trip runner reports original/A semantic changes separately from A/B stability and returns a nonzero exit status for any failure.

# Documentation
Documentation on functionality can be found on https://github.com/Ezekial711/MonsterHunterWorldModding/wiki/Asterisk's-Plugin-Features.

Additionaly under Asterisk's Plugin Notes are notes on the format that are not explained on the research template and cover advanced functionality.

# Installation
Create a ZIP containing one add-on folder with `__init__.py`, `blender/`, `operators/`, `mod3/`, `mrl3/`, `common/` and `boundingbox/` at that folder's root. Exclude `.git`, audit outputs, test assets and caches. In Blender use Preferences → Add-ons → Install from Disk, select the ZIP and enable the add-on. Alternatively place the folder under the user `scripts/addons` directory and restart Blender. The Import/Export menus contain the MOD3 operators.

This is a legacy add-on, not a Blender Extensions package. Do not install the whole workspace or the backup ZIP as the maintained version. For export-preserving imports select EmptyTree skeleton and Slash weights, disable LOD filtering, and preserve explicit bounds. Test on copies of your files.

# Author
* **AsteriskAmpersand/\*&**

# Acknowledgements
* **Lukas Scone/Predator** - For the initial reverse engineering of the MT Framework Model Format. - [Predator's Dev Blog](https://lukascone.wordpress.com/2017/06/18/mt-framework-tools/)
* **CrazyT** - For his work on the original blender importer plugin and his help during the coding of this version. - [CrazyT's Github User Page](https://github.com/TheCrazyT)
* **Jodo** - For his tex to dds converter and compiling a custom version for this project. - [Jodo's MHW Modding Site](http://www.mhwmod.com/)
* **Cristian Năvălici** - For his crc32/crcjam code for python. - [PyCRC Project Page](https://pypi.org/project/PyCRC/#description)
* **Chuck Walbourn** - For the DirectXTex library for dds to png convertor. - [DirectXTex Github Repo](https://github.com/Microsoft/DirectXTex/wiki)
