# Scenarios実行時テストの所有と手順

Scenariosが開始用Scenario/Faction/PawnKind・物資・研究・服装と実際の開始を検証する。
Grainsは穀物・一次加工・製粉・食事・環境・通常Billを検証し、旧シナリオ互換用コピーの回帰だけを残す。
ScenariosのNewVillageSteps、RuntimeThread、Quickstartおよび汎用ランナー部は、
Grains `faa2cedaa145811e9bb23598b5f11d78bb090984` のMITソースを基に移管・適応した。
汎用スクリプトはその初期の動作を維持しつつ、このリポジトリが独立して管理する。
ゲーム実行のためにGrainsのテストDLLを参照せず、Grainsは任意構成のソース入力だけとする。

| プロファイル | 対象Mod | 必須Pickle 3件 |
|---|---|---|
| vanilla | Scenarios | 提供元・ロード済み開始Def・実際の開始 |
| grains | Scenarios＋Grains | 同上 |
| mo | Scenarios＋MO | 同上 |
| grains-mo | Scenarios＋Grains＋MO | 同上 |

実際の開始は本番のAMJC_NewVillageを選び、5人の種類・Faction、初期研究、全約束物資、武器素材を確認する。
開始物資をテスト側で生成せず、Scenarioのpartsも差し替えない。物資のDef設定値は厳密に比較し、
実マップでは自然生成品が混ざるため最低保証数を確認する。Grainsなしは試案RawRice 300、ありはMillet 200＋RawMillet 100。
MOなしはPemmican 1080／研究なし、ありはMO携行食・素材・3研究を確認する。

## 配置と隔離

通常ModsConfig.xml・Prefs.xmlは参照するだけ。プロファイル別SaveData・ログ・Pickle結果へ書き、
ユーザーのactiveModsを再利用せず、宣言された必須依存だけを解決する。重複インストール・循環・禁止依存を拒否する。
API fixture、実ゲーム用のCore/Scenarios packageId、CCTOをテスト構成へ混ぜない。

生成先はゲームのMods配下にあるScenarios専用のE2ETarget／E2E／GrainsTargetのみ。
Grains通常テストのE2ETargetを消したり書き換えたりしない。
テスト用packageIdに合わせて、コピー側だけ以下のloader条件を別名へ対応させる。
本番ソースのloadFolders.xml、Def/Patch、翻訳、画像は変更しない。

| コピー | 別名対応 |
|---|---|
| Scenarios | 任意Grains条件→`sucro.ancientmedievaljapan.core.scenariose2etarget` |
| Grains | Legacy領域の2つのScenarios不在条件→`sucro.ancientmedievaljapan.scenarios.e2etarget` |

コピーのAbout名・packageId・依存／loadAfterもテスト用に変更する。GrainsのMO依存を外すのはコピーだけ。
MOの存在条件とLegacy MOのAND条件は維持する。旧Grainsにガードがなければ配置前に失敗させる。

## Windows実行

RimWorld 1.6、実MO（該当構成）、Harmony、RimLogging、Pickle、Quickstartsをインストールする。
Grains併用では更新済みGrainsリポジトリを入力する。Framework C#コンパイラでQuickstartとPickle stepsを別DLLへビルドする。

```powershell
powershell -NoProfile -File Scripts/IntegratedRuntimeDesktop/Run-Scenarios-IsolatedDesktop.ps1 -RimWorldRoot "D:\SteamLibrary\steamapps\common\RimWorld" -GrainsRepositoryRoot "D:\AMJ\Ancient-Medieval-Japan-Grains" -Profile all
```

通常入口はprivate desktopランチャーとする。描画を無効化せず、表示先をユーザーのデスクトップから隔離する。
内部Run-ScenarioProfiles.ps1を直接起動すると可視ウィンドウを出し得るため、通常の自動実行には使わない。
Linux対応はまだ実装していない。Xvfb等の隔離と同じゲートを用意するまでWindows経路を使う。

各構成でfresh summaryが指定した3件すべて成功・失敗0・skip0であることと、隔離ログのERROR 0を両方要求する。
プロセス失敗・タイムアウト時も両ゲートを確認する。警告は通常非致命、任意Mod由来ERRORも失敗とする。
300秒／構成、1800秒／全体。ロック・fresh出力・ソースコミットとSHA-256・DLL／プロバイダの全配置ハッシュを保存する。

## 検証の境界と残作業

ローカル／CIのPowerShellテストは仮のインストール台帳・結果・ログを用いた配置／制御のテストであり、
表示された3/3はゲームの実行結果ではない。C#ソースのコンパイル・ゲーム実行・private desktop上の描画は別ゲート。
クラウド作業環境にはゲームManaged assembliesがないため、これらは未実施。

ゲーム実行ハーネスは新規開始専用。旧セーブの入力コピー／再保存XML比較ゲートは[SaveMigrationTesting.md](SaveMigrationTesting.md)に記録する。
旧セーブ読込／再保存／Scenarios追加・削除・提供元切替をゲーム内で実行する自動テストは未実装。
次は実ゲーム環境で4構成をコンパイル・起動し、旧Grainsで生成した保存済みFaction・PawnKind・Scenario partsを含む
セーブを固定fixtureとして作成する。追加・切替・再保存・削除をそれぞれ隔離して検証し、
初期物資／研究が既存セーブに再配布されないことも確認する。GrainsやMOの安全な削除をこのテストで保証しない。
