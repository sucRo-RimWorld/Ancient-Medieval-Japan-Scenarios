# Ancient & Medieval Japan - Scenarios（中世日本 - シナリオ）

独立した開始シナリオModの開発候補です。packageIdは `sucro.ancientmedievaljapan.scenarios`。
Grainsとは別リポジトリで所有・配布します。専用リポジトリ: https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Scenarios 。

Vanillaを基盤とし、[AMJ Grains](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Grains)（旧CoreのpackageIdを維持）とMedieval Overhaulは任意互換です。
AMJC_NewVillage、AMJC_PlayerVillage、AMJC_Villagerと開始ダイアログを維持します。
MO互換の後にGrains互換を適用します。単独開始のRawRice 300は数量未承認の試案です。

## 所有と依存

Grainsは開始用Scenario/Faction/PawnKind/翻訳を一切同梱しません。Scenariosだけが `AMJC_NewVillage`、`AMJC_PlayerVillage`、`AMJC_Villager` を提供します。Grains非導入のVanilla単独でも開始でき、GrainsとMOは任意互換です。

旧Coreと旧Grainsの未公開シナリオ・セーブに対する移行互換は採用しません。Grains本番の `LegacyStartingScenarios/` は削除済みです。新規開始のゲーム動作は独立した実機テストで検証します。

## 検証

`python Tests/test_scenarios.py` は4構成の明示XML、任意互換の条件・順序、保存用識別子を検証します。
静的PASSは継承・実ゲーム起動・開始・セーブ成功を意味しません。
NewVillageStepsとQuickstartをScenariosへ移管し、4構成×3件の実行時テストソースとWindows隔離ランナーを用意しました。
手順と未検証範囲は [Docs/RuntimeTesting.md](Docs/RuntimeTesting.md)。
実行時テストは非表示で描画経路を維持し、対象Mod由来ERRORを全体失敗として扱います。

抽出元と入力SHA-256は `Docs/ExtractionProvenance.json` に記録しています。
`.rimignore` は購読者に不要なソース・テスト・文書を配布対象から除きます。

Grainsのリポジトリ改名はpackageId変更ではありません。任意互換の条件は引き続き `sucro.ancientmedievaljapan.core` です。
