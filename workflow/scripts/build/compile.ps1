# Windows 与 Unix 使用相同 compile.sh，需 Git for Windows Bash。
$ErrorActionPreference = 'Stop'
$bash = Get-Command bash -ErrorAction Stop
& $bash.Source (Join-Path $PSScriptRoot 'compile.sh') @args
exit $LASTEXITCODE
