param([ValidateSet('make', 'play')][string]$Action = 'make')
$ErrorActionPreference = 'Stop'
try {
    $root = $PSScriptRoot
    $manifest = Get-Content -LiteralPath (Join-Path $root 'pack.json') -Raw | ConvertFrom-Json
    $configPath = Join-Path $root 'folders.json'
    if (Test-Path -LiteralPath $configPath) {
        $config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
    } elseif ($Action -eq 'make') {
        $config = [pscustomobject]@{
            romfs = (Read-Host 'Your game .nup file or extracted romfs folder (no quotes)').Trim()
            hookshot = (Read-Host 'Optional Hookshot folder containing bin (no quotes; empty = emulator)').Trim()
        }
    } else {
        throw 'Run Make seed.bat first.'
    }
    # Check the source before generation, cache creation or saving configuration.
    $config.romfs = [IO.Path]::GetFullPath($config.romfs)
    if (Test-Path -LiteralPath $config.romfs -PathType Container) {
        # Folder preflight needs no uv/Python installation.
        $files = @(
            'Pack/ZsDic.pack.zs',
            'GameData/GameDataList.Product.110.byml.zs',
            'RSDB/EventSetting.Product.111.rstbl.byml.zs',
            'Banc/KokiriForest/KokiriForest_Child_Dynamic.bcett.byml.zs'
        )
        $hashes = ''
        foreach ($file in $files) {
            $stream = [IO.File]::OpenRead((Join-Path $config.romfs $file))
            $fileSha = [Security.Cryptography.SHA256]::Create()
            try {
                $hashes += [BitConverter]::ToString($fileSha.ComputeHash($stream)).Replace('-', '').ToLowerInvariant() + "`n"
            } finally { $stream.Dispose(); $fileSha.Dispose() }
        }
        $sha = [Security.Cryptography.SHA256]::Create()
        try {
            $actual = [BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::ASCII.GetBytes($hashes))).Replace('-', '').ToLowerInvariant()
        } finally { $sha.Dispose() }
        if ($actual -ne $manifest.romfs_sha256) {
            throw "RomFS does not match build $($manifest.build). Fingerprint $actual; expected $($manifest.romfs_sha256). Stop and report in help."
        }
    } else {
        # NUP extents may use zstd: bootstrap the locked reader, not the generator.
        Get-Command uv -ErrorAction Stop | Out-Null
        & uv run --project $root --frozen --no-dev python -m clawshot.pack.source $config.romfs --expected $manifest.romfs_sha256
        if ($LASTEXITCODE -ne 0) { throw 'NUP version/integrity check failed. No seed or cache was created.' }
    }
    if ($config.hookshot) {
        $config.hookshot = [IO.Path]::GetFullPath($config.hookshot)
    }
    foreach ($folder in @($config.romfs, $config.hookshot)) {
        if (-not $folder) { continue }
        $full = [IO.Path]::GetFullPath($folder).TrimEnd('\', '/')
        if ($root -eq $full -or $root.StartsWith($full + '\', [StringComparison]::OrdinalIgnoreCase) -or $full.StartsWith($root + '\', [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Extract the pack outside your RomFS and Hookshot folders.'
        }
    }
    if ($Action -eq 'play') {
        if (-not $config.hookshot) {
            throw 'No Hookshot folder configured. For emulator loading, follow docs/seed-pack.md (Emulator / console loading); do not run Play.'
        }
        $exe = Join-Path $config.hookshot 'bin/hookshot.exe'
        if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
            throw "Missing $exe. Never use the folder-root launcher."
        }
    }
    if (-not (Test-Path -LiteralPath $configPath)) {
        $config | ConvertTo-Json | Set-Content -LiteralPath $configPath -Encoding UTF8
    }
    Get-Command uv -ErrorAction Stop | Out-Null
    & uv run --project $root --frozen --no-dev python -m clawshot.pack.runtime $Action --root $root
    exit $LASTEXITCODE
} catch {
    Write-Host "ERROR: $_"
    exit 1
}
