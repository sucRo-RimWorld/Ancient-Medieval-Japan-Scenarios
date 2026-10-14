# Scenarios実行時テストの所有と手順

Scenariosが開始用Scenario/Faction/PawnKind・物資・研究・服装と実際の開始を検証する。
Grainsは穀物・一次加工・製粉・食事・環境・通常Billを検証し、開始Defを提供しない。
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

コピーのAbout名・packageId・依存／loadAfterはテスト用に変更する。Grainsには旧シナリオのDefも互換領域も存在しないことを配置前に検証する。GrainsのMO条件は変更しない。

## Windows実行

RimWorld 1.6、実MO（該当構成）、Harmony、RimLogging、Pickle、Quickstartsをインストールする。
Grains併用では更新済みGrainsリポジトリを入力する。Framework C#コンパイラでQuickstartとPickle stepsを別DLLへビルドする。

```powershell
powershell -NoProfile -File Scripts/IntegratedRuntimeDesktop/Run-Scenarios-IsolatedDesktop.ps1 -RimWorldRoot "D:\SteamLibrary\steamapps\common\RimWorld" -GrainsRepositoryRoot "D:\AMJ\Ancient-Medieval-Japan-Grains" -Profile all
```

通常入口はprivate desktopランチャーとする。描画を無効化せず、表示先をユーザーのデスクトップから隔離する。
内部Run-ScenarioProfiles.ps1を直接起動すると可視ウィンドウを出し得るため、通常の自動実行には使わない。
Project の専用Linux 1.6ホストで Xvfb / Pickle による独立した新規開始・所有境界E2Eを実装済み。Windows 4構成テストとは独立しており、MOを含む2構成とシナリオ選択画面のピクセル・クリック検証を代替しない。

各構成でfresh summaryが指定した3件すべて成功・失敗0・skip0であることと、隔離ログのERROR 0を両方要求する。
プロセス失敗・タイムアウト時も両ゲートを確認する。警告は通常非致命、任意Mod由来ERRORも失敗とする。
300秒／構成、1800秒／全体。ロック・fresh出力・ソースコミットとSHA-256・DLL／プロバイダの全配置ハッシュを保存する。

## 検証の境界と残作業

ローカル／CIのPowerShellテストは仮のインストール台帳・結果・ログを用いた配置／制御のテストであり、
表示された3/3はゲームの実行結果ではない。C#ソースのコンパイル・ゲーム実行・private desktop上の描画は別ゲート。
通常のGitHubホストランナーにはゲームManaged assembliesがないが、専用のライセンス済みLinux 1.6ホストで実機テストを実施できる。後述の実行記録以外の構成やUI描画は未検証。

ゲーム実行ハーネスは新規開始専用。旧 Core / Grains シナリオセーブは公開・実プレイ前で存在しないため、旧セーブ移行ゲートと合成XML移行テストは廃止済み。

残作業：実ゲーム環境で Vanilla / Grains / MO / Grains＋MO の4構成をコンパイルして新規開始し、シナリオ定義の一意性、5人の生成、物資・初期研究、派閥参照、全ログ ERROR 0、表示を検証する。

## Linux 1.6実ゲーム検証済み（2026-10-14、対象ソース固定）

Project の独立Linuxランナー（ライセンス済み RimWorld 1.6.4871 rev600、Xvfb + Pickle）で、Grains `9e1898de7104cd951349c6fc0da8ce870626721c` と Scenarios `bf931a6ee0eb9691db16b5edfe3c40c62821f6b5` を厳密に固定して実行した。テスト用Mod IDの別名化以外、Scenario/Faction/PawnKind本番XMLは変えていない。

- [所有境界 Actions #38525733684](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/actions/runs/38525733684)：Grains単体（3開始Defなし）、Scenarios単体（3開始Def各1件）、Grains＋Scenarios（各1件）の**3構成×1シナリオ＝3/3 PASS**。全プロファイル正常終了、ERROR 0。ロード済みのDef・partsの存在確認であり、当時の検証は選択画面リストを直接検査していない。
- [開始 E2E Actions #38526753894](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/actions/runs/38526753894)：Scenarios単体およびScenarios＋Grains、各3件（要求プロバイダ、5人/派閥/研究/物資の定義、Quickstartからの実コロニー開始）＝**6/6 PASS**。両構成ともゲーム終了コード0、ERROR 0、Pickle `exitReason=passed`。検証結果とnative UnityログはActions artifactに保存。
- [選択候補リスト Actions #38532021950](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/actions/runs/38532021950)：本物の RimWorld 1.6 が用いる `ScenarioLister.ScenariosInCategory(ScenarioCategory.FromDef)` で候補の存在を検証。Grains単体は開始Defなし。Scenarios単体／Grains＋Scenariosは `AMJC_NewVillage` のScenario参照が候補に**正確に1件**、`ScenarioIsListedAnywhere` も真。**3/3 PASS、全構成exit0、ERROR0**。画面の画像を撮って確かめたものではない。


**未検証：** Scenarios＋MO、Scenarios＋Grains＋MOの本番新規開始、1.7、シナリオ選択画面を実際に描画したスクリーンショット・クリック操作、長期プレイ、Workshop反映。ここに挙げた実機6件を、未実施構成やUIピクセルに拡大解釈しない。
