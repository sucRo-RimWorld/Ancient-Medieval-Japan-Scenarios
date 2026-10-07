# Ancient & Medieval Japan - Scenarios

独立した開始シナリオModの開発候補です。packageIdは `sucro.ancientmedievaljapan.scenarios`。
Grainsとは別リポジトリで所有・配布します。専用リポジトリ: https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Scenarios 。

Vanillaを基盤とし、[AMJ Grains](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Grains)（旧CoreのpackageIdを維持）とMedieval Overhaulは任意互換です。
AMJC_NewVillage、AMJC_PlayerVillage、AMJC_Villagerと開始ダイアログを維持します。
MO互換の後にGrains互換を適用します。単独開始のRawRice 300は数量未承認の試案です。

## 移行とセーブ

旧Core／移行前Grainsとの併用はDefが重複します。Grains側は [移行対応コミット3b92e381](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Grains/commit/3b92e3816d78f8ee9596c87a76e937f276d3344c) 以降を使用します。
更新版ではScenarios有効時にGrainsの互換用3Def・翻訳・MO開始差分を読み込まず、提供元を一つにします。
両リポジトリの6構成の静的検証は通過しましたが、実ゲームでの併用・セーブ移行成功は未検証です。
この候補はまだ実際のMods構成へ設置しないでください。
既存セーブへの追加・削除・提供元切替は未検証です。旧セーブの穀物・設備をこのModだけでは提供できません。
既存セーブへ開始物資・研究を再付与しません。

## 検証

`python Tests/test_scenarios.py` は4構成の明示XML、任意互換の条件・順序、保存用識別子を検証します。
静的PASSは継承・実ゲーム起動・開始・セーブ成功を意味しません。
NewVillageStepsとQuickstartの実行時テスト移管、旧セーブ・追加・削除の自動テストは次の実装です。
実行時テストは非表示で描画経路を維持し、対象Mod由来ERRORを全体失敗として扱います。

抽出元と入力SHA-256は `Docs/ExtractionProvenance.json` に記録しています。
`.rimignore` は購読者に不要なソース・テスト・文書を配布対象から除きます。

Grainsのリポジトリ改名はpackageId変更ではありません。任意互換の条件は引き続き `sucro.ancientmedievaljapan.core` です。
