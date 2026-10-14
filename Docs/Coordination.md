# Coordination

This file is the live status/handoff surface for AMJ - Scenarios. Confirmed behavior and test procedures belong in the formal owner sources; completed chronology remains recoverable from Git history.

### SCN-CURRENT-20261014 — Exclusive starting-scenario owner, 1.6 native matrix

**Owner:** Scenarios runtime/test verification. **Status:** FOUR-PROFILE PICKLE 12/12 PASS; STRICT MO AUDIO GATE FAIL, UI / 1.7 OPEN.

The author retired unpublished Core/Grains old-save provider migration. Scenarios exclusively owns `AMJC_NewVillage`, `AMJC_PlayerVillage`, `AMJC_Villager`; Grains has zero legacy scenario loader/Defs. Scenarios source [#12 / 7668d61](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Scenarios/commit/7668d61aa111c3668077014727e032d35a5efc2e) removed MO wholesale start-part replacement in favour of item-specific and order-independent MO/Grains patches. Older [native run 38534168906](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/actions/runs/38534168906) had grains-mo 1/3, now resolved.

Actual isolated Linux 1.6 [Project native #38542690689](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/actions/runs/38542690689), pinned Scenarios f7b2cfb5 / Grains 9e1898de, used real MO/VEF/SYR and original Scenarios tests. All four profiles 3/3 Pickle each (12/12 total), actual map starts and supply/starting research checks, exits0. Vanilla and Grains profiles native ERROR0 and full PASS. MO and Grains+MO each had 2 known FMOD audio Unity ERRORs: strict overall FAIL. Full source, expected behaviour and untested scope: `Docs/RuntimeTesting.md`. Real chooser list-data [#38532021950](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/actions/runs/38532021950) three profiles PASS, rendered menu screenshot/click untested.

Later Project [actual source-isolated native run #38566680624](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/actions/runs/38566680624) reran the exact same four source-pinned owner start suites with both implicated third-party MP3s converted only in an ephemeral game clone. Every profile was 3/3, native exit0, Unity ERROR0: **12/12 functional PASS under converted sound media**. This does not reclassify the unmodified MO/SYR provider strict ERROR2 failures or prove audible playback, UI, 1.7 or distribution. Project native audio owner handles original sound compatibility; Scenarios gameplay/Defs untouched.
Remaining: original-media MO audio ERROR gate and UI/1.7 verification; do not suppress or reclassify. 1.7, player UI, long gameplay and Steam publication remain OPEN. The separate Project FMOD workstream owns sound diagnosis and shares its status through Project main Coordination; user is not a message relay.

### SCN-ADD-CHANGENOTE-20261008 — Steam changenote author metadata

**Owner:** Scenarios packaging/release
**Status:** SOURCE IMPLEMENTED; runtime publication blockers remain, no Steam upload

Add Changenote support follows Project `Docs/WorkshopChangenotes.md`: source version `0.1.0-dev` agrees across `About/About.xml`, `About/Manifest.xml` and `About/Changelog.txt`. A new fast metadata validator runs in existing static CI. `.rimignore` keeps both About metadata files in YADA-delivered payload. This does not promote the unverified Scenarios gameplay gates to PASS or create a subscriber dependency.

### RULE-AUDIT-20261008 — operating-rule consolidation

**Owner:** Project common rules; this repository retains its local specification and gates.
**Status:** SOURCE RESTRUCTURED; validation/publication evidence is recorded in Project `Docs/RuleAudit.md` and actual commit/CI results, not inferred here.

AGENTS now routes through Project `Docs/SharedRules.md` stop conditions and task procedures. New development requires VE and non-VE source/evidence comparison plus a justified implementation decision. Static/runtime/specification/distribution/publication remain separate states. Historical records below/above retain their original scope; this entry does not reopen paused work, change gameplay/dependencies/art/versions, or supersede owner runtime/release blockers. Main-only Coordination means one authoritative integrated log, not deleting branch snapshots. No Steam/2game update is claimed.
