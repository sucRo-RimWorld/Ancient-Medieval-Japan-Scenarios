# AMJ Scenarios

Read this file, main:Docs/Coordination.md, then relevant implementation/design sources.
This repository owns starting Scenario/Faction/PawnKind, dialogue, optional starting-stock/research patches and their tests. Grains crops, recipes, equipment and general job tests remain in Core/Grains.
Keep AMJC DefNames and packageId sucro.ancientmedievaljapan.scenarios. No colon in Mod display names.
Confirmed design belongs in source/design documents; Coordination is main-only status and handoff.
Prefer reproducible automated tests. Static tests do not prove runtime or save compatibility. RimWorld automation must retain rendering offscreen/private, and fail on every mod-origin ERROR.
Historical prose is Japanese-first, author-approved before English translation. Preserve existing translations unless explicitly revising them.
Follow shared ModDescriptionGuidelines, DevelopmentGoldenPathGuidelines and WorkshopPackaging in https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Grains/tree/main/Docs . Exclude development files through .rimignore and synchronize alternative packaging adapters.
Do not announce GitHub changes without an actual remote commit SHA. Never claim safe Core/MO removal before real-save migration passes.

## VE-first overlap audit

Before designing a new substantial AMJ feature or proposing a separate Mod, audit the Vanilla Expanded (VE) family first for functional overlap and prior art, using `sucRo-RimWorld/Ancient-Medieval-Japan-Project/Docs/Research/ExistingModAudit.md` as the canonical criteria. VE is a comparison priority, not the AMJ design baseline or an automatic dependency: evaluate historical/cultural fit, dependency footprint, unrelated attached content, retention ratio and reuse value before choosing use-as-is, optional compatibility, patch/retexture, prior-art-only, or AMJ implementation.

## Unowned idea staging

When a new AMJ idea may become a separate Mod but does not yet have an owning repository, **record its durable concept, research and roadmap state in `sucRo-RimWorld/Ancient-Medieval-Japan-Project`**. Do not let this runtime repository become the evolving design home merely because the idea was discovered here. Keep only a concise compatibility or ownership-boundary pointer when relevant. Once a dedicated owner repository exists, migrate confirmed design there.


## Unowned AMJ idea staging

When work in this repository discovers an AMJ idea that may become a separate Mod but does not yet have an owning repository, **do not develop its evolving design here**. Record the concept, research and roadmap state in `sucRo-RimWorld/Ancient-Medieval-Japan-Project` until the author creates/selects an owner repository. Keep only a concise compatibility or ownership-boundary pointer here when it materially affects this repository.

