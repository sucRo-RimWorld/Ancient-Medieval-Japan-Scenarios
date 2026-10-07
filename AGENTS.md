# AMJ Scenarios

Read this file, main:Docs/Coordination.md, then relevant implementation/design sources.
This repository owns starting Scenario/Faction/PawnKind, dialogue, optional starting-stock/research patches and their tests. Grains crops, recipes, equipment and general job tests remain in Core/Grains.
Keep AMJC DefNames and packageId sucro.ancientmedievaljapan.scenarios. No colon in Mod display names.
Confirmed design belongs in source/design documents; Coordination is main-only status and handoff.
Prefer reproducible automated tests. Static tests do not prove runtime or save compatibility. RimWorld automation must retain rendering offscreen/private, and fail on every mod-origin ERROR.
Historical prose is Japanese-first, author-approved before English translation. Preserve existing translations unless explicitly revising them.
Follow shared ModDescriptionGuidelines, DevelopmentGoldenPathGuidelines and WorkshopPackaging in https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Grains/tree/main/Docs . Exclude development files through .rimignore and synchronize alternative packaging adapters.
Do not announce GitHub changes without an actual remote commit SHA. Never claim safe Core/MO removal before real-save migration passes.

## GitHub preflight / CI error hygiene (AMJ common)

Follow the project-wide canonical rule in `sucRo-RimWorld/Ancient-Medieval-Japan-Project/AGENTS.md`.

- Before a remote write that can trigger GitHub Actions, inspect the relevant workflow triggers, path filters, required checks, and repository-specific validation path.
- Run deterministic syntax/structure/XML/packaging/script checks before pushing whenever the current environment can do so. Treat GitHub Actions as a regression gate, not the first parser/debug pass.
- Do not use repeated commits, PR pushes, API writes, or Actions runs as an exploratory debugger, and do not publish obviously broken intermediate states merely to learn from CI.
- If CI fails, stop stacking further remote changes on that workstream. Inspect the failing workflow/job/log, identify the concrete cause, validate the correction, then submit one focused fix instead of speculative variants.
- Where appropriate, use narrow branch/path triggers and `concurrency` / `cancel-in-progress` to avoid duplicate or superseded runs. Do not disable meaningful checks merely to suppress notifications.
- Documentation-only or coordination-only changes should not trigger heavy runtime/build workflows unless those files are part of the validated contract.
- Before weakening or excluding a workflow trigger, verify that release, runtime, packaging, and regression coverage remain protected.

## VE-first overlap audit

Before designing a new substantial AMJ feature or proposing a separate Mod, audit the Vanilla Expanded (VE) family first for functional overlap and prior art, using `sucRo-RimWorld/Ancient-Medieval-Japan-Project/Docs/Research/ExistingModAudit.md` as the canonical criteria. VE is a comparison priority, not the AMJ design baseline or an automatic dependency: evaluate historical/cultural fit, dependency footprint, unrelated attached content, retention ratio and reuse value before choosing use-as-is, optional compatibility, patch/retexture, prior-art-only, or AMJ implementation.

## Unowned idea staging

When a new AMJ idea may become a separate Mod but does not yet have an owning repository, **record its durable concept, research and roadmap state in `sucRo-RimWorld/Ancient-Medieval-Japan-Project`**. Do not let this runtime repository become the evolving design home merely because the idea was discovered here. Keep only a concise compatibility or ownership-boundary pointer when relevant. Once a dedicated owner repository exists, migrate confirmed design there.


## Unowned AMJ idea staging

When work in this repository discovers an AMJ idea that may become a separate Mod but does not yet have an owning repository, **do not develop its evolving design here**. Record the concept, research and roadmap state in `sucRo-RimWorld/Ancient-Medieval-Japan-Project` until the author creates/selects an owner repository. Keep only a concise compatibility or ownership-boundary pointer here when it materially affects this repository.

