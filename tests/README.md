# Regression tests

Run from the repository root on Windows PowerShell:

```powershell
python -B -m unittest discover -s tests -p 'test_*.py' -v
$blenderExe = 'E:\Program Files\Blender Foundation\Blender 4.4\blender.exe'
foreach ($testFile in @('blender_registration.py','blender_import_api.py','blender_bounds.py','blender_export_safety.py','blender_materials.py','blender_generated_roundtrip.py')) {
    & $blenderExe --background --factory-startup --python-exit-code 1 --python (Join-Path 'tests' $testFile)
    if ($LASTEXITCODE -ne 0) { throw "Failed: $testFile" }
}
& $blenderExe --background --factory-startup --python-exit-code 1 --python tests/blender_opaque_bounds.py -- --output '..\opaque-guard-results'
& $blenderExe --background --factory-startup --python-exit-code 1 --python tests/blender_roundtrip.py -- --output '..\roundtrip-results'
```

For user-provided models append `--samples 'D:\your-sample-directory'`. No files are fetched from the internet. Samples are read only; outputs are written to the separate output folder. `--output` is required. The runner recursively searches MOD3 files and records errors in `results.json`, then fails the process if any case failed. `scripts/tests.py` delegates to the same runner.

Both suites have been run with Blender 4.4.3 and 5.2.2 LTS; substitute your executable path. No standalone Python mock is used as a Blender compatibility check.

Binary fixtures exercise 14 known blocks, signed/packed weights, half-floats, truncation, header counts/offsets, bone ranges/cycles and bbox inconsistencies. The Blender runner adds two packed-weight flag cases; each uses source→Blender→A→Blender→B, compares parsed semantics and A/B binary excluding creationDate, and reports original/A semantic changes. See [validation coverage](../docs/VALIDATION.md).

Known gaps: real models complete byte-preserving replay; body scene normals now pass after isolating opposing duplicate faces, while arm retains one degenerate-face normal limitation. Fixtures cannot replace in-game checks or real converter execution. Random/fuzz and large-quantity tests are not comprehensive. Fixtures build parts of the file using the production serializer; independent known half-float/packed-weight expectations mitigate, but do not eliminate, shared parser/writer assumptions.


Opaque bbox regressions use independent count patterns (0+0/23, 0+60/23 and 12/195), duplicate bone indices and nondefault opaque spacers. Corrupt physical counts/bounds/truncation still fail. The Blender guard runner checks edits/refusal/unchanged destination and launches a separate Blender process to reopen the saved `.blend`. To additionally test a private large real snapshot, append `--reopen-sample 'D:\private\model.mod3'` to that runner.

The guard runner also triggers a genuine import failure in the second synthetic mesh, removes that unfinished mesh and verifies that partial-scene export remains blocked with all original bytes retained. There are 30 default preservation/guard cases, or 31 with the optional real save/reopen check.

Use `--samples DIR` or `MHW_MOD3_TEST_DATA` for local-only real round-trips. Unresolved replay must satisfy **source == A == B for the complete file**, plus explicit global raw bbox and complete raw mesh-header comparisons. Scene counts/topology/positions/bone hierarchy/functions/weights/UV/colors/normals are checked separately. `preservation_status` and `scene_normals_status` prevent exact replay from concealing preview-fidelity failures. The five real-file cases pass on Blender 4.4.3 and 5.2.2; body normals pass, and arm is PARTIAL because one source normal belongs to a zero-area face. The comparison threshold was not relaxed.

`blender_generated_roundtrip.py` separately creates 16 synthetic scenes from explicitly known fixture ownership and exercises the normal encoder. Outputs match fixture bytes except creationDate; it does not infer parsed-file ownership or bypass unresolved guards.

Private source copies and `.blend` snapshots embed game assets: choose output folders outside the repository (or under ignored `testdata/private/` / `samples/private/`). Never commit generated real outputs. See the [current report](../docs/OPAQUE_BBOX_PRESERVATION.md) for precise tested/untested boundaries.
