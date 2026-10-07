# AMJ Scenarios

Read this file, main:Docs/Coordination.md, then relevant implementation/design sources.
This repository owns starting Scenario/Faction/PawnKind, dialogue, optional starting-stock/research patches and their tests. Grains crops, recipes, equipment and general job tests remain in Core/Grains.
Keep AMJC DefNames and packageId sucro.ancientmedievaljapan.scenarios. No colon in Mod display names.
Confirmed design belongs in source/design documents; Coordination is main-only status and handoff.
Prefer reproducible automated tests. Static tests do not prove runtime or save compatibility. RimWorld automation must retain rendering offscreen/private, and fail on every mod-origin ERROR.
Historical prose is Japanese-first, author-approved before English translation. Preserve existing translations unless explicitly revising them.
Follow shared ModDescriptionGuidelines, DevelopmentGoldenPathGuidelines and WorkshopPackaging in https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Grains/tree/main/Docs . Exclude development files through .rimignore and synchronize alternative packaging adapters.
Do not announce GitHub changes without an actual remote commit SHA. Never claim safe Core/MO removal before real-save migration passes.
