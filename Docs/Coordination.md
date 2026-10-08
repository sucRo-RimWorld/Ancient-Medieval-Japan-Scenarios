# Coordination

This file is the live status/handoff surface for AMJ - Scenarios. Confirmed behavior and test procedures belong in the formal owner sources; completed chronology remains recoverable from Git history.

### SCN-CURRENT-20261009 — paused engine/save verification handoff

**Owner:** Scenarios runtime/save verification  
**Status:** OPEN — paused while higher-priority Grains work proceeds; engine/runtime/save release gates remain unresolved

Repository extraction, guarded Grains coexistence, runtime-test ownership transfer, static/CI tooling and read-only save-contract tooling are complete. Current source baseline is the post-PR #2 save-contract implementation line; formal procedures are `Docs/RuntimeTesting.md` and `Docs/SaveMigrationTesting.md`.

Still required when this workstream resumes: installed-game C# compilation and four-profile starts, isolated production-ID legacy save load/re-save, provider add/remove coverage, rendering, exact fresh evidence and every-ERROR = 0. No safe Grains/MO removal or release-readiness claim follows from the completed static tooling.

### SCN-ADD-CHANGENOTE-20261008 — Steam changenote author metadata

**Owner:** Scenarios packaging/release
**Status:** SOURCE IMPLEMENTED; runtime/old-save publication blockers remain, no Steam upload

Add Changenote support follows Project `Docs/WorkshopChangenotes.md`: source version `0.1.0-dev` agrees across `About/About.xml`, `About/Manifest.xml` and `About/Changelog.txt`. A new fast metadata validator runs in existing static CI. `.rimignore` keeps both About metadata files in YADA-delivered payload. This does not promote the unverified Scenarios gameplay/old-save gates to PASS or create a subscriber dependency.

### RULE-AUDIT-20261008 — operating-rule consolidation

**Owner:** Project common rules; this repository retains its local specification and gates.
**Status:** SOURCE RESTRUCTURED; validation/publication evidence is recorded in Project `Docs/RuleAudit.md` and actual commit/CI results, not inferred here.

AGENTS now routes through Project `Docs/SharedRules.md` stop conditions and task procedures. New development requires VE and non-VE source/evidence comparison plus a justified implementation decision. Static/runtime/specification/distribution/publication remain separate states. Historical records below/above retain their original scope; this entry does not reopen paused work, change gameplay/dependencies/art/versions, or supersede owner runtime/release blockers. Main-only Coordination means one authoritative integrated log, not deleting branch snapshots. No Steam/2game update is claimed.
