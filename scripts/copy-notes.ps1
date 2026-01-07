$ErrorActionPreference = 'Stop'

function Get-TextEncoding {
  param(
    [Parameter(Mandatory = $true)]
    [byte[]]$Bytes
  )

  if ($Bytes.Length -ge 3 -and $Bytes[0] -eq 0xEF -and $Bytes[1] -eq 0xBB -and $Bytes[2] -eq 0xBF) {
    return [System.Text.Encoding]::UTF8
  }
  if ($Bytes.Length -ge 2 -and $Bytes[0] -eq 0xFF -and $Bytes[1] -eq 0xFE) {
    return [System.Text.Encoding]::Unicode
  }
  if ($Bytes.Length -ge 2 -and $Bytes[0] -eq 0xFE -and $Bytes[1] -eq 0xFF) {
    return [System.Text.Encoding]::BigEndianUnicode
  }

  try {
    $strictUtf8 = New-Object System.Text.UTF8Encoding($false, $true)
    $null = $strictUtf8.GetString($Bytes)
    return $strictUtf8
  } catch {
    return [System.Text.Encoding]::GetEncoding('GBK')
  }
}

function Normalize-MarkdownHeadings {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Path
  )

  $bytes = [System.IO.File]::ReadAllBytes($Path)
  $encoding = Get-TextEncoding -Bytes $bytes
  $text = $encoding.GetString($bytes)
  $lines = $text -split "`r?`n"
  $inFence = $false
  $fencePattern = '^\s*(```|~~~)'

  $out = foreach ($line in $lines) {
    if (-not $inFence -and $line -match '^\s*[-*+]\s+(```|~~~)') {
      $line = $line -replace '^(\s*[-*+])\s+(```|~~~)', '$1   $2'
    }

    if ($line -match $fencePattern) {
      $inFence = -not $inFence
      $line
      continue
    }

    if (-not $inFence) {
      if ($line -match '^\s*(?:[-*+]|\d+\.)\s+(#{1,6})\s+(.*)$') {
        "$($matches[1]) $($matches[2])"
      } elseif ($line -match '^\\s{0,3}(#{1,6})([^ #])(.*)$') {
        $hashes = $matches[1]
        $rest = $matches[2] + $matches[3]
        if ($rest -match '^(include|define|pragma|if|elif|endif|else|!/|region|endregion)\\b') {
          $line
        } else {
          "$hashes $rest"
        }
      } else {
        $line
      }
    } else {
      $line
    }
  }

  [System.IO.File]::WriteAllLines($Path, $out, [System.Text.Encoding]::UTF8)
}

$sourceFiles = @(
  'D:\My2025\MyNotes\flow\EDA4PR.md',
  'D:\My2025\MyNotes\flow\EDA4PR-Analog.md',
  'D:\My2025\MyNotes\flow\EDA4PR-Digtal.md',
  'D:\My2025\MyNotes\flow\EDA4PR-LCM.md',
  'D:\My2025\MyNotes\flow\flow.md',
  'D:\My2025\MyNotes\Other\Algorithms.md',
  'D:\My2025\MyNotes\Other\Hardware.md',
  'D:\My2025\MyNotes\Other\Literature.md',
  'D:\My2025\MyNotes\Other\OS.md',
  'D:\My2025\MyNotes\Other\Program.md',
  'D:\My2025\MyNotes\Other\Tools.md'
)

$destDocs = 'D:\My2025\MyBlog\docs'
$destAssets = 'D:\My2025\MyBlog\docs\assets'

New-Item -ItemType Directory -Force -Path $destDocs | Out-Null
New-Item -ItemType Directory -Force -Path $destAssets | Out-Null

foreach ($file in $sourceFiles) {
  if (Test-Path -LiteralPath $file) {
    Copy-Item -LiteralPath $file -Destination $destDocs -Force
    $destFile = Join-Path $destDocs (Split-Path $file -Leaf)
    Normalize-MarkdownHeadings -Path $destFile
  } else {
    Write-Warning "Missing file: $file"
  }
}

$assetSources = @(
  'D:\My2025\MyNotes\Other\assets',
  'D:\My2025\MyNotes\flow\assets'
)

foreach ($src in $assetSources) {
  if (Test-Path -LiteralPath $src) {
    # Robocopy uses bitmask exit codes; 0-7 are success/warnings.
    & robocopy $src $destAssets /E
    if ($LASTEXITCODE -ge 8) {
      throw "Robocopy failed for assets folder: $src (exit code $LASTEXITCODE)"
    }
  } else {
    Write-Warning "Missing assets folder: $src"
  }
}
