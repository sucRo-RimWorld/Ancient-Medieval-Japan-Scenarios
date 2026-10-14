# Tests agent instructions — AMJ Scenarios

Read root `AGENTS.md`, `main:Docs/Coordination.md`, and Project shared rules first. Testing procedures and accepted contracts remain in `Docs/RuntimeTesting.md`.

Static contracts: `Tests/Production/test_scenarios.py` and `Tests/Release/validate_add_changenote.py`.

Run relevant runtime/profile tooling when start behavior or the Grains provider boundary changes. No published legacy scenario saves exist to migrate. Preserve normal ModsConfig/Prefs. Report test items, expected behavioral premises, evidence, and untested coverage, not only PASS counts.

Production owns real scenario XML and new-start contracts; Release owns subscriber archive and changenote validation. Research probes never enter default CI. See `Tests/TestLifecycle.md`.
