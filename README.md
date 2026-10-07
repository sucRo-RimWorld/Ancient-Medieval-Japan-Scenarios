# Ancient & Medieval Japan - Scenarios

独立した開始シナリオModの開発候補です。packageIdは `sucro.ancientmedievaljapan.scenarios`。
Grainsとは別リポジトリで所有・配布します。専用リポジトリ: https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Scenarios 。

Vanillaを基盤とし、AMJ Grains（現行CoreのpackageId）とMedieval Overhaulは任意互換です。
AMJC_NewVillage、AMJC_PlayerVillage、AMJC_Villagerと開始ダイアログを維持します。
MO互換の後にGrains互換を適用します。単独開始のRawRice 300は数量未承認の試案です。

## 移行とセーブ

現行の未移行Coreとの併用はDefが重複します。Core側を条件付きLegacy領域へ移す更新が先に必要です。
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
