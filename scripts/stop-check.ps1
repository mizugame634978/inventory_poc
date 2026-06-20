#!/usr/bin/env pwsh
# Stop hook 用ラッパ。標準入力で hook の JSON を受け取る。
# - すでに stop hook 起因の継続中(stop_hook_active)なら何もしない(無限ループ防止)。
# - そうでなければ check.ps1 を実行し、赤なら exit 2 で停止をブロックして失敗内容を返す。

$ErrorActionPreference = 'Continue'

$raw = [Console]::In.ReadToEnd()
try { $payload = $raw | ConvertFrom-Json } catch { $payload = $null }
if ($payload -and $payload.stop_hook_active) { exit 0 }

$out = & (Join-Path $PSScriptRoot 'check.ps1') 2>&1
$code = $LASTEXITCODE

if ($code -ne 0) {
    [Console]::Error.WriteLine("自動チェックが失敗しました。緑にしてから終了してください:`n" + ($out -join "`n"))
    exit 2
}
exit 0
