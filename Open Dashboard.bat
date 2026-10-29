<# : Batch launcher - cmd runs these lines; PowerShell sees them as a comment.
@echo off
set "DASH_DIR=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((Get-Content -LiteralPath '%~f0' -Encoding UTF8) -join [Environment]::NewLine)"
if errorlevel 1 pause
exit /b
#>

# ---------------------------------------------------------------------------
# Everything below is PowerShell: scans the applied-jobs folder (and its
# position subfolders), writes
# data.js next to this file, then opens index.html in your default browser.
# ---------------------------------------------------------------------------

$Folder = 'C:\Users\Admin\Documents\job search\job description\applied'
$After  = '2026-07-29'   # only applications saved AFTER this date are counted

$ErrorActionPreference = 'Stop'
$here   = $env:DASH_DIR
$cutoff = [datetime]::ParseExact($After, 'yyyy-MM-dd', $null).Date

if (-not (Test-Path -LiteralPath $Folder)) {
    Write-Host "Folder not found: $Folder" -ForegroundColor Red
    exit 1
}

$rootDir = (Get-Item -LiteralPath $Folder).FullName.TrimEnd('\')

# Date each file by the earlier of created/modified: copying a file resets
# CreationTime, editing it resets LastWriteTime - the earlier one is the save date.
# Subfolders are positions (e.g. "data science"); the first subfolder level names it.
$items = @(
    Get-ChildItem -LiteralPath $Folder -File -Recurse |
        Where-Object { $_.Name -notlike '~$*' -and $_.Name -ne 'desktop.ini' } |
        ForEach-Object {
            $t = if ($_.CreationTime -lt $_.LastWriteTime) { $_.CreationTime } else { $_.LastWriteTime }
            if ($t.Date -gt $cutoff) {
                $rel = $_.DirectoryName.Substring($rootDir.Length).TrimStart('\')
                [pscustomobject]@{
                    date     = $t.ToString('yyyy-MM-dd')
                    time     = $t.ToString('HH:mm')
                    name     = $_.Name
                    category = if ($rel) { $rel.Split('\')[0] } else { 'Uncategorized' }
                    path     = $_.FullName
                }
            }
        } |
        Sort-Object date, time
)

$json  = ConvertTo-Json -InputObject $items -Compress
$start = $cutoff.AddDays(1).ToString('yyyy-MM-dd')
$js = "window.START_DATE = '$start';`r`n" +
      "window.GENERATED_AT = '$(Get-Date -Format s)';`r`n" +
      "window.APPLICATIONS = $json;`r`n"

[IO.File]::WriteAllText((Join-Path $here 'data.js'), $js, (New-Object Text.UTF8Encoding $false))
Write-Host "Found $($items.Count) applications since $start."

Start-Process (Join-Path $here 'index.html')
