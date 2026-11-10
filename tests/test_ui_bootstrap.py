r"""Static bootstrap contracts: no launcher, network, native window or game is run by these tests.

Optional OFFLINE smoke commands (manual; not part of the test gates): from the repository root, use a fake uv
first on PATH and a disposable app folder with spaces. It only prints arguments and exits; no dependency install
or window opens. Expect `run --project <one path containing spaces> --frozen --no-dev`, `--extra ui` on Windows,
then `python -m clawshot.ui --no-open`. A download message means the fake was not found: stop, do not proceed.

POSIX shell (Linux/macOS, or Git Bash for this PATH-only smoke):

    scratch=$(mktemp -d)
    mkdir "$scratch/App with spaces" "$scratch/fake"
    cp clawshot.sh pyproject.toml uv.lock "$scratch/App with spaces/"
    cat > "$scratch/fake/uv" <<'FAKE'
    #!/bin/sh
    printf 'arg=<%s>\n' "$@"
    FAKE
    chmod +x "$scratch/fake/uv"
    PATH="$scratch/fake:$PATH" sh "$scratch/App with spaces/clawshot.sh" --no-open
    rm -rf "$scratch"

Remove the four-space documentation indentation before pasting (including the FAKE delimiter).

Windows PowerShell (no policy or PATH change survives this block):

    $scratch = Join-Path $env:TEMP ('Clawshot smoke ' + [Guid]::NewGuid().ToString('N'))
    $app = Join-Path $scratch 'App with spaces'
    $fake = Join-Path $scratch 'fake'
    New-Item -ItemType Directory -Path "$app/scripts", $fake | Out-Null
    Copy-Item Clawshot.bat, pyproject.toml, uv.lock -Destination $app
    Copy-Item scripts/start-windows.ps1 "$app/scripts/"
    @('@echo off', 'echo FAKE UV: %*', 'exit /b 0') | Set-Content "$fake/uv.cmd" -Encoding Ascii
    $oldPath = $env:PATH
    try {
        $env:PATH = "$fake;$oldPath"
        & "$app/Clawshot.bat" --no-open
    } finally {
        $env:PATH = $oldPath
        Remove-Item -LiteralPath $scratch -Recurse -Force
    }

These smokes cover only PATH discovery, project-root quoting and locked invocation, not download or GUI behavior.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.13.7"
RELEASE = f"https://github.com/astral-sh/uv/releases/download/{VERSION}"

# Official checksum source: https://github.com/astral-sh/uv/releases/download/0.13.7/sha256.sum
# The same digests appear in each asset's .sha256 file and the GitHub release API's asset digest.
# Deliberately independent of the launchers: changing a version requires reviewing all six official hashes.
HASHES = {
    "uv-x86_64-pc-windows-msvc.zip": "0cdc5b38fe5a8168ed6a25814f5ba43c21d313dd3187314fccb37b7cec46e021",
    "uv-aarch64-pc-windows-msvc.zip": "505d9e65e7692bac3ddf98c66754aa26c5050c409c184af30a881a0a72cc85e3",
    "uv-x86_64-unknown-linux-musl.tar.gz": "287491da03f2a785c70fa75b13e1f849918c2f2b5415fe84876b8214eeb792f9",
    "uv-aarch64-unknown-linux-musl.tar.gz": "2d3ec076a0c4c0e8250bb6418c44080828b544f1a3be0b6e46adf9fb6923de45",
    "uv-x86_64-apple-darwin.tar.gz": "20c47e4c1f630b8abaff8c291fa9b9aa300fef92c4fbff95adf198b55287cda7",
    "uv-aarch64-apple-darwin.tar.gz": "81b811b57e4624df7ed3aac148e0359100d9962f3d9dce00aec533dc2e086731",
}


@pytest.fixture(scope="module")
def scripts():
    return {
        name: (ROOT / name).read_text(encoding="utf-8")
        for name in ("Clawshot.bat", "clawshot.sh", "scripts/start-windows.ps1")
    }


def test_pinned_release_and_all_official_hashes(scripts):
    windows = scripts["scripts/start-windows.ps1"]
    unix = scripts["clawshot.sh"]
    assert f"$UvVersion = '{VERSION}'" in windows
    assert f"UV_VERSION='{VERSION}'" in unix
    windows_hashes = re.findall(r"'([a-z0-9_-]+)'\s*=\s*'([a-f0-9]{64})'", windows)
    unix_hashes = re.findall(r"([a-z0-9_-]+)\) expected='([a-f0-9]{64})'", unix)
    found = {f"uv-{target}.zip": digest for target, digest in windows_hashes}
    found.update({f"uv-{target}.tar.gz": digest for target, digest in unix_hashes})
    assert len(windows_hashes) == 2
    assert len(unix_hashes) == 4
    assert found == HASHES
    assert len(set(found.values())) == 6
    assert f"{RELEASE}/$asset" in windows.replace("$UvVersion", VERSION)
    assert f"{RELEASE}/$asset" in unix.replace("$UV_VERSION", VERSION)
    assert '$asset = "uv-$target.zip"' in windows
    assert 'asset="uv-$target.tar.gz"' in unix


def test_download_selection_covers_native_architectures(scripts):
    windows = scripts["scripts/start-windows.ps1"]
    unix = scripts["clawshot.sh"]
    assert "$arch = $env:PROCESSOR_ARCHITEW6432" in windows
    assert "if (-not $arch) { $arch = $env:PROCESSOR_ARCHITECTURE }" in windows
    assert "'AMD64' { $target = 'x86_64-pc-windows-msvc' }" in windows
    assert "'ARM64' { $target = 'aarch64-pc-windows-msvc' }" in windows
    for selector, target in (
        ("Linux:x86_64|Linux:amd64", "x86_64-unknown-linux-musl"),
        ("Linux:aarch64|Linux:arm64", "aarch64-unknown-linux-musl"),
        ("Darwin:x86_64", "x86_64-apple-darwin"),
        ("Darwin:arm64|Darwin:aarch64", "aarch64-apple-darwin"),
    ):
        assert f"{selector}) target='{target}' ;;" in unix
    assert "sysctl -n hw.optional.arm64" in unix
    assert "arch=arm64" in unix
    assert '*) fail "Clawshot has no uv download' in unix
    assert "Clawshot has no uv download" in windows
    for text in (windows, unix):
        assert "https://github.com/astral-sh/uv/releases/tag/" in text
        assert "Install uv yourself from" in text


def test_windows_verifies_before_opening_or_running_download(scripts):
    text = scripts["scripts/start-windows.ps1"]
    steps = (
        "Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $archive",
        "Get-FileHash -LiteralPath $archive -Algorithm SHA256",
        "if ($actual -ne $expected) { throw 'SHA-256 mismatch' }",
        "[System.IO.Compression.ZipFile]::OpenRead($archive)",
        "$zip.GetEntry('uv.exe')",
        "[System.IO.Compression.ZipFileExtensions]::ExtractToFile",
        "& $unpacked --version",
        "Move-Item -LiteralPath $unpacked -Destination $UvExe",
        "& $uv run --project $Root",
    )
    positions = [text.index(step) for step in steps]
    assert positions == sorted(positions)
    assert "$expected = $UvSha256[$target]" in text
    assert "if ($LASTEXITCODE -ne 0) { throw 'uv --version failed' }" in text
    assert "if ($failure) {" in text
    assert "Remove-Item -LiteralPath $work -Recurse -Force" in text


def test_unix_verifies_before_extracting_or_running_download(scripts):
    text = scripts["clawshot.sh"]
    steps = (
        "curl --fail --silent --location",
        'actual=$(sha256sum < "$archive")',
        'actual=$(shasum -a 256 < "$archive")',
        "actual=${actual%% *}",
        'if [ "$actual" != "$expected" ]; then',
        "bootstrap_failure 'the downloaded file is not the expected one",
        'tar -xzf "$archive" -C "$work" "uv-$target/uv"',
        '"$unpacked" --version',
        'mv -- "$unpacked" "$uv_local"',
        '"$uv" run --project "$root"',
    )
    positions = [text.index(step) for step in steps]
    assert positions == sorted(positions)
    assert "trap cleanup 0" in text
    assert 'rm -rf -- "$work"' in text
    assert "trap - 0 INT TERM HUP" in text
    assert "--proto '=https' --proto-redir '=https'" in text
    assert "wget --quiet --https-only --timeout=30 --tries=1" in text
    assert "--connect-timeout 15 --max-time 180" in text
    assert "--retry" not in text


def test_path_uv_precedes_versioned_app_local_uv(scripts):
    windows = scripts["scripts/start-windows.ps1"]
    unix = scripts["clawshot.sh"]
    assert "$onPath = Get-Command uv -CommandType Application" in windows
    assert windows.index("if ($onPath) {") < windows.index("} elseif (Test-Path -LiteralPath $UvExe")
    assert "$uv = $onPath.Path" in windows
    assert "$Tools = Join-Path $Root '.tools'" in windows
    assert '$UvDir = Join-Path $Tools "uv-$UvVersion"' in windows
    assert windows.index("    Install-PinnedUv\n") > windows.index("} elseif (Test-Path -LiteralPath $UvExe")
    assert unix.index("uv=$(command -v uv") < unix.index('[ -x "$uv_local" ]') < unix.index("os=$(uname -s)")
    assert 'tools="$root/.tools"' in unix
    assert 'uv_dir="$tools/uv-$UV_VERSION"' in unix
    assert 'work=$(mktemp -d "$tools/download.XXXXXXXX"' in unix
    assert "$work = Join-Path $Tools" in windows


def test_locked_launch_commands_and_quoted_project_roots(scripts):
    windows = scripts["scripts/start-windows.ps1"]
    unix = scripts["clawshot.sh"]
    batch = scripts["Clawshot.bat"]
    assert "$Root = Split-Path -Parent $PSScriptRoot" in windows
    assert "& $uv run --project $Root --frozen --no-dev --extra ui python -m clawshot.ui @args" in windows
    assert 'root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)' in unix
    assert '"$uv" run --project "$root" --frozen --no-dev python -m clawshot.ui "$@"' in unix
    assert "--extra" not in unix
    assert "setlocal DisableDelayedExpansion" in batch
    assert '-NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\\start-windows.ps1" %*' in batch
    assert "%SystemRoot%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" in batch
    assert 'if not exist "%~dp0uv.lock"' in batch
    assert not re.search(r"(?im)^\s*(?:goto\b|:[^:])", batch)  # No LF-sensitive batch label jumps.


def test_failures_remain_readable_and_have_manual_links(scripts):
    batch = scripts["Clawshot.bat"]
    unix = scripts["clawshot.sh"]
    windows = scripts["scripts/start-windows.ps1"]
    assert 'set "status=%errorlevel%"' in batch
    assert 'if not "%status%"=="0" pause' in batch
    assert "exit /b %status%" in batch
    assert "if [ -t 0 ]; then" in unix
    assert "Press Enter to close this window." in unix
    assert "IFS= read -r ignored" in unix
    assert "pause_on_failure\n    exit 1" in unix
    assert 'exit "$status"' in unix
    assert "exit $status" in windows
    for text in (unix, windows):
        assert "Downloading uv " in text
        assert "no internet connection, or the download was blocked" in text
        assert "Download $url yourself" in text
        assert "it was not unpacked or run" in text


@pytest.mark.parametrize("name", ("Clawshot.bat", "clawshot.sh", "scripts/start-windows.ps1"))
def test_no_installer_pipes_privilege_or_system_changes(scripts, name):
    text = scripts[name]
    lower = text.lower()
    assert text.isascii()  # In particular, Windows PowerShell 5.1 has no UTF-8 default.
    for forbidden in (
        "/latest",
        "uv-installer",
        "astral.sh/uv/install",
        "invoke-expression",
        "--insecure",
        "--no-check-certificate",
        "-skipcertificatecheck",
        "--system",
        "setx ",
        "set-executionpolicy",
        "-verb runas",
        "sudo ",
        "http://",
    ):
        assert forbidden not in lower
    assert not re.search(r"\|\s*(?:sh|bash|zsh|powershell|iex)\b", lower)
    assert not re.search(r"(?im)^\s*(?:export\s+)?(?:\$env:)?path\s*=", text)
    assert not re.search(r"(?im)^\s*set\s+\"?path=", text)
    assert not re.search(r"[>]+.*(?:\.profile|\.bashrc|\.zshrc|\$profile)", lower)
