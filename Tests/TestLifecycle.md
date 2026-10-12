# Test lifecycle separation

Tests are owned by their **purpose and acceptance state**, not their date or file extension.

| Type | Intended location | Rule |
| --- | --- | --- |
| Production | `Tests/Production/` | Only approved behavior and real production code/Defs. Keep deterministic regression coverage. |
| Runtime | `Tests/Runtime/`, existing `Tests/E2E/`, `Tests/Pickle/`, `Tests/RimTest/` where present | Loaded RimWorld, actual provider/jobs, saves and rendering. Preserve existing isolated runners and complete ERROR-log requirements. |
| Release | `Tests/Release/`, existing `Tests/validate_*.py` used for packaging | Subscriber payload, Workshop, source integrity and packaging safety. |
| Research | `Tests/Research/` | Optional temporary experiments only. Never automatically invoke from default CI or ordinary `run-tests` entries. |

**Migration rule:** Existing test paths/commands are valid until an atomic migration updates all imports, CI, scripts and documented commands. Do not create no-op tests, copy fixtures into production, or delete a test still guarding active behavior. E2E remains Runtime; visual/art validators can stay in an existing specialized location. An experiment must identify its question, owner, evidence destination and retirement condition; after findings enter the canonical design/research record, remove experiment code and all callers in the same PR. Nothing in this classification authorizes changing gameplay or reducing existing CI/runtime gates.

**Current migration status:** Category boundary established; existing tests and runner paths are retained pending separately tested moves. Test failures and CI checks determine safe per-repository relocation, not the appearance of a folder tree.
