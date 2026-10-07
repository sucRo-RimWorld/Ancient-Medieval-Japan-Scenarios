# 旧セーブ移行テストの入力と比較ゲート

Scenariosが旧New Villageの開始Def提供元切替を検証する。GrainsとMOは残したまま、
旧Core由来の保存済みScenario parts・Faction・PawnKindが保持されることを確認する。
この手順の準備とXML比較は自動化済み。ゲーム内の保存・読込・再保存、テスト結果収集はまだ未実装である。
新規開始ランナーを旧セーブへ流用しない。新規開始の3/3をセーブ移行結果として扱わない。

## 入力

RimWorld 1.6の実ゲームで旧Grains/Core＋MOのAMJC_NewVillageを開始し、5人以上のAMJC_Villagerが
マップ上に存在する状態で一時停止して保存したUTF-8 `.rws` を入力にする。通常プレイ中の長期セーブは
この固定fixture契約に合うとは限らない。元セーブは読み取りのみで、Mod IDやDefNameを修正しない。
実セーブは公開リポジトリへcommitせず、ローカルTestResults以下に保持する。

以下のコマンドのSHAは、実際の保存元旧Grains、検証に使う更新済みGrains、Scenariosの完全な40桁を入力する。
コマンドはSHAの形式を検査し、入力値として記録する。保存元の実ソースや実行事実をSHAだけで認証するものではない。
現在のsource-state／DLL／providerハッシュと、旧保存元の実行記録を別途収集する必要がある。

```powershell
python Scripts/scenario_save_contract.py prepare --save "D:\AMJ-TestFixtures\legacy-new-village.rws" --output "TestResults\SaveMigration\run-001" --legacy-commit $LegacyGrainsSha --grains-commit $UpdatedGrainsSha --scenarios-commit $ScenariosSha
```

出力先は新規ディレクトリ限定。既存結果の消去・上書きは行わない。入力をバイト一致でコピーし、SHA-256と
構造のスナップショットをplan.jsonへ記録する。結果のstatusは`prepared-not-run`、runtimeVerifiedは常にfalse。
テスト用packageId／API fixtureが混ざる入力、重複Mod ID、Grains/MO不在、Scenarios導入済み、未対応XML構造は拒否する。

## ケース順と依存

| ケース | 入力 | 使用する開始Def提供元 | 必要な構成変更 |
|---|---|---|---|
| guarded-legacy | 元の旧セーブコピー | 更新済みGrainsのLegacy | Scenariosなし、Grains更新 |
| add-scenarios | 元の旧セーブコピー | Scenarios | 更新済みGrains＋MOにScenarios追加 |
| reload-scenarios | add-scenariosが実ゲームで再保存したセーブ | Scenarios | 同じ構成で再読込・再保存 |
| remove-scenarios | add-scenariosが実ゲームで再保存したセーブ | 更新済みGrainsのLegacy | Scenariosのみ削除 |

最初の2ケースにはinput.rwsをコピーする。後の2ケースには元の旧セーブをコピーしない。
Scenarios導入後の実再保存ファイルができるまで入力は欠番とし、元セーブで削除テストを代用させない。
各ケースの実出力は`ケース名/resaved.rws`として扱う。保存元Grainsから更新済みGrainsへの実配置を記録する。

元セーブのmeta/modIdsをテスト用別名へ書き換えて「互換確認」にしない。この入力契約は本番packageIdを要求する。
既存の新規開始用E2ETarget別名とは別に、隔離した本番ID構成と旧セーブをロードするゲーム用アダプターが必要である。
現在のRun-ScenarioProfiles.ps1やprivate desktopラッパーは旧セーブをロードしない。

## 再保存XMLの比較

例は追加ケース。削除ではbeforeをadd-scenarios/resaved.rwsにし、transitionをremove-scenariosにする。
同一構成の再読込とguarded-legacyはsame-providersを指定する。

```powershell
python Scripts/scenario_save_contract.py compare --before "TestResults\SaveMigration\run-001\add-scenarios\input.rws" --after "TestResults\SaveMigration\run-001\add-scenarios\resaved.rws" --transition add-scenarios
```

比較はゲーム版一致、許可したScenariosだけのMod構成変更、Grains/MO維持に加えて次を要求する。

- ticksGame一致。一時停止した読込・保存だけを対象にし、シミュレーションの進行と移行不具合を混同しない。
- Scenario全体と唯一のAMJC_PlayerVillage Factionの保存構造一致。
- マップ上のAMJC_VillagerのID・PawnKind・Faction参照一致。5人未満、重複ID、参照不一致を拒否。
- 各マップ・ポーンのinventoryやequipmentなど、入れ子も含めた保存済みthingのDef別個数一致。
- researchManager全体一致。開始研究の再適用と物資再配布を比較対象に含める。

XMLのインデント／属性順は無視し、子ノード順と値は保持する。未対応の保存構造は空の結果にせず失敗させる。
現在の抽出パスは`game/scenario`、`game/world/factionManager/allFactions`、`game/maps`、
`game/researchManager`、`game/tickManager/ticksGame`を要求する限定アダプターである。
実1.6セーブをこの環境で検査していないため、実fixtureとの照合は残ゲート。形式差異があればサンプルに基づいて
アダプターを修正する。契約を満たすために元セーブを加工しない。

成功出力は`xml-contracts-checked`／runtimeVerified=false、失敗は終了コード2。
全保存データを比較するものではなく、個々の非AMJC Pawn状態・全世界参照・各種Mod componentなどは保証しない。
テストは合成XMLであり、実セーブfixtureやゲームのロード成功を装わない。

## 実行時ゲート

XML比較だけで移行PASS・リリース可・安全な削除とはしない。次にゲーム用アダプターを実装して、
private desktopで通常描画を保持し、各ケースを別プロセス・別SaveData・fresh結果・タイムアウト付きで実行する。
実ロード後のScenario/Faction/PawnKind解決と既存ポーン・物資・研究をゲーム内で確認し、再保存を出力する。
各ケースの正確なPickle件数、ソース／DLL／providerハッシュ、入力・出力セーブSHA-256、全ERROR 0を要求する。
元セーブのMod不一致のために通常ユーザー構成を自動切替する処理は入れない。

GrainsやMOの削除、提供元パッケージの上書きインストール、別版ゲームへの移行はこのケース群では未検証。
穀物やMO固有アイテム・建築物などを失う可能性があるため、それぞれの専用移行契約が通るまで削除を案内しない。
旧互換Defの削除とGrains AboutのMO依存解除も、対応する実行時・画像・保存ゲートが通るまで保留する。
