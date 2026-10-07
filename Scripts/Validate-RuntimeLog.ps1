param(
    [Parameter(Mandatory = $true)]
    [string]$LogPath,

    [Parameter(Mandatory = $true)]
    [string]$ModIdPrefixes,

    [switch]$FailOnAnyError
)

$ErrorActionPreference = "Stop"

function Fail([string]$Message) {
    Write-Host "[FAIL] $Message" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path -LiteralPath $LogPath)) {
    Fail "Runtime log was not produced: $LogPath"
}

$text = Get-Content -LiteralPath $LogPath -Raw -Encoding UTF8
$prefixes = @(
    $ModIdPrefixes.Split(';') |
        ForEach-Object { $_.Trim().ToLowerInvariant() } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
)

if ($prefixes.Count -eq 0) {
    Fail "No mod-id prefixes were supplied for runtime log validation."
}

$errors = New-Object System.Collections.Generic.List[string]

# Structured RimLogging export blocks, when present.
$blocks = [regex]::Matches(
    $text,
    '(?ms)^Timestamp:\s*.*?(?=^Timestamp:\s*|\z)'
)

foreach ($match in $blocks) {
    $block = $match.Value
    if ($block -notmatch '(?m)^Level:\s*ERROR\s*$') {
        continue
    }

    if ($FailOnAnyError) {
        $errors.Add($block.Trim())
        continue
    }

    $idMatch = [regex]::Match($block, '(?mi)^mod_id:\s*([^\r\n]+)')
    $channelMatch = [regex]::Match($block, '(?mi)^Channel:\s*Mod\.([^\r\n]+)')

    $candidates = @()
    if ($idMatch.Success) {
        $candidates += $idMatch.Groups[1].Value.Trim().ToLowerInvariant()
    }
    if ($channelMatch.Success) {
        $candidates += $channelMatch.Groups[1].Value.Trim().ToLowerInvariant()
    }

    foreach ($candidate in $candidates) {
        foreach ($prefix in $prefixes) {
            if ($candidate.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
                $errors.Add($block.Trim())
                break
            }
        }
    }
}

# The normal RimWorld -logFile output used by the E2E runner is line-oriented
# and includes entries such as "[ERROR] [Vanilla]". Validate that format too.
$coloredErrorLines = [regex]::Matches(
    $text,
    '(?mi)^.*\[ERROR\].*$'
)

foreach ($match in $coloredErrorLines) {
    $line = $match.Value.Trim()
    if ($FailOnAnyError) {
        if (-not $errors.Contains($line)) {
            $errors.Add($line)
        }
        continue
    }

    $lower = $line.ToLowerInvariant()
    foreach ($prefix in $prefixes) {
        if ($lower.Contains($prefix)) {
            if (-not $errors.Contains($line)) {
                $errors.Add($line)
            }
            break
        }
    }
}

if ($errors.Count -gt 0) {
    if ($FailOnAnyError) {
        Write-Host "[FAIL] ERROR-level entries were found in the isolated AMJ runtime log:" -ForegroundColor Red
    }
    else {
        Write-Host "[FAIL] AMJ Core-origin runtime ERROR entries were found:" -ForegroundColor Red
    }

    $limit = [Math]::Min($errors.Count, 8)
    for ($i = 0; $i -lt $limit; $i++) {
        Write-Host ""
        Write-Host $errors[$i]
    }
    if ($errors.Count -gt $limit) {
        Write-Host ""
        Write-Host "... plus $($errors.Count - $limit) more runtime ERROR entries."
    }
    exit 1
}

if ($FailOnAnyError) {
    Write-Host "[OK] No ERROR-level entries were found in the isolated AMJ runtime log." -ForegroundColor Green
}
else {
    Write-Host "[OK] No AMJ Core-origin runtime ERROR entries were found." -ForegroundColor Green
}
exit 0
