# Tests agent instructions — AMJ Scenarios

Read root `AGENTS.md`, `main:Docs/Coordination.md`, and Project shared rules first. Testing procedures and accepted contracts remain in `Docs/RuntimeTesting.md` and `Docs/SaveMigrationTesting.md`.

Static contracts: `Tests/Production/test_scenarios.py`, `Tests/Production/test_scenario_save_contract.py`, and `Tests/Release/validate_add_changenote.py`.

Run relevant runtime/profile tooling when start, removal, migration or save behavior changes. Synthetic save XML and alias-based new-start tests do not prove real legacy engine load/re-save. Preserve actual old saves and normal ModsConfig/Prefs. Report test items, expected behavioral premises, evidence, and untested coverage, not only PASS counts.

Production owns real scenario XML and save-source contracts; Release owns subscriber archive and changenote validation. Research probes never enter default CI. See `Tests/TestLifecycle.md`.
