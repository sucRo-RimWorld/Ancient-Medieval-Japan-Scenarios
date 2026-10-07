param([Parameter(Mandatory=$true)][string]$GrainsRepositoryRoot)
$ErrorActionPreference='Stop'
$repo=Split-Path -Parent $PSScriptRoot
. (Join-Path $repo 'Scripts/ScenarioTestProfiles.ps1')
function Assert([bool]$Value,[string]$Message) { if (-not $Value) { throw $Message } }
function MustFail([scriptblock]$Action,[string]$Message) { $failed=$false;try { & $Action } catch { $failed=$true };Assert $failed $Message }
$temp=Join-Path ([IO.Path]::GetTempPath()) ('AMJ-Scenario-'+[Guid]::NewGuid().ToString('N'))
$game=Join-Path $temp 'steamapps/common/RimWorld'
$mods=Join-Path $game 'Mods'
$config=Join-Path $temp 'NormalConfig'
New-Item -ItemType Directory -Force -Path $mods,$config | Out-Null
function Metadata([string]$Id) { [xml]"<ModMetaData><name>$Id</name><packageId>$Id</packageId><supportedVersions><li>1.6</li></supportedVersions></ModMetaData>" }
function Install([string]$Id,[string]$Root) {
 New-Item -ItemType Directory -Force -Path (Join-Path $Root 'About') | Out-Null
 (Metadata $Id).Save((Join-Path $Root 'About/About.xml'))
}
try {
 Install 'ludeon.rimworld' (Join-Path $game 'Data/Core')
 foreach ($id in @('brrainz.harmony','rimworks.rimlogging','rimworks.pickle','rimworks.quickstarts','dankpyon.medieval.overhaul','unrelated.player.mod')) { Install $id (Join-Path $mods $id) }
 '<ModsConfigData><version>1.6.4633</version><activeMods><li>unrelated.player.mod</li></activeMods><knownExpansions/></ModsConfigData>' | Set-Content (Join-Path $config 'ModsConfig.xml')
 '<Prefs><devMode>False</devMode></Prefs>' | Set-Content (Join-Path $config 'Prefs.xml')
 $normalHash=(Get-FileHash (Join-Path $config 'ModsConfig.xml')).Hash
 $sourceLoader=(Get-FileHash (Join-Path $GrainsRepositoryRoot 'loadFolders.xml')).Hash
 foreach ($name in @('vanilla','grains','mo','grains-mo')) {
  $spec=Get-ScenarioTestProfile $name
  & (Join-Path $repo 'Scripts/Stage-ScenarioTestProfile.ps1') -RepositoryRoot $repo -ModsRoot $mods -Profile $name -GrainsRepositoryRoot $GrainsRepositoryRoot
  $target=Join-Path $mods 'AncientMedievalJapanScenarios.E2ETarget'
  foreach ($folder in @('Defs','Languages','Compatibility')) {
   foreach ($file in Get-ChildItem -LiteralPath (Join-Path $repo $folder) -Recurse -File) {
    $relative=$file.FullName.Substring($repo.Length+1)
    Assert ((Get-FileHash $file.FullName).Hash -eq (Get-FileHash (Join-Path $target $relative)).Hash) "Scenario runtime bytes changed: $relative"
   }
  }
  [xml]$loader=Get-Content (Join-Path $target 'loadFolders.xml') -Raw
  Assert ($loader.loadFolders.'v1.6'.li[2].IfModActive -eq 'sucro.ancientmedievaljapan.core.scenariose2etarget') 'Optional Grains alias missing.'
  $grainTarget=Join-Path $mods 'AncientMedievalJapanScenarios.GrainsTarget'
  Assert ((Test-Path $grainTarget) -eq $spec.UseGrains) 'Unrequested Grains target present.'
  if ($spec.UseGrains) {
   [xml]$guards=Get-Content (Join-Path $grainTarget 'loadFolders.xml') -Raw
   Assert (@($guards.SelectNodes('/loadFolders/v1.6/li[@IfModNotActive="sucro.ancientmedievaljapan.scenarios.e2etarget"]')).Count -eq 2) 'Legacy exclusion aliases lost.'
   foreach ($folder in @('Defs','Languages','Compatibility','BaseWithoutMO','LegacyStartingScenarios','Textures')) {
    foreach ($file in Get-ChildItem -LiteralPath (Join-Path $GrainsRepositoryRoot $folder) -Recurse -File) {
     $relative=$file.FullName.Substring((Resolve-Path $GrainsRepositoryRoot).Path.Length+1)
     Assert ((Get-FileHash $file.FullName).Hash -eq (Get-FileHash (Join-Path $grainTarget $relative)).Hash) "Grains runtime bytes changed: $relative"
    }
   }
  }
  $output=Join-Path $temp $name
  & (Join-Path $repo 'Scripts/Prepare-TestSaveData.ps1') -OutputRoot $output -Profile $name -RimWorldRoot $game -SourceModsConfigPath (Join-Path $config 'ModsConfig.xml')
  Assert ($LASTEXITCODE -eq 0) 'Config creation failed.'
  [xml]$actual=Get-Content (Join-Path $output 'Config/ModsConfig.xml') -Raw
  $ids=@($actual.ModsConfigData.activeMods.li)
  Assert (($ids -contains 'dankpyon.medieval.overhaul') -eq $spec.UseMO) 'MO provider isolation failed.'
  Assert (($ids -contains 'sucro.ancientmedievaljapan.core.scenariose2etarget') -eq $spec.UseGrains) 'Grains provider isolation failed.'
  Assert (-not ($ids -contains 'unrelated.player.mod')) 'Player active list leaked.'
  Assert ($ids -contains 'sucro.ancientmedievaljapan.scenarios.e2etarget') 'Scenario provider absent.'
  $summary=Join-Path $temp 'summary.json'
  @{total=3;passed=3;failed=0;skipped=0;scenarios=@($spec.Scenarios|ForEach-Object{@{name=$_}})} | ConvertTo-Json -Depth 5 | Set-Content $summary
  & (Join-Path $repo 'Scripts/Validate-ScenarioPickleSummary.ps1') -SummaryPath $summary -Profile $name
  @{total=3;passed=3;failed=0;skipped=0;scenarios=@(@{name='wrong owner suite'})} | ConvertTo-Json -Depth 5 | Set-Content $summary
  MustFail { & (Join-Path $repo 'Scripts/Validate-ScenarioPickleSummary.ps1') -SummaryPath $summary -Profile $name } 'Wrong summary accepted.'
 }
 Assert ((Get-FileHash (Join-Path $config 'ModsConfig.xml')).Hash -eq $normalHash) 'Player config altered.'
 Assert ((Get-FileHash (Join-Path $GrainsRepositoryRoot 'loadFolders.xml')).Hash -eq $sourceLoader) 'Production Grains loader altered.'
 $installed=@{}
 foreach ($id in @('brrainz.harmony','ludeon.rimworld','rimworks.rimlogging','rimworks.pickle','rimworks.quickstarts','sucro.ancientmedievaljapan.scenarios.e2etarget','sucro.ancientmedievaljapan.scenarios.e2e','dankpyon.medieval.overhaul')) { $installed[$id]=[pscustomobject]@{Xml=(Metadata $id)} }
 [xml]$installed['rimworks.rimlogging'].Xml='<ModMetaData><modDependencies><li><packageId>dankpyon.medieval.overhaul</packageId></li></modDependencies></ModMetaData>'
 MustFail { Get-ScenarioActiveMods (Get-ScenarioTestProfile 'vanilla') $installed } 'Forbidden transitive MO dependency accepted.'
 $duplicate=Join-Path $mods 'duplicate-pickle';Install 'rimworks.pickle' $duplicate
 MustFail { & (Join-Path $repo 'Scripts/Prepare-TestSaveData.ps1') -OutputRoot (Join-Path $temp 'duplicate') -Profile 'mo' -RimWorldRoot $game -SourceModsConfigPath (Join-Path $config 'ModsConfig.xml') } 'Ambiguous installed framework accepted.'
 $log=Join-Path $temp 'Player.log'
 '[WARNING] Nonfatal example' | Set-Content $log
 & (Join-Path $repo 'Scripts/Validate-RuntimeLog.ps1') -LogPath $log -ModIdPrefixes sucro.ancientmedievaljapan.scenarios -FailOnAnyError
 Assert ($LASTEXITCODE -eq 0) 'Warning-only log rejected.'
 '[ERROR] [AMJ.Scenarios] synthetic test error' | Set-Content $log
 & (Join-Path $repo 'Scripts/Validate-RuntimeLog.ps1') -LogPath $log -ModIdPrefixes sucro.ancientmedievaljapan.scenarios -FailOnAnyError
 Assert ($LASTEXITCODE -ne 0) 'ERROR log accepted.'
 Write-Host '[OK] Four Scenario profile staging/config/summary/negative tooling checks; no game run claimed.'
} finally { if (Test-Path $temp) { Remove-Item -LiteralPath $temp -Recurse -Force } }

# The expected ERROR-negative leaves LASTEXITCODE=1; report suite success explicitly.
exit 0
