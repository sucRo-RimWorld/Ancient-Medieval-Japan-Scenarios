param(
 [Parameter(Mandatory=$true)][string]$RimWorldRoot,
 [ValidateSet('vanilla','grains','mo','grains-mo')][string]$Profile='vanilla',
 [string]$GrainsRepositoryRoot
)
$ErrorActionPreference='Stop'
$repo=Split-Path -Parent $PSScriptRoot
$csc=Join-Path $env:WINDIR 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
if (-not (Test-Path -LiteralPath $csc)) { $csc=Join-Path $env:WINDIR 'Microsoft.NET/Framework/v4.0.30319/csc.exe' }
if (-not (Test-Path -LiteralPath $csc)) { throw 'Framework C# compiler missing.' }
$managed=Join-Path $RimWorldRoot 'RimWorldWin64_Data/Managed'
$refs=@('Assembly-CSharp.dll','UnityEngine.CoreModule.dll','Unity.Mathematics.dll','netstandard.dll' | ForEach-Object { Join-Path $managed $_ })
foreach ($reference in $refs) { if (-not (Test-Path -LiteralPath $reference)) { throw "Required game assembly missing: $reference" } }
$workshop=Join-Path $RimWorldRoot '../../workshop/content/294100'
function Framework-Dll([string]$WorkshopId,[string]$Name) {
 $root=Join-Path $workshop $WorkshopId
 $preferred=Join-Path $root "1.6/Assemblies/$Name"
 if (Test-Path -LiteralPath $preferred) { return $preferred }
 $found=@(Get-ChildItem -LiteralPath $root -Recurse -File -Filter $Name)
 if ($found.Count -ne 1) { throw "Cannot uniquely resolve $Name; use installed 1.6 framework." }
 return $found[0].FullName
}
$pickle=Framework-Dll '3791648678' 'RimWorks.Pickle.dll'
$quick=Framework-Dll '3793646067' 'Quickstarts.dll'
& (Join-Path $PSScriptRoot 'Stage-ScenarioTestProfile.ps1') -RepositoryRoot $repo -ModsRoot (Join-Path $RimWorldRoot 'Mods') -Profile $Profile -GrainsRepositoryRoot $GrainsRepositoryRoot
$test=Join-Path $RimWorldRoot 'Mods/AncientMedievalJapanScenarios.E2E'
$referenceArgs=@($refs | ForEach-Object { '/reference:'+$_ })
& $csc /nologo /target:library /optimize+ ("/out:"+(Join-Path $test 'Assemblies/AMJ.Scenarios.E2E.dll')) @referenceArgs ("/reference:"+$quick) (Join-Path $repo 'Tests/E2E/NewVillageQuickstart.cs')
if ($LASTEXITCODE -ne 0) { throw "Scenario Quickstart compilation failed: $LASTEXITCODE" }
& $csc /nologo /target:library /optimize+ ("/out:"+(Join-Path $test 'Pickle/Assemblies/AMJ.Scenarios.E2E.Steps.dll')) @referenceArgs ("/reference:"+$pickle) (Join-Path $repo 'Tests/E2E/RuntimeThread.cs') (Join-Path $repo 'Tests/E2E/NewVillageSteps.cs')
if ($LASTEXITCODE -ne 0) { throw "Scenario steps compilation failed: $LASTEXITCODE" }
