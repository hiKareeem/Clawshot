#!/bin/sh
# Start from any working directory: sh /path/to/Clawshot/clawshot.sh
# uv is found on PATH or in this app's .tools; otherwise only a checked release archive is downloaded.
# No installer script, admin privileges, profile edits or PATH changes. Linux/macOS use the browser UI.

# Official immutable release; update this pin and its hashes together with scripts/start-windows.ps1.
# Source: https://github.com/astral-sh/uv/releases/download/0.13.7/sha256.sum
UV_VERSION='0.13.7'
RELEASE_PAGE="https://github.com/astral-sh/uv/releases/tag/$UV_VERSION"
work=''

pause_on_failure() {
    # A terminal opened by a file manager must not vanish before the message can be read.
    if [ -t 0 ]; then
        printf '\nPress Enter to close this window. '
        IFS= read -r ignored
    fi
}

fail() {
    printf '%s\n' "$@" >&2
    pause_on_failure
    exit 1
}

root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P) || exit 1
tools="$root/.tools"
uv_dir="$tools/uv-$UV_VERSION"
uv_local="$uv_dir/uv"

if [ ! -f "$root/uv.lock" ] || [ ! -f "$root/pyproject.toml" ]; then
    fail 'Unzip the whole Clawshot folder first, then open clawshot.sh inside it.'
fi

cleanup() {
    if [ -n "$work" ]; then
        rm -rf -- "$work" 2>/dev/null
    fi
}

bootstrap_failure() {
    # No retry and no attempt to execute a failed download.
    cleanup
    work=''
    fail "Clawshot could not download uv: $1." \
        "Download $url yourself, put the uv file from it in \"$uv_dir\", then open clawshot.sh again."
}

# Prefer an existing PATH uv unchanged; versioned local storage cannot reuse an older bootstrap pin.
uv=$(command -v uv 2>/dev/null) || uv=''
if [ -z "$uv" ] && [ -x "$uv_local" ]; then
    uv=$uv_local
fi

if [ -z "$uv" ]; then
    os=$(uname -s)
    arch=$(uname -m)
    # Under Rosetta uname can report x86_64 on Apple Silicon. Fetch the native build in that case.
    if [ "$os" = Darwin ] && [ "$(sysctl -n hw.optional.arm64 2>/dev/null)" = 1 ]; then
        arch=arm64
    fi
    # Static Linux builds run on both glibc and musl systems, without a minimum glibc version.
    case "$os:$arch" in
        Linux:x86_64|Linux:amd64) target='x86_64-unknown-linux-musl' ;;
        Linux:aarch64|Linux:arm64) target='aarch64-unknown-linux-musl' ;;
        Darwin:x86_64) target='x86_64-apple-darwin' ;;
        Darwin:arm64|Darwin:aarch64) target='aarch64-apple-darwin' ;;
        *) fail "Clawshot has no uv download for this computer ($os $arch)." \
            "Install uv yourself from $RELEASE_PAGE, then open clawshot.sh again." ;;
    esac
    case "$target" in
        x86_64-unknown-linux-musl) expected='287491da03f2a785c70fa75b13e1f849918c2f2b5415fe84876b8214eeb792f9' ;;
        aarch64-unknown-linux-musl) expected='2d3ec076a0c4c0e8250bb6418c44080828b544f1a3be0b6e46adf9fb6923de45' ;;
        x86_64-apple-darwin) expected='20c47e4c1f630b8abaff8c291fa9b9aa300fef92c4fbff95adf198b55287cda7' ;;
        aarch64-apple-darwin) expected='81b811b57e4624df7ed3aac148e0359100d9962f3d9dce00aec533dc2e086731' ;;
    esac
    asset="uv-$target.tar.gz"
    url="https://github.com/astral-sh/uv/releases/download/$UV_VERSION/$asset"
    printf 'Downloading uv %s (the tool that runs Clawshot) once from its official GitHub release into "%s"; uv stays inside this app folder.\n' "$UV_VERSION" "$uv_dir"

    mkdir -p -- "$tools" 2>/dev/null || bootstrap_failure "this folder cannot be written to: $tools"
    work=$(mktemp -d "$tools/download.XXXXXXXX" 2>/dev/null) || bootstrap_failure "this folder cannot be written to: $tools"
    trap cleanup 0
    trap 'exit 130' INT
    trap 'exit 143' TERM HUP
    archive="$work/$asset"

    if command -v curl >/dev/null 2>&1; then
        curl --fail --silent --location --proto '=https' --proto-redir '=https' \
            --connect-timeout 15 --max-time 180 --output "$archive" "$url" || \
            bootstrap_failure 'no internet connection, or the download was blocked'
    elif command -v wget >/dev/null 2>&1; then
        wget --quiet --https-only --timeout=30 --tries=1 --output-document="$archive" "$url" || \
            bootstrap_failure 'no internet connection, or the download was blocked'
    else
        bootstrap_failure 'neither curl nor wget is available on this computer'
    fi

    # Hash stdin so filenames with spaces or backslashes cannot affect the checksum output.
    if command -v sha256sum >/dev/null 2>&1; then
        actual=$(sha256sum < "$archive") || bootstrap_failure 'the download could not be checked'
    elif command -v shasum >/dev/null 2>&1; then
        actual=$(shasum -a 256 < "$archive") || bootstrap_failure 'the download could not be checked'
    else
        bootstrap_failure 'neither sha256sum nor shasum is available to check the download'
    fi
    actual=${actual%% *}
    if [ "$actual" != "$expected" ]; then
        bootstrap_failure 'the downloaded file is not the expected one (its SHA-256 differs); it was not unpacked or run'
    fi

    # Do not extract anything until the archive's SHA-256 matches the embedded official checksum.
    tar -xzf "$archive" -C "$work" "uv-$target/uv" 2>/dev/null || \
        bootstrap_failure 'the downloaded file could not be unpacked'
    unpacked="$work/uv-$target/uv"
    chmod u+x "$unpacked" 2>/dev/null || bootstrap_failure 'the downloaded uv could not be made executable'
    "$unpacked" --version >/dev/null 2>&1 || bootstrap_failure 'the downloaded uv did not start on this computer'
    mkdir -p -- "$uv_dir" 2>/dev/null || bootstrap_failure "this folder cannot be written to: $uv_dir"
    mv -- "$unpacked" "$uv_local" 2>/dev/null || bootstrap_failure "this folder cannot be written to: $uv_dir"
    cleanup
    work=''
    trap - 0 INT TERM HUP
    uv=$uv_local
fi

# No pywebview extra here: its system GUI backends are not available on every Linux/macOS installation.
# The uv cache and this folder are often on different drives; copying is expected there, so skip uv's hardlink warning.
UV_LINK_MODE=${UV_LINK_MODE:-copy}
export UV_LINK_MODE
"$uv" run --project "$root" --frozen --no-dev python -m clawshot.ui "$@"
status=$?
if [ "$status" -ne 0 ]; then
    printf '\nClawshot stopped. The lines above say why.\n' >&2
    pause_on_failure
fi
exit "$status"
