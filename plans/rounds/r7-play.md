# Round 7, Track F: graveyard and bombs from play (cs7f)

Branch `r7/play`. Required AGENTS/README, plans 00–04, decisions and round-5/6 reports read;
Round 7 shared-file opening applies. No dependency edit, game/window/launcher/build, save edit,
dump write, active-overlay rewrite, merge, push, stash or terminal-control command.
Read-only research/decoded data stays in `E:/OOTRemake/work/r7-play-cs7f/`.

## Item 1: the three pull-back graves

Source observation: Kareem via Claude, 2026-11-08, Hookshot 2.0.1: from the Royal Family's Tomb,
fourth grave from the right is unmarked and contains a ReDead and chest; a marked grave has a cracked wall.
His graveyard loaded vanilla during the reported overlay gap; this is not a shuffled-chest acceptance result.

`graves.py` independently reads both ages' Static/Dynamic placements with the project's reader. Coordinates
are x/y/z, metres, y up. Stand at the Royal Family's Tomb entrance (48.4,104.6,2.6), **face out over the
graveyard**, not toward the tomb. Kareem's shield-grave observation calibrates right-to-left as increasing z:

| Grave | Where from that viewpoint | Surface hole (child Hash) | Underground |
|---|---|---|---|
| ReDead / shield | Nearest row of seven; fourth from right, unmarked | (21.47,103,11.2), `13042589291289571846` | ReDead `17994273783244561622`; chest `16912540161937823130` (38.3,86.3,11.2) |
| Heart-piece chest | Same seven-grave row; leftmost, seventh from right | (21.39,103,23.15), `14989078271173641200` | Chest `9622128545943056087` (21.4,85.8,39.3); no enemy/song puzzle |
| Marked fairy grave | Lower row of five (farther from tomb); second from right, flowers/butterflies | (4,101.5,5.75), `11636637601453373828` | `WallCrack` `9366825990748670811` (3.94,83.92,27); passage to pool around (-21,84,34), **eight `Obj_Fairy`, no chest/check** |

The last two ordinals are placement-derived, not new gameplay observations. Both chest catalogue rows now
use this single viewpoint. The fairy-only grave is explained as a non-check, not fabricated as a catalogue
location or added to the pool. Existing Shield Grave `Fairy` capability folds the separate third grave into
an equivalent entrance rule plus `can_blast_or_smash and has_bottle`; no new region is needed for this audit.

Heart chest remains `True` **inside** the grave. Both age Static copies have only
`Drop__DropActor=Obj_Heart_Piece` in Dynamic; no Presence, SpawnType override, links or AiGroup reference to
that chest in either age's pair. Native `SpawnType=0`; no Sun's Song, wall or clear trigger binds it. The only
wall AI group binds the fairy wall: `Graveyard_Common_8f81`, death -> 60-frame timer -> riddle sound,
not chest creation. Child entrance still requires night plus `Time Flows`; no adult requirement was added.
Shield combat and all other access rules are unchanged.

Guide corroboration (facts only):
https://www.nintendolife.com/guides/zelda-ocarina-of-time-heart-piece-locations-switch-2 (#8),
https://www.ign.com/wikis/ocarina-of-time-remake/Spiritual_Stone_of_Fire_-_Kakariko_Village_Walkthrough .

### Diagnostics

- First probe used `str(U64)` for reference comparison. Printed `U64(7)`, `int=7`, `isinstance(int)=True`:
  typed numbers' repr is not decimal. Normalize to builtin numbers; the corrected probe finds the wall group
  and no chest group. No absence conclusion was retained from the faulty comparison.
- External GPL `ainb` 0.2.16 failed decoding the chest expression string pool: `ParseWarning.__init__`
  missing `msg`. Printed the signature `(reader, msg)`, failing call and 22,242-byte chest header.
  Upstream `main/ainb/utils.py` removes that erroneous duplicate-string warning call. Installed **unmodified
  0.2.17 in a new external venv only**, and the cause-aimed decode passed (two chest graphs). No GPL code,
  dependency or decoded tree enters the repository; no NX2navi code/docs read.
- `uv pip index versions ainb` is unsupported (exit 2, printed command usage); used PyPI's JSON release metadata
  instead. No unchanged command retry.

Full gates will run on the final tree before any commit is posted ready. Targeted/runtime results follow.

### Item 1 checks

`uv run pytest tests/test_world_remake_play.py -k grave -q`: **2 passed, 21 deselected**.
Scoped ruff format/lint passed. Actual full-world `load_world`/`Search` plus catalogue reader smoke:
child with Gohma exit and `Time Flows`, no weapon/song/bombs, reaches the heart chest but not the
guarded shield chest. Rendered both player directions. No in-game observation is claimed.
