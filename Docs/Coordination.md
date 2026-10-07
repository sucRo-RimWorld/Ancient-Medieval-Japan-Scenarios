# Coordination

2026-10-07: Author selected AMJ - Scenarios and packageId sucro.ancientmedievaljapan.scenarios, then requested a separate repository.
Independent source candidate prepared from the recorded Core commit. The author created sucRo-RimWorld/Ancient-Medieval-Japan-Scenarios; initial source registration follows on main.
Core production Defs/loadFolders have not been moved. Existing Core + this candidate is invalid until guarded Legacy extraction is merged.
Open: guarded Core migration, runtime test ownership transfer, actual four-profile starts and old-save/add/remove tests. No game run or save-migration PASS.

2026-10-07 registration completed: source commit 13372c3794217446ae449140c8e4dd6db77d09ae. Author renamed the source repository to Ancient-Medieval-Japan-Grains (same repository ID). Historical provenance/source hashes remain unchanged; current source repository is recorded separately. Local four-profile XML/negative tests passed; archive parity contains 13 runtime/license files. CI/runtime/save success is not claimed. Grains handoff committed at ac6233b47b387bf68c7b9614daafa241ffa7358a; guarded physical extraction remains next.

2026-10-07 guarded Grains production extraction merged: Grains PR #6, merge 3b92e3816d78f8ee9596c87a76e937f276d3344c, implementation c5567a5d8c08be59d96cb5db07bc518ca8c9f332. Grains 3Def/5localization legacy copies and 2 MO starting operations now use provider-absence guards. Actual separate repository pair passed six explicit XML configurations. Grains PR CI Stage A 37614452046 and Workshop 37614451954 succeeded; these do not compile C# or run RimWorld. Scenarios metadata/README now require the guarded Grains version when combined. Runtime/start/save tests and scenario runtime-test ownership transfer remain next; standalone RawRice 300 remains draft.
