$ErrorActionPreference = 'Stop'

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
