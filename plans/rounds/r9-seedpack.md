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
All four complete gates passed serially before the floor source/data cutover; no Python/TOML/test mutation
during that chain. Basetemps: external `item1-synthetic-next`, `item1-dump-next`. No pools or filtered tests.

| Full command | Observed result |
|---|---|
| `uv run ruff format --check` |229 files already formatted |
| `uv run ruff check` |All checks passed |
| `uv run pytest` |726 passed,86 skipped;319.11s |
| `OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest -m dump` |85 passed,727 deselected;1402.32s |

812 tests collected. Initial tasklist in this chain reported no matching Hookshot process.
Item1 commits: `9370057` pack/tests/source-only oracle, `92aec67` isolated README/Discord guide,
`cc7047a` reviewer-requested Lichii/save-safety docs. Runtime proof is branch-local, not a claim about
the future merged source. No in-game acceptance is invented.

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

## Item 2: room and pause-map floors

Read-only research began after item1 commits `9370057`, `92aec67`; gates remain serial.
The authoritative mapping is **Banc/BancBasedResource/MapParam.byml.zs**, not RSDB/DungeonParam,
Scene/Component/DungeonParam, MapMenuInfo or MapCaptureInfo (those were inspected first).
`<area>.Room[Dynamic.DefaultDungeonRoomIndex].Floor` stores signed logical floors (0=1F,
-1=B1); `<area>.Floor[slot]` starts at `MinFloor` and lists chest `TBox.InstanceID` hashes.
Use the exact icon's floor when a room spans multiple floors, never chest height or N64 room names.

All **134 existing dungeon chest descriptions** resolve:126 by exact icon Hash,8 Ganon trial
chests absent from icon lists by their single-valued room floor. No unresolved/multi-floor guess.
The Remake map texture filenames independently agree with displayed labels (Deku B2..3F,
Well B2/B1, Jabu B1..2F, Fire1F..5F). GTG and Ganon have stored map floors but no matching
floor-texture set; no newly observed pause-map surface is claimed for them.

Fire Temple: exactly **16 chests /5 Skulltulas**, matching Kareem's guide-map count; map icon lists
independently hold16 TBox and5 CollectSign entries. Chest floors:1F five,2F one,3F six,4F zero,
5F four. The timed trio's two extra red-rupee chests and the old Scarecrow check are all5F,
alongside the Hammer. The Bomb-floor shortcut chest is2F even though the boulder maze is3F.
No guide text or decoded map tree goes in the repository.

Boss-heart research first printed KeyError Dynamic for Volvagia's native pickup; the exact actor
payload has no Dynamic override. Printed all eight existing identities plus MapParam.BossRoomId:
seven explicit room values agree; Volvagia uses the unique boss room33, floor0=1F. This is a
boss-room identity join, not a guessed actor default. Implemented coverage includes eight already-supported
BossHeart descriptions and the Ice Cavern Sheik lesson at the mapped Iron Boots chest.

**Kareem: compare the timed trio with Fire5F and the shortcut cell with2F on the pause map.
GTG/Ganon have floor metadata but no shipped dungeon-floor texture set: confirm whether the pause UI
shows a floor number there; until observed, their labels describe stored floor metadata, not a proven UI.**

### Implemented and exercised

Catalogue now has369 descriptions with143 structured floor labels (134 chests,8 native boss pickups,
1 lesson). The one reader renders the floor in names used by spoiler, note and location hints; its
new floor field serializes independently of label punctuation. Logical keys/IDs/rules stay unchanged.
Removed three old hard-coded Deku floor prefixes so a label does not repeat its floor twice.
Python LSP references returned no server; literal fallback found only the one LocationName constructor
and existing spoiler/hint consumers; all consumers use the same reader. Shared reader/coverage edits
are isolated; no fill/CLI/settings/patch algorithm change.

Scoped checks: format/lint passed; names/route/presentation **12 passed**; independent native floor
oracle **1 passed** (0.76s), covering every definition, basement offset, tall-room distinction,
visible floor tokens and physical-ID coverage. The external researcher's first native run printed
Forest Boss Key Hash5306318520835485827 with **no explicit room**, but exact map-icon logical floor2=3F.
Its overstrict room assertion was removed only for exact-icon matches; aimed rerun reports all143
facts with126 icon/8 room chest matches. Production oracle already used the correct icon-first order
and passed on its first attempt. No fake room0, height fallback or narrowed oracle.

Actual public generator CLI, original seed8/effective CS1 into fresh `floors-seed8-next`: **exit0**.
All131 output paths remain; placements and chronological spheres are exactly unchanged.
**142 shuffled locations** display their correct floor (the excluded Well check remains excluded).
The printed play-note rows show timed Scarecrow5F, cracked-floor pit2F, Deku vine-wall2F,
Volvagia pickup1F. Only spoiler/note,16 Mals hint archives and the common size table differ from
r8-full. No Banc, flow, GameData or item placement delta. Retained `floors-output-proof.json`,
`floors-cli.log`, `floor-facts.json` and reusable `floors.py` outside the repo.

All four complete gates will run again on this final floor cutover before readiness/handoff.

## Coordination

Posted cs-r9 as cs9c: item order, no planned shared fill/CLI edit, supported-dump fingerprint and scratch-only
output. No request for another track's source files. Python LSP has no configured server (marksman only);
the floor-reader references attempt/fallback is recorded above. No existing pack/CLI API is replaced.

Reviewer steer: cs9b `806b1c7` changes Sheik text in16 Mals archives. The exact-r8-full comparison
is branch-local historical proof only. Pack `build()` computes each oracle by generating from the source
snapshot it ships, never from a stored r8-full seed digest. Claude will rebuild into a NEW zip/folder after
merges (floor-labelled hint names also legitimately change Mals). Posted acknowledgement on cs-r9.

Reviewer docs-only steer: Kareem played seed8 successfully in Lichii (Eden/yuzu family), recorded on
main `d3e5c08` in answers R9-LICHII. That new answer is not in this worktree's base; the reported
player result is accepted, not rerun. Added Lichii's confirmed LayeredFS destination and Add-ons steps
to `docs/seed-pack.md` and the Discord tester guide; clearly marked Ryujinx/Atmosphere paths untested.
New Game takes over this game's emulator save slots: back up first; Hookshot user isolation does not
apply; unticking a mod does not restore saves. No Make/Play behavior change. No emulator/window started.
Current Make still asks for a valid Hookshot folder; the emulator instructions replace only Play.

Removed only the completed session-created smoke_pack.py driver after its successful proof;
reference zip, extracted output, proof JSON, player checklist and reusable floor researcher are retained.
