# Regression tests

Run from the repository root on Windows PowerShell:

```powershell
python -B -m unittest discover -s tests -p 'test_*.py' -v
$blenderExe = 'E:\Program Files\Blender Foundation\Blender 4.4\blender.exe'
foreach ($testFile in @('blender_registration.py','blender_import_api.py','blender_bounds.py','blender_export_safety.py','blender_materials.py')) {
    & $blenderExe --background --factory-startup --python-exit-code 1 --python (Join-Path 'tests' $testFile)
    if ($LASTEXITCODE -ne 0) { throw "Failed: $testFile" }
}
& $blenderExe --background --factory-startup --python-exit-code 1 --python tests/blender_roundtrip.py -- --output '..\roundtrip-results'
```

For user-provided models append `--samples 'D:\your-sample-directory'`. No files are fetched from the internet. Samples are read only; outputs are written to the separate output folder. `--output` is required. The runner recursively searches MOD3 files and records errors in `results.json`, then fails the process if any case failed. `scripts/tests.py` delegates to the same runner.

Repeat the full Blender suite with the path to a real Blender 5.2 executable before claiming support. No standalone Python mock is used as a Blender compatibility check.

Binary fixtures exercise 14 known blocks, signed/packed weights, half-floats, truncation, header counts/offsets, bone ranges/cycles and bbox inconsistencies. The Blender runner adds two packed-weight flag cases; each uses source→Blender→A→Blender→B, compares parsed semantics and A/B binary excluding creationDate, and reports original/A semantic changes. See [validation coverage](../docs/VALIDATION.md).

Known gaps: supplied user models cannot currently complete import due to bbox mapping ambiguity; fixtures cannot replace game-origin samples, in-game checks or real converter execution. Random/fuzz and large-quantity tests are not comprehensive. Fixtures build parts of the file using the production serializer; independent known half-float/packed-weight expectations mitigate, but do not eliminate, shared parser/writer assumptions.
