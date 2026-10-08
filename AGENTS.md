# AMJ Scenarios

## Start here

1. Read this file and `main:Docs/Coordination.md`; locate the latest relevant owner/status/evidence, including later corrections. Historical entries are not current approval.
2. Read Project [AGENTS.md](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/blob/main/AGENTS.md) and [Docs/SharedRules.md](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/blob/main/Docs/SharedRules.md): apply its stop conditions, then open only the task-relevant canonical procedures.
3. Read the local specification and affected source/tests below. Shared rules are owned by Project; this file owns only local scope and routing. Missing access or conflicting authority blocks the dependent action, not unrelated safe work.

New features cannot enter implementation before the Project [existing-Mod audit gate](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/blob/main/Docs/Research/ExistingModAudit.md#implementation-entry-gate) covers VE and non-VE alternatives and records why independent implementation is needed. Existing approved behavior is not redesigned by this rule audit.

## Scope and local stops

This repository owns starting Scenario/Faction/PawnKind, dialogue, optional starting-stock/research patches and their tests. Grains owns crops, recipes, equipment and general job tests.

Keep AMJC DefNames and packageId `sucro.ancientmedievaljapan.scenarios`. Preserve existing translations unless explicitly revising them. Never claim safe Core/Grains/MO removal before the real-save migration gate passes.

Read `Docs/RuntimeTesting.md` for real starts and `Docs/SaveMigrationTesting.md` for existing-save evidence. Synthetic save XML and alias-based new-start tests do not prove actual legacy engine load/re-save. Preserve original saves and the user's normal ModsConfig/Prefs.

Static contracts: `Tests/test_scenarios.py`, `Tests/test_scenario_save_contract.py`, `Tests/validate_add_changenote.py`. Follow the existing runtime/profile tooling when those behaviors change.
