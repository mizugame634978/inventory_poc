#!/usr/bin/env pwsh
# 自走ハーネスの統一オラクル: ヘッドレスで決定的なテストだけを実行する。
# UIテスト(InventoryClient.UiTests)は Show() がデスクトップ依存のため、ここには含めない(#0004)。
# $PSScriptRoot 起点なので、どのカレントディレクトリから呼んでも動く。

$ErrorActionPreference = 'Continue'
$root = Split-Path $PSScriptRoot -Parent
$failed = $false

Write-Host '=== server: pytest ==='
Push-Location (Join-Path $root 'server')
uv run pytest -q
if ($LASTEXITCODE -ne 0) { $failed = $true }
Pop-Location

Write-Host '=== client: ViewModel tests ==='
Push-Location (Join-Path $root 'client')
dotnet test InventoryClient.Tests
if ($LASTEXITCODE -ne 0) { $failed = $true }
Pop-Location

if ($failed) {
    Write-Host 'CHECK: FAILED'
    exit 1
}
Write-Host 'CHECK: OK'
exit 0
