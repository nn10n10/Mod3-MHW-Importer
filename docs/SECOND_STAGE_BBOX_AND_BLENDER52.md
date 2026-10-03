# 第二阶段：真实 MOD3 bbox 根因与 Blender 5.2 验证

测试 Blender：5.2.2 LTS，Python `3.13.13`；Blender 4.4 基线 `4.4.3` / Python `3.11.11`。分支代码 HEAD 在本阶段未修改。样本只读；输入哈希前后相同。

## A. 五个文件的物理布局

MOD3 magic 字节为 `4D 4F 44`（小端整数 `0x444F4D`）；版本字段 offset `4=237`、`5=0`。文件头本身**没有单一全局 bbox count 字段**。mesh 记录长 80 bytes，当前 schema 的 `boundingBoxCount` 是 mesh header 相对 offset 41 的一个 byte（旧 schema 在同一位置属于 `unkn9[0]`）。bbox 表紧跟所有 mesh headers：先 4-byte uint count，再是 144-byte records。记录布局按当前 upstream schema 解码为 boneIndex、12-byte spacer、AABB center/radius/min/max、OABB matrix/vector。

| File | Size | Bones / meshes | mesh bbox refs | table count | meshOffset → bbox start | expected table end | next section (`vertexOffset`) | delta | bytes after bbox | result |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| `f_arm039_0001.mod3` | 387,604 | 135 / 2 | `0,0` | 23 | `21776` → `21936` | `25252` | `25252` | **+0** | 362,352 | reject: refs sum != table count |
| `f_body039_0001.mod3` | 387,964 | 135 / 2 | `0,60` | 23 | `21904` → `22064` | `25380` | `25380` | **+0** | 362,584 | reject: refs sum != table count |
| `f_helm039_0001.mod3` | 399,920 | 90 / 1 | `12` | 195 | `15568` → `15648` | `43732` | `43732` | **+0** | 356,188 | reject: refs sum != table count |
| `f_leg039_0001.mod3` | 399,920 | 90 / 1 | `12` | 195 | `15568` → `15648` | `43732` | `43732` | **+0** | 356,188 | reject: refs sum != table count |
| `f_wst039_0001.mod3` | 56,216 | 58 / 1 | `0` | 23 | `10192` → `10272` | `13588` | `13588` | **+0** | 42,628 | reject: refs sum != table count |

bbox table expected end is `meshOffset + meshCount*80 + 4 + tableCount*144`. The computed table end equals `vertexOffset` for all five files (delta 0); there is no missing bbox padding or section overlap. Remaining file bytes after the table are vertex/index/trailing sections, not unused bbox capacity. The current rejection is not caused by a truncated table or incorrect section offset.

| File | Per-mesh references | Global records | Refs minus records | Current rejection |
|---|---:|---:|---:|---|
| `f_arm039_0001.mod3` | `0+0 = 0` | 23 | -23 | `Traceback (most recent call last):` |
| `f_body039_0001.mod3` | `0+60 = 60` | 23 | +37 | `Traceback (most recent call last):` |
| `f_helm039_0001.mod3` | `12 = 12` | 195 | -183 | `Traceback (most recent call last):` |
| `f_leg039_0001.mod3` | `12 = 12` | 195 | -183 | `Traceback (most recent call last):` |
| `f_wst039_0001.mod3` | `0 = 0` | 23 | -23 | `Traceback (most recent call last):` |

Header values (all files): magic/version above; `boneOffset`, `groupOffset`, `materialNamesOffset`, `meshOffset`, `vertexOffset`, `facesOffset`, and `trailOffset` are emitted in `bbox-triple-parse.json` alongside all mesh vertex/face counts. Table details: arm/body/waist have 23 records and bone refs 1–54 with 23 distinct values; helm/leg have 195 records, bone refs 0–73 with 29 distinct values (records repeat bone indices). Every decoded record has finite values, ordered AABB min/max, bone indices below the file header boneCount, and no 255 sentinel. This supports a structured table; it does not establish which mesh owns each record. Helm and leg are byte-identical (same SHA-256) despite separate names.

## B. Three-way behavior on the same five inputs

**Old user 4.4.3 add-on:** add-on register/unregister passed; Import and Export operators were available. Each real operator returned `FINISHED`, created the expected mesh count and header-matching total vertex/index-derived polygon counts, an Armature, UV layers, custom normals and vertex weights. All vertices had at least one assigned group. The input SHA-256 remained unchanged. It created zero visible bbox objects. Instead, it interpreted the global `count × 36 int32` records (36×4 = 144 bytes each) as `MeshProperty` entries and stored `MeshPropertyCount` plus every `MeshPropertyN` in scene custom properties (24 or 196 keys including the count). The old code does not give these records bbox semantics. No textures/materials were requested in this baseline. One old source `SyntaxWarning` reports invalid escape `\M`; no import traceback occurred.

| File | Old operator | Meshes | Vertices | Polygons | Armature bones* | vertex groups | UVs | custom normals | weighted vertices | saved opaque records |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `f_arm039_0001.mod3` | `FINISHED` | 2 | 9,078 | 11,972 | 136 | 68 | 2 | 2 | 9,078 | 23 |
| `f_body039_0001.mod3` | `FINISHED` | 2 | 8,767 | 13,669 | 136 | 216 | 2 | 2 | 8,767 | 23 |
| `f_helm039_0001.mod3` | `FINISHED` | 1 | 8,566 | 13,675 | 91 | 182 | 1 | 1 | 8,566 | 195 |
| `f_leg039_0001.mod3` | `FINISHED` | 1 | 8,566 | 13,675 | 91 | 182 | 1 | 1 | 8,566 | 195 |
| `f_wst039_0001.mod3` | `FINISHED` | 1 | 994 | 1,799 | 59 | 92 | 1 | 1 | 994 | 23 |

*Scene Armature count includes the synthetic root, one more than the MOD3 header bone count. Colors were absent in the imported mesh datablocks; real files therefore do not exercise vertex-color import. This import setup disabled texture/material conversion.

**Upstream master (`364c260…`):** `Mod3.marshall` completed for all five. The historical `Mod3MeshCollection.marshall` catches any exception raised while assigning the requested per-mesh references and executes `pass`. Observed per-mesh assignments were `[0,0]`, `[0,23]` when the second mesh asks 60, `[12]` when the table has 195, and `[0]`. So upstream parser success is not evidence that associations were parsed correctly; body silently truncates at 23, while many global records remain unattached. The upstream add-on itself does not register in Blender 4.4.3 (`INFO_MT_file_import` absent); calling its importer layer directly reaches `scene.objects.link`, removed from current Blender, before it can create scene meshes. Parser-only pass and actual Blender scene-import pass are distinct results.

**Current branch:** at both Blender 4.4.3 and 5.2.2, `b95a2eb` rejects all five at `assigned != BoundingBoxes.count`, before scene mutation. The error includes both counts. The five samples remain byte-for-byte unchanged. This is a behavior regression versus the old plugin’s geometry import, introduced by the new equality invariant, rather than a Blender API failure.

## History and root cause

- `7a2a3b2` (2020-06-14, “Unstable 2.0 Release”) changed the old `Mod3MeshProperties` table (`36 int32` values per entry) to `Mod3BoundingBox` records (also 144 bytes) and reinterpreted bytes in the mesh header’s former opaque `unkn9[39]` area, including the byte now named `boundingBoxCount`. Its commit message says “Not retrocompatible with files from previous versions.”
- `git log -S boundingBoxCount` finds `7a2a3b2` as the upstream introduction of the field. `f714f08` (2022-10-06) reformats/reworks importer and mesh code for weight behavior while retaining the existing bbox field; its diff adds no evidence that per-mesh counts must sum to every historical table.
- `aecdae8` (2024-01-16) addresses eight-weight decoding and vertex-buffer offsets. `88eace4` (2024-07-05) adjusts malformed face index handling. Their diffs do not alter bbox table association.
- `b95a2eb` (2026-10-03, local change) adds the strict equality check in `Mod3MeshCollection.marshall`; `git show` identifies this as the first commit that rejects these inputs. The narrow change is direct, so `git bisect` would not add evidence and was not used.

**Root cause:** the strict rejection is triggered by a new, unproven assumption that the byte at mesh-header offset 41 is a per-mesh record count and that all values index the global 144-byte table sequentially. The files have a physically complete global table, while their semantic layout resembles the pre-2020 opaque property-table implementation that the user’s old version retained. Upstream’s newer bbox interpretation silently drops associations on underflow. The records look structurally plausible, but repo history/sample evidence does not prove a safe per-mesh mapping for this legacy layout. Do not label these files corrupt; do not simply remove the check, infer a new count, or keep upstream’s `except: pass`.

## C. Decision and safe next change

Bounding-box handling **does need a compatibility redesign** before PR. Keep the current explicit fail-closed behavior until a new path can identify and preserve a legacy/opaque table as such, report that mesh-to-box ownership is unknown, and prevent an ordinary export from silently discarding or reassigning the records. The repo does not yet contain evidence for a valid ownership rule, so this phase makes no bbox code change. A follow-up fix needs local-only real fixtures, exact original-to-A and A-to-B checks, and a clear warning/refusal policy. This is safer than either rejecting the whole mesh forever or guessing which mesh owns each box.

## D. Blender 5.2.2 LTS runtime results

- Version: Blender 5.2.2 LTS, build hash `d13f752e3b9c`, branch `blender-v5.2-release`; bundled Python 3.13.13 (May 8, 2026).
- Add-on repeated register/unregister/reload and Import/Export operators: PASS. Registration code appends/removes the Import and Export callbacks on `TOPBAR_MT_file_import` / `TOPBAR_MT_file_export`; actual menu UI drawing is unavailable in background mode.
- Importer mesh/UV/custom-normal/empty-tree/empty-armature API, export safety, bounding geometry and shader-node tests: 5 scripts PASS.
- The 13 standalone binary/MRL tests also passed inside Blender 5.2’s bundled Python 3.13.13. All 44 source files parsed by Python AST.
- 16 real-operator synthetic MOD3 import → A export → A import → B export tests: PASS; all original/A semantic comparisons equal, and A/B bytes match except creationDate.
- Three real MRL3 samples parsed under Blender’s Python: 5 materials / 12 textures each, no unknown map types. This is MRL3 parser coverage, not texture conversion.
- Five user MOD3 files: FAIL at the intentional bbox invariant before mesh creation. No real-file round-trip completed.
- Console warning: `Material.use_nodes` is deprecated in 5.2 and expected to be removed in 6.0; it still works and this is non-blocking for the target. The safety test’s “Apply modifiers explicitly” error is expected and asserts preservation of an existing output file. No unexpected traceback, invalid RNA property or unknown-node warning was seen in passing tests. Texture EXEs and game behavior remain untested.

## E. Feature matrix

Status is scoped to the tested path; real-file issues are not hidden by synthetic results.

| Feature | Blender 4.4.3 | Blender 5.2.2 | Evidence |
|---|---|---|---|
| Add-on registration | PASS | PASS | repeated lifecycle, operators, Import/Export callbacks attached by registration |
| MOD3 parsing | PARTIAL | PARTIAL | 14 block types synthetic PASS; five real files FAIL current strict bbox check; upstream parser pass has silent partial association |
| Mesh import | PASS (old user plugin) | PARTIAL | old operator creates all five samples; current synthetic import passes, real files rejected |
| Skeleton import | PASS (old user plugin) | PASS (synthetic) | real armature has header bones plus synthetic root; 5.2 armature API smoke and synthetic round-trip |
| Weights | PASS (old user plugin) | PASS (synthetic) | every old imported real vertex assigned; Slash synthetic/packed flag round-trips |
| Normals | PASS | PASS | old real models have custom normals; synthetic API + round-trip |
| UV | PASS | PASS | old real models UV count; synthetic round-trip |
| Vertex colors | UNTESTED on supplied models | PASS synthetic | no color attributes in supplied model imports; synthetic block coverage |
| Bounding boxes | PARTIAL | PARTIAL | old stores opaque records; upstream truncates association; current rejects mismatch; synthetic geometry/round-trip pass |
| MRL3 parsing | PASS | PASS | 3 real MRL3, each 5 materials/12 textures |
| Material node creation | PASS synthetic | PASS synthetic | named sockets, Color nodes, normal/roughness/metallic/subsurface/output; alpha coverage limited |
| Texture conversion | UNTESTED | UNTESTED | bundled upstream EXEs not executed |
| MOD3 export | PASS synthetic | PASS synthetic | non-destructive export safety; real samples cannot enter current exporter |
| Synthetic round-trip | PASS | PASS | 16/16, A/B semantic and binary stability |
| Real-file round-trip | UNTESTED | FAIL to start | current importer rejects all five before A export; old importer was not round-tripped |
| Game-side validation | UNTESTED | UNTESTED | no game launch/load performed |

## F. PR gate

| Gate | State | Evidence |
|---|---|---|
| 1. Blender 5.2 registration | PASS | Blender 5.2.2 repeated lifecycle / operators |
| 2. Synthetic import/export round-trip | PASS | 16 real bpy operator cases |
| 3. Real MOD3 import | FAIL | current branch rejects all five; old 4.4.3 plugin imported these geometries |
| 4. Real MOD3 export/reimport stability | FAIL | cannot reach export with current importer; no real A/B |
| 5. No known HIGH/CRITICAL silent corruption | PARTIAL | current code rejects bbox ambiguity; unproven historical mapping remains and upstream silently truncates |
| 6. No game assets committed | PASS | samples are outside repo; Git working tree clean before report update |
| 7. README distinguishes test status | PASS after this evidence update | README/validation will state exact limited 5.2 results |

**PR-ready: NOT PR-ready.** Blockers: define/preserve the legacy bbox layout without guessing; successful real source→A→B; Blender 5.2 real model import after that; review the Blender 5.2 `use_nodes` deprecation and game/texture/licensing gaps. Do not push or open a PR yet.
