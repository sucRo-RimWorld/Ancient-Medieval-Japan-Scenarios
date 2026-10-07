param([string]$RepositoryRoot,[string]$GrainsRepositoryRoot,[string]$OutputPath,[string]$Profile)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'ScenarioTestProfiles.ps1')
$spec=Get-ScenarioTestProfile $Profile
$roots=@($RepositoryRoot)
if ($spec.UseGrains) { $roots += $GrainsRepositoryRoot }
$states=@()
foreach ($root in $roots) {
 $commit=(& git -C $root rev-parse HEAD).Trim()
 if ($LASTEXITCODE -ne 0) { throw 'Source repository commit unavailable.' }
 $files=@()
 foreach ($path in @(& git -C $root ls-files)) {
  if ($path -like 'Art/*' -or $path -like 'Docs/Coordination.md') { continue }
  $file=Join-Path $root $path
  if (Test-Path -LiteralPath $file -PathType Leaf) { $files += [pscustomobject]@{Path=$path;Sha256=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()} }
 }
 $states += [pscustomobject]@{Root=$root;Commit=$commit;Files=$files}
}
[pscustomobject]@{Profile=$spec;Sources=$states} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
