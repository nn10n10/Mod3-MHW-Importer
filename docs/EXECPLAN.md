# Execution plan: maintained Blender 5.2 fork

## Goal and scope

Prepare this local `blender-5.2-compat` branch as the source for the `nn10n10/Mod3-MHW-Importer` maintenance fork. The original AsteriskAmpersand repository remains `upstream/master`. Inspect public compatibility forks read-only, adopt only independently justified changes, give users a concise and accurate status page, then rerun regression suites. Bbox ownership is unresolved; do not investigate or infer it. Do not push or create a PR in this task.

## Repository state

- Branch: `blender-5.2-compat`; upstream master baseline: `364c260`.
- Public target `nn10n10/Mod3-MHW-Importer` currently has only `master`, at `364c260` (checked with `git ls-remote`). No personal fork remote is configured in this local repository.
- VaiVuong and Leoluis0705 repositories were cloned without checkout outside this worktree and their refs fetched into local review-only refs. Neither fork was modified.
- Prior validation on Blender 4.4.3 / Python 3.11.11 and Blender 5.2.2 LTS / Python 3.13.13 covers the opaque-preservation design, synthetic exporters, and five private real samples. Arm retains one zero-area-face normal mismatch; TEX conversion and game-side behavior remain untested.

## Work sequence

1. **Inspect public compatibility forks — complete.** Compared VaiVuong `master` (`89ac10a`) and `Mod3ImporterLayer-Fixes` (`6a3dddd`), plus Leoluis0705 `main` / `v5.0.1-fix6` (`eb3ad02`) against the maintained branch and upstream base. Findings: [FORK_COMPARISON.md](FORK_COMPARISON.md).
2. **Assess changes and safety — complete.** No missing fork change met the independent correctness and safety bar. No fork code was adopted.
3. **Prepare maintenance documentation — complete.** README now states the maintained-fork relationship, tested Blender versions, unchanged-file guarantee, real-file edit boundary, known normal limitation and untested converter/game behavior. Detailed audit evidence remains under `docs/` and `tests/`.
4. **Run full relevant regression suite — complete.** Ordinary Python tests: 18 passed. On Blender 4.4.3 and 5.2.2, registration/API/bounds/export-safety/material/generated-export tests passed; opaque-preservation suite passed 31 checks, including real-file save/close/reopen; round-trip suite passed 16 generated exports, 16 replay fixtures, and all five private real samples. The arm sample retains the documented zero-area corner-normal mismatch; texture conversion and in-game behavior remain untested. Logs/results and sample assets remain outside the repository.
5. **Publication readiness — complete after the documentation commit.** Verify accurate docs, clean worktree, branch history and private-asset exclusion. Report whether the local branch is ready for publication to the maintained fork. Do not push or create a PR.

## Boundaries

Unchanged complete real imports can round-trip by exact source replay. Edited real MOD3 reconstruction remains unsupported while bbox ownership is unknown. Keep the zero-area normal limitation, untested TEX conversion and untested game validation visible. No license is inferred from another fork's added `LICENSE`; upstream has no top-level license declaration.
