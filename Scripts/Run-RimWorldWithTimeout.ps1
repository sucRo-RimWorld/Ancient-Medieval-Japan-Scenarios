param(
    [Parameter(Mandatory = $true)]
    [string]$ExePath,

    [Parameter(Mandatory = $true)]
    [string]$SavedataFolder,

    [Parameter(Mandatory = $true)]
    [string]$ReportDir,

    [Parameter(Mandatory = $true)]
    [string]$LogPath,

    [string]$RunFilter = "stage-a.feature",

    [int]$TimeoutSeconds = 300
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $ExePath)) {
    Write-Host "[ERROR] RimWorld executable was not found:" -ForegroundColor Red
    Write-Host "        $ExePath"
    exit 2
}

$logDir = Split-Path -Parent $LogPath
if (-not (Test-Path -LiteralPath $logDir)) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
}
if (Test-Path -LiteralPath $LogPath) {
    Remove-Item -LiteralPath $LogPath -Force
}

$arguments = @(
    '-savedatafolder="' + $SavedataFolder + '"',
    '-logFile "' + $LogPath + '"',
    '-pickle-run="' + $RunFilter + '"',
    '-pickle-mode=fast',
    '-pickle-report-dir="' + $ReportDir + '"',
    '-pickle-no-browser',
    '-pickle-run-timeout=4'
) -join ' '

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $ExePath
$psi.Arguments = $arguments
$psi.WorkingDirectory = Split-Path -Parent $ExePath
$psi.UseShellExecute = $false

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $psi

try {
    if (-not $process.Start()) {
        Write-Host "[ERROR] Failed to start RimWorld." -ForegroundColor Red
        exit 2
    }

    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
        Write-Host ""
        Write-Host "[ERROR] RimWorld/Pickle did not exit within $TimeoutSeconds seconds." -ForegroundColor Red
        Write-Host "        The process will be terminated so run-tests.bat cannot hang indefinitely."

        try {
            $process.Kill()
            $process.WaitForExit()
        }
        catch {
            Write-Host "[WARN] Failed to terminate RimWorld cleanly: $($_.Exception.Message)" -ForegroundColor Yellow
        }

        exit 124
    }

    exit $process.ExitCode
}
finally {
    $process.Dispose()
}
