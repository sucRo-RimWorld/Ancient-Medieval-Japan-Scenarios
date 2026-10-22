# Ancient & Medieval Japan - Scenarios（中世日本 - シナリオ）

独立した開始シナリオModの開発版です。現時点ではWorkshop公開を確認していません。packageIdは `sucro.ancientmedievaljapan.scenarios`。
Grainsとは別リポジトリで所有・配布します。専用リポジトリ: https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Scenarios 。

Vanillaを基盤とし、[AMJ Grains](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Grains)（旧CoreのpackageIdを維持）とMedieval Overhaulは任意互換です。
AMJC_NewVillage、AMJC_PlayerVillage、AMJC_Villagerと開始ダイアログを維持します。
MO互換の後にGrains互換を適用します。単独開始のRawRice 300は数量未承認の試案です。

## 所有と依存

Grainsは開始用Scenario/Faction/PawnKind/翻訳を一切同梱しません。Scenariosだけが `AMJC_NewVillage`、`AMJC_PlayerVillage`、`AMJC_Villager` を提供します。Grains非導入のVanilla単独でも開始でき、GrainsとMOは任意互換です。

旧Coreと旧Grainsの未公開シナリオ・セーブに対する移行互換は採用しません。Grains本番の `LegacyStartingScenarios/` は削除済みです。RimWorld 1.6では、Scenarios単体・Grains併用・MO併用・Grains+MO併用の4構成で新規開始と開始物資を検証し、各3件（計12件）のゲーム内シナリオが成功しています。ただし元のMO/SYR音声ファイル使用時には既知のFMODエラーが残り、その環境の厳密なERROR0判定は不合格です。別途、問題の音声を一時的にWAV変換した隔離環境では12/12、Unity ERROR0を確認しました。表示UI、RimWorld 1.7、既存セーブ移行とWorkshop配布物は未検証です。

## 検証

`python Tests/test_scenarios.py` は4構成の明示XML、任意互換の条件・順序、保存用識別子を検証します。
静的PASSは継承・実ゲーム起動・開始・セーブ成功を意味しません。
NewVillageStepsとQuickstartをScenariosへ移管しました。4構成×3件の実機検証結果と制限は下記手順書に記録しています。
手順と未検証範囲は [Docs/RuntimeTesting.md](Docs/RuntimeTesting.md)。
実機検証ではUnity ERRORの原記録を維持し、MO/SYRに由来する既知の音声エラーも厳密なERROR0判定から除外していません。

抽出元と入力SHA-256は `Docs/ExtractionProvenance.json` に記録しています。
`.rimignore` は購読者に不要なソース・テスト・文書を配布対象から除きます。

Grainsのリポジトリ改名はpackageId変更ではありません。任意互換の条件は引き続き `sucro.ancientmedievaljapan.core` です。
