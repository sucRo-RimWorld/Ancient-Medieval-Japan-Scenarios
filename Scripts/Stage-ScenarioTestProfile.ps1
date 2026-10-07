param(
 [Parameter(Mandatory=$true)][string]$RepositoryRoot,
 [Parameter(Mandatory=$true)][string]$ModsRoot,
 [ValidateSet('vanilla','grains','mo','grains-mo')][string]$Profile='vanilla',
 [string]$GrainsRepositoryRoot
)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'ScenarioTestProfiles.ps1')
$spec=Get-ScenarioTestProfile $Profile
$RepositoryRoot=(Resolve-Path -LiteralPath $RepositoryRoot).Path
$target=Join-Path $ModsRoot 'AncientMedievalJapanScenarios.E2ETarget'
$test=Join-Path $ModsRoot 'AncientMedievalJapanScenarios.E2E'
$grainTarget=Join-Path $ModsRoot 'AncientMedievalJapanScenarios.GrainsTarget'
# Fail before replacing generated targets if the optional source is old or missing.
if ($spec.UseGrains) {
 if (-not $GrainsRepositoryRoot) { throw 'GrainsRepositoryRoot is required for the Grains profiles.' }
 $GrainsRepositoryRoot=(Resolve-Path -LiteralPath $GrainsRepositoryRoot).Path
 [xml]$grainLoader=Get-Content -LiteralPath (Join-Path $GrainsRepositoryRoot 'loadFolders.xml') -Raw -Encoding UTF8
 $guards=@($grainLoader.SelectNodes('/loadFolders/v1.6/li[@IfModNotActive="sucro.ancientmedievaljapan.scenarios"]'))
 if ($guards.Count -ne 2 -or [string]$guards[0].InnerText -ne 'LegacyStartingScenarios' -or [string]$guards[1].InnerText -ne 'LegacyStartingScenarios/Compatibility/MedievalOverhaul' -or $guards[1].GetAttribute('IfModActive') -ne 'DankPyon.Medieval.Overhaul') { throw 'Grains must have both guarded LegacyStartingScenarios roots and the MO-positive guard.' }
}
foreach ($path in @($target,$test,$grainTarget)) {
 if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Recurse -Force }
}
function Stage-Runtime([string]$Source,[string]$Destination,[string]$Id,[string[]]$After) {
 New-Item -ItemType Directory -Force -Path (Join-Path $Destination 'About') | Out-Null
 foreach ($folder in @('Defs','Patches','Textures','Languages','Compatibility','BaseWithoutMO','LegacyStartingScenarios','Assemblies','1.6')) {
  $from=Join-Path $Source $folder
  if (Test-Path -LiteralPath $from) { Copy-Item -LiteralPath $from -Destination $Destination -Recurse }
 }
 Copy-Item -LiteralPath (Join-Path $Source 'loadFolders.xml') -Destination $Destination
 [xml]$about=Get-Content -LiteralPath (Join-Path $Source 'About/About.xml') -Raw -Encoding UTF8
 $about.ModMetaData.name='[DEV] '+$Id
 $about.ModMetaData.packageId=$Id
 $about.ModMetaData.description='Disposable Scenario test target; metadata and provider aliases differ. Do not publish.'
 foreach ($node in @($about.ModMetaData.SelectNodes('modDependencies|loadAfter'))) { [void]$about.ModMetaData.RemoveChild($node) }
 $afterNode=$about.CreateElement('loadAfter')
 foreach ($provider in $After) { $li=$about.CreateElement('li');$li.InnerText=$provider;[void]$afterNode.AppendChild($li) }
 [void]$about.ModMetaData.AppendChild($afterNode)
 $about.Save((Join-Path $Destination 'About/About.xml'))
}
if ($spec.UseGrains) {
 Stage-Runtime $GrainsRepositoryRoot $grainTarget 'sucro.ancientmedievaljapan.core.scenariose2etarget' @('dankpyon.medieval.overhaul')
 foreach ($guard in $guards) { $guard.SetAttribute('IfModNotActive','sucro.ancientmedievaljapan.scenarios.e2etarget') }
 $grainLoader.Save((Join-Path $grainTarget 'loadFolders.xml'))
}
Stage-Runtime $RepositoryRoot $target 'sucro.ancientmedievaljapan.scenarios.e2etarget' @('dankpyon.medieval.overhaul','sucro.ancientmedievaljapan.core.scenariose2etarget')
[xml]$loader=Get-Content -LiteralPath (Join-Path $target 'loadFolders.xml') -Raw -Encoding UTF8
$grain=@($loader.SelectNodes('/loadFolders/v1.6/li[@IfModActive="sucro.ancientmedievaljapan.core"]'))
if ($grain.Count -ne 1) { throw 'Expected one optional Grains integration root.' }
$grain[0].SetAttribute('IfModActive','sucro.ancientmedievaljapan.core.scenariose2etarget')
$loader.Save((Join-Path $target 'loadFolders.xml'))
foreach ($folder in @('About','Assemblies','Pickle/Assemblies','Pickle/Features')) { New-Item -ItemType Directory -Force -Path (Join-Path $test $folder) | Out-Null }
Copy-Item -LiteralPath (Join-Path $RepositoryRoot 'Tests/E2E/TestMod/About/About.xml') -Destination (Join-Path $test 'About/About.xml')
Copy-Item -LiteralPath (Join-Path $RepositoryRoot "Tests/E2E/Profiles/$($spec.Feature)") -Destination (Join-Path $test 'Pickle/Features')
$spec | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $test 'profile.json') -Encoding UTF8
Write-Host "[OK] Staged Scenario $Profile. Only disposable About/provider aliases differ; runtime Def/Patch/language/texture bytes preserved."
