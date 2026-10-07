param(
    [Parameter(Mandatory = $true)][string]$SummaryPath,
    [Parameter(Mandatory = $true)][ValidateSet('vanilla','grains','mo','grains-mo')][string]$Profile
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'ScenarioTestProfiles.ps1')
$spec = Get-ScenarioTestProfile $Profile
if (-not (Test-Path -LiteralPath $SummaryPath)) { throw "Missing fresh summary: $SummaryPath" }
$summary = Get-Content -LiteralPath $SummaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($summary.total -ne $spec.Scenarios.Count -or $summary.passed -ne $spec.Scenarios.Count -or $summary.failed -ne 0 -or $summary.skipped -ne 0) {
    throw "Profile $Profile requires exactly $($spec.Scenarios.Count)/$($spec.Scenarios.Count) passes with no failures/skips."
}
$names = @($summary.scenarios | ForEach-Object { [string]$_.name })
if ($names.Count -ne $spec.Scenarios.Count) { throw "Unexpected number of named scenarios for $Profile." }
foreach ($name in $spec.Scenarios) {
    if (@($names | Where-Object { $_ -eq $name }).Count -ne 1) { throw "Expected exactly one scenario: $name" }
}
Write-Host "[OK] $Profile fresh migration smoke summary $($spec.Scenarios.Count)/$($spec.Scenarios.Count). This is not the full Scenario runtime/save release gate."
