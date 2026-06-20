# Defaults to the repo root so it validates every *.trip.js — the committed
# samples plus any trip in your local my-trips/ workspace. Pass explicit paths
# (directories searched recursively, or single *.trip.js files) to narrow scope.
Param(
    [string[]]$Dirs = @("$PSScriptRoot\..")
)

$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py) {
    $py = (Get-Command py -ErrorAction SilentlyContinue).Source
}
if (-not $py) {
    Write-Error "Python not found in PATH. Install Python or run from WSL/Git-Bash."
    exit 1
}

& $py (Join-Path $PSScriptRoot 'validate_trips.py') @Dirs
exit $LASTEXITCODE
