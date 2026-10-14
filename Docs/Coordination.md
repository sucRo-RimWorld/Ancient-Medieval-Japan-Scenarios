# Coordination

This file is the live status/handoff surface for AMJ - Scenarios. Confirmed behavior and test procedures belong in the formal owner sources; completed chronology remains recoverable from Git history.

### SCN-CURRENT-20261014 — Scenarios sole owner and runtime gate

**Owner:** Scenarios runtime/test verification. **Status:** NATIVE 1.6 PARTIAL PASS — Scenarios and Scenarios＋Grains E2E 6/6; MO profiles and rendered menu remain OPEN.

2026-10-14 author decision: Since no public/private play or old saves exist, pre-publication Core/Grains scenario save-migration support is unnecessary. Grains no longer supplies the three starting Defs or `LegacyStartingScenarios/`; Scenarios exclusively owns `AMJC_NewVillage`, `AMJC_PlayerVillage`, `AMJC_Villager` and conditional start supplies. The old provider-guard staging and synthetic old-save migrations were removed from Scenarios; current authoritative test procedure is `Docs/RuntimeTesting.md`.

2026-10-14 actual native Linux 1.6 evidence: [Project Actions #38525733684](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/actions/runs/38525733684) three-profile loaded-def ownership 3/3, ERROR 0; [#38526753894](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/actions/runs/38526753894) Scenarios and Scenarios＋Grains actual colony starts, 6/6, ERROR 0. Pinned Grains 9e1898de and Scenarios bf931a6e. Formal assertions and limits recorded in `Docs/RuntimeTesting.md`.

Remaining: actual native new starts with MO and Grains＋MO, rendered scenario menu and click/screenshot, 1.7, long play. These PASS results are not publication or untested-profile evidence.

### SCN-ADD-CHANGENOTE-20261008 — Steam changenote author metadata

**Owner:** Scenarios packaging/release
**Status:** SOURCE IMPLEMENTED; runtime publication blockers remain, no Steam upload

Add Changenote support follows Project `Docs/WorkshopChangenotes.md`: source version `0.1.0-dev` agrees across `About/About.xml`, `About/Manifest.xml` and `About/Changelog.txt`. A new fast metadata validator runs in existing static CI. `.rimignore` keeps both About metadata files in YADA-delivered payload. This does not promote the unverified Scenarios gameplay gates to PASS or create a subscriber dependency.

### RULE-AUDIT-20261008 — operating-rule consolidation

**Owner:** Project common rules; this repository retains its local specification and gates.
**Status:** SOURCE RESTRUCTURED; validation/publication evidence is recorded in Project `Docs/RuleAudit.md` and actual commit/CI results, not inferred here.

AGENTS now routes through Project `Docs/SharedRules.md` stop conditions and task procedures. New development requires VE and non-VE source/evidence comparison plus a justified implementation decision. Static/runtime/specification/distribution/publication remain separate states. Historical records below/above retain their original scope; this entry does not reopen paused work, change gameplay/dependencies/art/versions, or supersede owner runtime/release blockers. Main-only Coordination means one authoritative integrated log, not deleting branch snapshots. No Steam/2game update is claimed.
