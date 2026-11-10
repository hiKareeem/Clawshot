# Clawshot start for Windows; Clawshot.bat runs this file. It uses uv from the PATH or from this folder's .tools,
# and otherwise downloads the pinned official uv release from GitHub into .tools, checking its SHA-256 against the
# value below before anything is unpacked or run. Nothing is installed system-wide: no admin, no PATH or profile
# change. Then it starts the UI with the locked dependencies and the app-window extra (pywebview).
# Keep this file ASCII: Windows PowerShell 5.1 reads a file without a byte order mark in the ANSI code page.

$ErrorActionPreference = 'Stop'

# Pinned uv release: https://github.com/astral-sh/uv/releases/tag/0.13.7 (an immutable GitHub release). The hashes
# are that release's own sha256.sum values. Bump the version and every hash together, in clawshot.sh too.
$UvVersion = '0.13.7'
$UvSha256 = @{
    'x86_64-pc-windows-msvc'  = '0cdc5b38fe5a8168ed6a25814f5ba43c21d313dd3187314fccb37b7cec46e021'
    'aarch64-pc-windows-msvc' = '505d9e65e7692bac3ddf98c66754aa26c5050c409c184af30a881a0a72cc85e3'
}

$Root = Split-Path -Parent $PSScriptRoot
$Tools = Join-Path $Root '.tools'
$UvDir = Join-Path $Tools "uv-$UvVersion"
$UvExe = Join-Path $UvDir 'uv.exe'
$ReleasePage = "https://github.com/astral-sh/uv/releases/tag/$UvVersion"

function Exit-WithMessage([string[]]$Lines) {
    Write-Host ''
    foreach ($line in $Lines) { Write-Host $line }
    exit 1
}

function Install-PinnedUv {
    # The machine's own architecture, also when this PowerShell runs emulated (x86 or x64 on ARM64).
    $arch = $env:PROCESSOR_ARCHITEW6432
    if (-not $arch) { $arch = $env:PROCESSOR_ARCHITECTURE }
    switch ($arch) {
        'AMD64' { $target = 'x86_64-pc-windows-msvc' }
        'ARM64' { $target = 'aarch64-pc-windows-msvc' }
        default {
            Exit-WithMessage @(
                "Clawshot has no uv download for this computer (Windows $arch).",
                "Install uv yourself from $ReleasePage, then double-click Clawshot.bat again."
            )
        }
    }
    $asset = "uv-$target.zip"
    $url = "https://github.com/astral-sh/uv/releases/download/$UvVersion/$asset"
    $expected = $UvSha256[$target]

    Write-Host "Downloading uv $UvVersion (the tool that runs Clawshot) once from its official GitHub release into `"$UvDir`"; uv stays inside this app folder."

    # $failure names the step that stops; it is cleared only when uv is in place.
    $failure = $null
    $work = $null
    try {
        $failure = "Windows did not let it write to `"$Tools`""
        $work = Join-Path $Tools ("download-" + [Guid]::NewGuid().ToString('N'))
        New-Item -ItemType Directory -Force -Path $work | Out-Null
        $archive = Join-Path $work $asset
        $unpacked = Join-Path $work 'uv.exe'

        $failure = 'no internet connection, or the download was blocked'
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $archive -TimeoutSec 180

        # Nothing from the download is opened before this check.
        $failure = 'the downloaded file is not the expected one (its SHA-256 differs); it was not unpacked or run'
        $actual = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne $expected) { throw 'SHA-256 mismatch' }

        $failure = 'the downloaded file could not be unpacked'
        Add-Type -AssemblyName 'System.IO.Compression', 'System.IO.Compression.FileSystem'
        $zip = [System.IO.Compression.ZipFile]::OpenRead($archive)
        try {
            $entry = $zip.GetEntry('uv.exe')
            if ($null -eq $entry) { throw 'uv.exe is missing from the archive' }
            [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $unpacked, $true)
        } finally {
            $zip.Dispose()
        }

        $failure = 'the downloaded uv did not start on this computer'
        & $unpacked --version | Out-Null
        if ($LASTEXITCODE -ne 0) { throw 'uv --version failed' }

        $failure = "Windows did not let it write to `"$UvDir`""
        New-Item -ItemType Directory -Force -Path $UvDir | Out-Null
        if (-not (Test-Path -LiteralPath $UvExe -PathType Leaf)) {
            Move-Item -LiteralPath $unpacked -Destination $UvExe
        }
        $failure = $null
    } catch {
        # Reported once below, in $failure's words.
    } finally {
        if ($work) { Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue }
    }
    if ($failure) {
        Exit-WithMessage @(
            "Clawshot could not download uv: $failure.",
            "Download $url yourself, put the uv.exe from it in `"$UvDir`", then double-click Clawshot.bat again."
        )
    }
}

$onPath = Get-Command uv -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if ($onPath) {
    $uv = $onPath.Path
} elseif (Test-Path -LiteralPath $UvExe -PathType Leaf) {
    $uv = $UvExe
} else {
    Install-PinnedUv
    $uv = $UvExe
}

& $uv run --project $Root --frozen --no-dev --extra ui python -m clawshot.ui @args
$status = $LASTEXITCODE
if ($status -ne 0) {
    Write-Host ''
    Write-Host 'Clawshot stopped. The lines above say why.'
}
exit $status
