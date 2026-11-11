#!/bin/sh
# macOS Finder entry point. The macOS launch path is untested.
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P) || exit 1
exec /bin/sh "$root/clawshot.sh" "$@"
