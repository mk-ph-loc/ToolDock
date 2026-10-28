param(
    [string]$Version = (Get-Content VERSION -Raw).Trim()
)

$ErrorActionPreference = "Stop"
Write-Host "ToolDock release v$Version"

python -m pytest
if ($LASTEXITCODE -ne 0) { throw "Tests failed" }

if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
New-Item "dist" -ItemType Directory | Out-Null
$zip = "dist/tooldock-v$Version.zip"
Compress-Archive -Path "src","tests","scripts","docs","README.md","AGENTS.md","CLAUDE.md","VERSION","CHANGELOG.md","requirements.txt","config.example.json","run.bat",".gitignore" -DestinationPath $zip -Force

git add -A
git commit -m "v$Version: release ToolDock v$Version"
git tag "v$Version"
git push origin main
git push origin "v$Version"
git push github main
git push github "v$Version"

Write-Host "OK: $zip"
