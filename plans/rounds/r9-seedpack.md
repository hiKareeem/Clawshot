# Round 9, Track C: seed packs and map floors (cs9c)

Branch `r9/seedpack`, base `4a0a2f3`. Required AGENTS, README, plans00–04, decisions,
round7/8 records and r6-names read; Round9 opening/shared-file rules apply. No dependency change,
fill/CLI edit, merge, push, stash, game/launcher/batch execution, window or terminal-control command.
Dump, seed8 active output and all save backups are read-only. Scratch: `E:/OOTRemake/work/r9-seedpack-cs9c/`.
One serial worker throughout; initial tasklist reported no matching hookshot.exe.

## Item 1: private source-only packs

Implemented `python -m clawshot.pack --settings CS1... --seed N --out <new.zip>`;
publisher supplies `--romfs` or OOT_ROMFS. Source/data/locked metadata/license/NOTICE included;
plans, tests, environments, outputs, decoded data and game bytes excluded by positive file selection.
Reference is generated from the exact shipped source snapshot in an external disposable directory;
only its whole-output SHA256 is included. Fixed zip metadata and entry order.

Make asks once for RomFS and Hookshot, stores paths only after preflight, invokes frozen uv and
refuses to overwrite existing seeds. Play verifies bytes again before user/log creation and starts
only bin/hookshot.exe with update checks disabled and per-pack --user. Missing bin is a hard stop.
The approved new-game chest-ocarina-storms batch supplied the launch/isolation pattern; no game started.

RomFS contains no NSO build-ID header. Provisional engineering choice by cs9c: fingerprint four known
supported files (ZsDic, GameDataList, EventSetting, child Kokiri Dynamic) to identify build e0f3ccfa
before uv/generation, rather than trust a directory label/Hookshot version. Both PowerShell preflight
and Python compute SHA256 over the four lowercase SHA256 strings with LF. This is not an exefs-ID or
whole-dump integrity assertion; complete generated output must independently match the reference digest.
Only hash values are derived game content in the zip; fingerprint paths are identifiers already used by source.

Tester guide updated in the shared Discord document; separate small commit to be posted.
**Kareem: packs and source remain private to invited testers. After code review, test a pack in a new
external folder: Make -> Verified seed; Play -> isolated new game; require overlay-open log and expected
Mido placements. The agent will not execute Play or any launcher.**

Actual public pack CLI plus extracted Windows PowerShell **Make-only** path passed. Seed8's original
effective CS1 replays **287 checks,24 spheres,129 overlay resources**; all **131 files** including
spoiler/note match `E:/OOTRemake/work/r8-full/seed-full-8` byte-for-byte (same relative paths, none missing).
Reference/extracted/baseline SHA256 all
`a82ac11d0aa0dcb81611c762f4145fe03e0c796d2aecd189e2199bbb64bb49ec`.
Zip has **180 entries**, the required source/templates/license metadata, no plans/tests/seed/game formats.
Proof: external `pack-proof.json`; private artifact `seed-8-private-net-next.zip` and extracted sibling.
These are review artifacts, not a release before TrackA's item-bar guidance/fix is integrated.
No batch, Play, executable or window started; only setup.ps1 `-Action make`.

All five new safety regressions pass: wrong-version pre-generation refusal, complete-tree digest changes,
existing seed non-overwrite, changed-seed launch refusal, missing-bin no-fallback and game-folder isolation.
All four full gates now run as one serial chain with external basetemps; results not assumed.

### Diagnostics before gate checkpoint

First scoped lint printed E501 at pack writer's 126-character context manager; split the context
manager, then format/lint passed. First pytest basetemp setup printed WinError3: external parent
did not exist; created the session's external scratch directory, then all five safety regressions passed.
No test body was run in that setup failure.

First real pack generated successfully, but Windows PowerShell preflight printed `Get-FileHash`
not recognized and stopped before generation on the tester side (exit1). Replaced that cmdlet with
streaming .NET SHA256, retaining the same exact signature format. Also included the repository's
`.python-version` (`3.12`): the first disposable source snapshot without it selected installed3.14.
Removed inherited VIRTUAL_ENV in the publisher's child. No game/launcher was invoked in either probe.
The cause-aimed second proof uses a new `seed-8-private-net-next` zip/folder, never rewrites the first.

## Item 2

Not started: item1 is first in the requested order. No floor is guessed from N64 or Y position.

## Coordination

Posted cs-r9 as cs9c: item order, no planned shared fill/CLI edit, supported-dump fingerprint and scratch-only
output. No request for another track's source files. Python LSP has no configured server (marksman only),
so no Python exported symbols are changed by this new package.
