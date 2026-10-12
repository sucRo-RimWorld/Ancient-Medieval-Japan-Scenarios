# Tests agent instructions — AMJ Scenarios

Read root `AGENTS.md`, `main:Docs/Coordination.md`, and Project shared rules first. Testing procedures and accepted contracts remain in `Docs/RuntimeTesting.md` and `Docs/SaveMigrationTesting.md`.

Static contracts: `Tests/test_scenarios.py`, `Tests/test_scenario_save_contract.py`, and `Tests/validate_add_changenote.py`.

Run relevant runtime/profile tooling when start, removal, migration or save behavior changes. Synthetic save XML and alias-based new-start tests do not prove real legacy engine load/re-save. Preserve actual old saves and normal ModsConfig/Prefs. Report test items, expected behavioral premises, evidence, and untested coverage, not only PASS counts.
