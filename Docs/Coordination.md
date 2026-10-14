# Coordination

This file is the live status/handoff surface for AMJ - Scenarios. Confirmed behavior and test procedures belong in the formal owner sources; completed chronology remains recoverable from Git history.

### SCN-CURRENT-20261014 — Scenarios sole owner and runtime gate

**Owner:** Scenarios runtime/test verification. **Status:** SOURCE RECONCILIATION IN PROGRESS — four-profile native game evidence remains OPEN.

2026-10-14 author decision: Since no public/private play or old saves exist, pre-publication Core/Grains scenario save-migration support is unnecessary. Grains no longer supplies the three starting Defs or `LegacyStartingScenarios/`; Scenarios exclusively owns `AMJC_NewVillage`, `AMJC_PlayerVillage`, `AMJC_Villager` and conditional start supplies. The old provider-guard staging and synthetic old-save migrations were removed from Scenarios; current authoritative test procedure is `Docs/RuntimeTesting.md`.

Remaining: actual RimWorld native four-profile new starts, rendering/UI, isolated complete logs and every-ERROR = 0. Neither static CI nor removal of unneeded legacy gates establishes a successful game launch or a release.

### SCN-ADD-CHANGENOTE-20261008 — Steam changenote author metadata

**Owner:** Scenarios packaging/release
**Status:** SOURCE IMPLEMENTED; runtime publication blockers remain, no Steam upload

Add Changenote support follows Project `Docs/WorkshopChangenotes.md`: source version `0.1.0-dev` agrees across `About/About.xml`, `About/Manifest.xml` and `About/Changelog.txt`. A new fast metadata validator runs in existing static CI. `.rimignore` keeps both About metadata files in YADA-delivered payload. This does not promote the unverified Scenarios gameplay gates to PASS or create a subscriber dependency.

### RULE-AUDIT-20261008 — operating-rule consolidation

**Owner:** Project common rules; this repository retains its local specification and gates.
**Status:** SOURCE RESTRUCTURED; validation/publication evidence is recorded in Project `Docs/RuleAudit.md` and actual commit/CI results, not inferred here.

AGENTS now routes through Project `Docs/SharedRules.md` stop conditions and task procedures. New development requires VE and non-VE source/evidence comparison plus a justified implementation decision. Static/runtime/specification/distribution/publication remain separate states. Historical records below/above retain their original scope; this entry does not reopen paused work, change gameplay/dependencies/art/versions, or supersede owner runtime/release blockers. Main-only Coordination means one authoritative integrated log, not deleting branch snapshots. No Steam/2game update is claimed.
