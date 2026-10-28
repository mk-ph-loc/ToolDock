param([string]$Version = (Get-Content "$PSScriptRoot/../VERSION" -Raw).Trim(), [switch]$Push)
$ErrorActionPreference = 'Stop'
Set-Location "$PSScriptRoot/.."
$python = Join-Path (Get-Location) '.venv/Scripts/python.exe'
if (-not (Test-Path $python)) { throw 'Δεν βρέθηκε .venv/Scripts/python.exe' }
& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Αποτυχία tests: διακοπή' }
& $python scripts/package.py
if ($LASTEXITCODE -ne 0) { throw 'Αποτυχία zip: διακοπή' }
if (-not $Push) { Write-Host 'Zip έτοιμο. Για commit/tag/push: .\scripts\release.ps1 -Push'; exit 0 }
# ΠΡΟΣΟΧΗ: το -Push δημοσιεύει όλες τις μη αγνοημένες αλλαγές και στα δύο remotes.
git add -A
if ($LASTEXITCODE -ne 0) { throw 'git add failed' }
git diff --cached --quiet
if ($LASTEXITCODE -eq 1) {
    git commit -m "v${Version}: floating, dock και υποστήριξη πολλών οθονών"
    if ($LASTEXITCODE -ne 0) { throw 'git commit failed' }
} elseif ($LASTEXITCODE -ne 0) { throw 'git diff failed' }
git rev-parse --verify --quiet "refs/tags/v$Version"
if ($LASTEXITCODE -eq 0) { throw 'Το tag υπάρχει ήδη· δεν αντικαθίσταται' }
git tag "v$Version"
if ($LASTEXITCODE -ne 0) { throw 'git tag failed' }
foreach ($remote in @('origin', 'github')) {
    git push $remote main
    if ($LASTEXITCODE -ne 0) { throw "Push main απέτυχε: $remote" }
    git push $remote "v$Version"
    if ($LASTEXITCODE -ne 0) { throw "Push tag απέτυχε: $remote" }
}
Write-Host 'Ολοκληρώθηκε η δημοσίευση και στα δύο remotes.' -ForegroundColor Green
