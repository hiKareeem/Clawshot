# Tracker in logic (PR #36, BBender)

Design record for the Tracker's in-logic display and manual marks, contributed by BBender in
[PR #36](https://github.com/hiKareeem/Clawshot/pull/36), with the maintainers' review changes.
Player guide: [tracker guide](../docs/tracker.md#in-logic). Part 1 is the spec, Part 2 the implementation plan.

Maintainer review (2026-11-20): the child Hylian Shield rule for the Kokiri Storms Grotto scrubs (commit 4c02f84)
was reverted: it contradicted Kareem's played note in `03-game-data.md` and needs its own PR with a played check.
Marks are keyed per seed and save folder; Bombchus count once `IsGet.Item_Bombchu` is set; hearts and the
missing-marks-file behavior are as the PR describes. Marks warnings carry no file path and stay off the OBS view.

## Part 1: spec

Status: draft, 2026-11-20. Decisions below were made by BBender in a design interview with Claude (Opus 5.5);
"(rec)" marks where BBender took Claude's recommendation. Revised 2026-11-20: Background corrected and D15 added
after plan item 1.3 found the generator's world is not `validate` + `prepare` alone. Revised 2026-11-20 after the
main maintainer's review: D11 default age is Either; Either is `can_access(location)` with no age; save items go to
the search the way the generator feeds its own (closed return gate); marks live beside the preferences (D9); the
version gate also checks the spoiler's locations (D14); story-flag logic items (2.2); Ruto's Letter follows
`has_bottle` (2.7); Q1 and Q2 answered. Decisions marked "(maint)" are the maintainer's. Revised 2026-11-21: D19 and
section 8 (fixed vanilla pick-ups as tracker rows) added after play showed Jabu-Jabu stays out of logic with no open
check pointing at Ruto's Letter; proposed by Claude, chosen by BBender, **awaiting the maintainer**. Revised
2026-11-21 after a grill-me interview with BBender: Q3, Q4 and Q5 answered (BBender; the maintainer still to
approve), and Q6 (the Goron Bracelet) left for the maintainer (end of this file).

### Goal

The Tracker tab shows which of the seed's still-open checks are **in logic** right now: reachable with what the
player's save holds, by the seed's own logic. Checks whose collection the save cannot read (`?`: shops, swap-only
gifts, unset placement-hash pickups, unaudited event gates) can be marked done by hand so they leave the open list.

### Background (what exists)

- `clawshot.world.search.Search(world, items)` answers `can_access(location, age)` per age, and
  `can_access(location)` (no age) for "either age" by the search's own age rules. The constructor adds
  `world.start_items` and then the given items through `collect`. While `world.age_return` is closed the child view
  keeps separate counts (`_child_counts`, `search.py` `__init__`), so "granted to both ages" holds only for items
  fed in this way, not for everything the search later finds; the generator feeds assumed items through the
  constructor (`generate/fill.py`, e.g. `Search(world, [*assumed, *items])`). Events (Master Sword pull, age return,
  dungeon clears) are derived by the search itself.
- The spoiler holds the canonical CS1 `settings_string` and `generator`. `app.schema.validate(text=...)` plus
  `generate.prepare.prepare(spec, settings)` do **not** alone rebuild the `World` the generator searched: before
  `prepare`, the seed pipeline changes the spec, and two of those changes alter reachability (found 2026-11-20 while
  checking plan item 1.3):
  - Gift/NPC shuffle: `patch.gifts.shopkeeper_spec` (applied in `gifts.seed_setup`) turns the shopkeeper's free
    "Deku Shield" event into a placed check. Without it the search grants Deku Shield on reaching the shop.
  - Scrub shuffle: `patch.scrubs.seed_setup` (applied in `make_seed`) adds each one-time sale's wallet tier to its
    rule. Without it unaffordable scrubs read as reachable.
  The other pre-`prepare` changes (gift `restrict_spec`, bowling `n64_only`, `freestanding.restrict_spec`,
  `restrict_event_openings`, drop/freestanding palettes) only set `keep_vanilla`, exclusions, types or fill
  palettes, not reachability. Neither reachability change needs the dump.
- `tracker.state` already reads items, songs, rewards, hearts, tokens, bottles and per-dungeon key counts
  (held and found) from the save, and gives each shuffled check a three-state `collected` (True/False/None).
- The save holds `Sequence_IsChildhood` (Bool, file 0, default true; `plans/rounds/r18-master-sword-design.md`).
  Natural play keeps it right; Longshot's debug age switch does not change it.
- `has_bottle` (`world/rules.py`) is true when any item with `bottle = true` is held, or when `Rutos Letter` is held
  twice or more: one letter held is the letter, not a bottle.
- Some story steps are logic names too (for example `Met Child Zelda` and `Field Owl Arrival`, events in
  `data/world/remake/child_hyrule_castle.toml`).
- User preferences live in `app/preferences.py`'s folder (`%APPDATA%\Clawshot` on Windows, macOS/XDG
  equivalents); the icon cache (`%LOCALAPPDATA%\Clawshot\Cache\icons`) is safe to delete and holds no user data.
- The OBS view already strips `areas[].checks`.
- Tracker rows come only from the spoiler's `placements`, which hold only the seed's shuffled locations
  (`generate/__init__.py`, `seed.shuffled`). A location the seed does not shuffle (type not selected,
  `keep_vanilla`, not admitted as a gift) keeps its vanilla item and has no row. The generator's beatability search
  collects those vanilla items when it reaches them; the tracker's search (D1, D16) counts only what the save holds.
  So a fixed vanilla item that opens progress is invisible until picked up. Found 2026-11-21: `LH Underwater Item`
  (Ruto's Letter, type `NPC`, a placed pick-up with no gift flow step, `plans/03-game-data.md` section on gifts) is
  never shuffled; Jabu-Jabu (`is_child and Fish`, where `Fish` needs `has_bottle`, i.e. `Deliver Letter`) showed no
  in-logic checks and no open check said why, until the letter was picked up.
- Size, on a Chest-only seed (seed 2445192976's settings, 2026-11-21): 299 non-shuffled locations hold a progression
  item (100 Gold Skulltula tokens, 80 silver rupees, 27 heart pieces, the rest NPC/song/cutscene/boss/mask-shop
  gifts). 61 of them hold an item that only that location gives in the world (every song, the ocarinas, the trade
  chain, Ruto's Letter, Zelda's Letter, the Weird Egg, Gerudo card, Great Fairy spells, masks, boss rewards when
  not shuffled).

### Decisions

| # | Topic | Decision |
|---|-------|----------|
| D1 | Logic inventory source | The tracker's existing save-read holdings, mapped to logic item names. Not the spoiler's placements. |
| D2 | Items that leave the inventory (trade items, Ruto's Letter, eaten/burnt shields) | Count if held now **or** the save's acquired-once flag is set (rec). An item with no known acquired-once flag counts only when held now, as D4 (Q2 answered (maint)). |
| D3 | Small keys | Use the dungeon's **found** count (including spent keys), not held (rec). |
| D4 | Unknown save fields (`?`) | Item counts as **not held** (rec). |
| D5 | Unknown checks without a manual mark | Count as **not collected** (still open) (rec). |
| D6 | Manual mark effect | Marks the check done (leaves the open list). Does **not** add its item to the logic inventory (rec). |
| D7 | Manual mark spoilers | A marked check's item stays hidden in spoiler-free mode; only spoiler mode or save confirmation shows it (rec). |
| D8 | Which checks can be marked | Only checks whose save state is unknown (`collected is None`). A save-confirmed state wins over and drops a mark. |
| D9 | Mark storage | JSON in Clawshot's preferences folder (beside `app/preferences.py`'s file, not the deletable icon cache), never in seed, save or game folders (rec; folder (maint)). |
| D10 | Mark scope | Per seed (by `output_sha256`, else a hash of the spoiler file) and per save slot (rec). |
| D11 | Age display | Selectable: **Either** (default), Follow save, Child, Adult. Either means `Search.can_access(location)` with no age, so tracker and generator agree. Follow save reads `Sequence_IsChildhood`; unreadable falls back to Either and says so. A chosen option persists until changed (rec; default Either (maint): with Follow save a child would see adult-only checks as out of logic even when they can become adult, and other randomizer trackers count both ages). |
| D12 | Display | Every open check gets an in-logic / out-of-logic style, each area shows "N in logic", and a "Show only in-logic" toggle hides the rest (rec). |
| D13 | OBS | Unchanged in v1 (rec). |
| D14 | Version gate | In-logic is computed only when the spoiler's `generator` equals `clawshot <installed version>` exactly, the world rebuilds from its settings string, and every location named in the spoiler exists in the rebuilt world; otherwise it is disabled with the reason shown, and item tracking continues (rec; location check (maint): `generator` carries no commit, so two builds from `main` with one version can differ in logic). |
| D16 | Save items into the search | The logic inventory is fed to `Search` the way the generator feeds its own assumed items (constructor `items`), so the closed-return-gate child view behaves as in generation (maint). |
| D17 | Story-flag logic items | Story steps that are logic names map to their save flags where the flag is known; otherwise they are listed as unmapped with a reason (maint). |
| D18 | Ruto's Letter and bottles | Follow `has_bottle`: a bottle slot holding the letter counts as the letter only, never also as a bottle (maint). |
| D19 | Fixed vanilla pick-ups | While logic is available, the tracker also lists **vanilla rows**: non-shuffled locations whose vanilla item is progression, shown with that item and the same in-logic flags as other open checks. Logic itself is unchanged (still D1/D16: only what the save holds); the alternative of letting the tracker's search collect reachable vanilla items like the generator was rejected, since it reports areas in logic while hiding which pick-up they wait on. Default scope and toggle are Q3/Q4. Proposed by Claude, chosen by BBender, 2026-11-21; awaiting the maintainer. |
| D15 | Logic world source | One shared, dump-free builder of the seed's logic world (the reachability-changing spec steps, then `prepare`) used by both the seed pipeline and the tracker, so the two cannot drift. Proposed by Claude, chosen by BBender over a tracker-side copy of the steps or storing the world in the spoiler (rec). |

### Acceptance criteria

#### 1. Logic world

- **1.1** For a seed whose `generator` equals `clawshot <installed version>`, the tracker rebuilds the seed's
  `World` from the spoiler's settings string with the same code path the generator uses: `validate` and then the
  shared logic-world builder (D15).
- **1.5** The shared builder needs no dump. The seed pipeline (`make_seed`, with gift setup) searches a world equal
  in regions, exits, events, locations, location rules and items to the builder's world for the same settings;
  a test shows this on synthetic settings with Gift/NPC and Scrub shuffle on and off.
- **1.6** Introducing the builder changes no generated seed: same seed and settings give a byte-identical output
  folder and spoiler before and after (AGENTS.md rule 4).
- **1.2** The world is built once per loaded seed and cached; save polls do not rebuild it.
- **1.3** When the generator string differs, the settings string is missing, validation/prepare raises, or a
  location named in the spoiler is missing from the rebuilt world (D14), the state carries `logic.available = false` with a human-readable `logic.reason`, no check carries in-logic data, and
  every existing tracker field is unchanged.
- **1.4** The tracker never writes to the seed folder, save folder, game dump or game folder while computing logic.

#### 2. Logic inventory

- **2.1** The inventory is built only from the tracker's save-read state (items, upgrades, songs, stones,
  medallions, hearts/pieces, Gold Skulltula token count, bottles, magic, dungeon items), plus the world's starting
  items. Spoiler placements are not used to build it. It is handed to `Search` as the constructor's `items`, the
  way the generator feeds its own assumed items (D16); a test with the age-return gate still closed shows the
  tracker's per-age results equal a search built the generator's way from the same items.
- **2.2** The mapping from tracker cells to logic item names lives in a data file, not in Python branches. Every
  progression item of the world is either mapped or listed as unmapped with a reason; a test fails when a
  progression item is neither. Story steps that are logic names (for example `Met Child Zelda`,
  `Field Owl Arrival`) map to their save flags where the flag is known, else they are listed as unmapped (D17).
- **2.3** Tiered/progressive cells grant as many copies of the progressive logic item as the held tier
  (e.g. Longshot = two Progressive Hookshot).
- **2.4** A trade item, Ruto's Letter or a shield counts as held when the save holds it now or its acquired-once
  flag is set (D2). An item without a known acquired-once flag counts only when held now.
- **2.5** Small keys per dungeon use the found count, including spent keys (D3). Boss keys, maps and compasses use
  their saved flags.
- **2.6** A cell whose save value is unknown contributes nothing (D4), and the state lists those cells in
  `logic.unknown_items` so the UI can say the result may be conservative.
- **2.7** Bottles follow the logic's `has_bottle` (D18): each owned slot without the letter counts as a bottle item;
  a slot holding Ruto's Letter counts as one `Rutos Letter` and not also as a bottle, so the letter is never counted
  twice.

#### 3. In-logic per check

- **3.1** A check is **open** when its save state is not collected, or unknown and not manually marked (D5).
- **3.2** For each open check the state reports `in_logic`: `child` and `adult` from
  `Search.can_access(location, age)`, and `either` from `Search.can_access(location)` with no age (not the OR of
  the two).
- **3.3** Collected checks and manually marked checks carry no in-logic flag and never count as in logic.
- **3.4** Each area reports `in_logic` counts for child, adult and either age (either from 3.2's `either`).
- **3.5** The search is recomputed only when the logic inventory changes, not on every poll.
- **3.6** Showing in-logic status reveals no item: an open check's entry contains no `item`/`item_label` unless
  spoiler mode is on, as today.

#### 4. Manual marks

- **4.1** In the app tab, a check whose save state is unknown can be toggled between unknown and "marked done by
  you". Checks with a save-confirmed state cannot be marked.
- **4.2** A marked check is shown distinctly from a save-confirmed collected check, and counts as done in area
  counts and the open list.
- **4.3** A mark does not add the check's item to the logic inventory (D6).
- **4.4** In spoiler-free mode a marked check's item stays hidden (D7).
- **4.5** When a later save reads the marked check as collected or not collected, the save's state is used and the
  mark is removed from storage.
- **4.6** Marks are stored as JSON in Clawshot's preferences folder (the parent of
  `app.preferences.user_preferences_path()`: `%APPDATA%\Clawshot` on Windows, macOS/XDG equivalents; not the
  deletable cache folder),
  keyed by seed identity (`output_sha256`, else SHA-256 of the spoiler file) and save slot path. Nothing is written
  in seed, save or game folders.
- **4.7** Marks survive a Clawshot restart and are separate per seed and per slot: a different slot of the same
  seed starts with no marks.
- **4.8** A "Clear manual marks" control removes all marks for the current seed and slot after a confirmation.
- **4.9** The mark endpoint is a POST behind the server's existing token/Host/Origin checks and rejects unknown
  check ids, checks not currently unknown, and requests without a configured seed and slot.
- **4.10** An unreadable marks file is reported as a warning and treated as empty; a missing one is treated as empty
  without a warning (a fresh install has none; maintainer review, 2026-11-20). Neither is overwritten until the user changes a
  mark.

#### 5. Age selection

- **5.1** The Tracker tab has an age control: Either (default), Follow save, Child, Adult.
- **5.2** Follow save uses Child when `Sequence_IsChildhood` is true and Adult when false. When the Bool is
  unreadable, it uses Either and shows a one-line note.
- **5.3** A chosen option other than the default persists across reloads in the browser (localStorage, every access
  wrapped in try/catch) until the user changes it; the page works when storage is unavailable.
- **5.4** The in-logic styling, area counts and the filter all follow the selected age.

#### 6. Display

- **6.1** In Checks by area, each open check is styled in-logic or out-of-logic for the selected age; collected and
  marked checks keep their own styles.
- **6.2** Each area heading shows "N in logic" for the selected age next to its existing counts.
- **6.3** A "Show only in-logic" toggle hides open out-of-logic checks, collected and marked checks; areas with no
  visible check collapse.
- **6.4** When logic is unavailable (1.3), the age control and filter are disabled and the reason is shown; the
  rest of the tab works as today.
- **6.5** When `logic.unknown_items` is not empty, the tab shows one line saying in-logic may be conservative,
  naming the unknown cells.
- **6.6** The OBS view (`tracker-obs`) payload and rendering are unchanged (D13); logic and marks data are not
  included in it.

#### 7. Docs and checks

- **7.1** `docs/tracker.md` gains an "In logic" section covering D1–D18 as the player sees them, including that
  Follow save reads `Sequence_IsChildhood`, which Longshot's debug age switch does not change. Its "Nothing is
  created or changed by tracking" statement is reworded to "nothing in your game, seed or save folders" with the
  marks file's location (Q1 approved by the maintainer).
- **7.2** Synthetic-fixture tests cover: version gate (1.3), inventory mapping including tiers, trade
  acquired-once, found keys and unknown fields (2.x), the closed age-return gate (2.1), Ruto's Letter in a bottle
  (2.7), per-age and either-age in-logic on a small custom world (3.x), the spoiler-location gate (1.3), marks
  lifecycle and isolation per seed/slot (4.x), Follow save from `Sequence_IsChildhood` (5.2), and OBS payload
  unchanged (6.6).
- **7.3** `uv run ruff format --check`, `uv run ruff check` and the test suite pass. The suite is run with
  `uv run --with pytest-xdist pytest -n auto` (much faster than plain `pytest`); tests needing a game dump skip
  without one.
- **7.4** In-game acceptance (maintainer run, not by an agent): with a Clawshot Play seed, save after collecting a
  few items, and confirm the Tracker's in-logic list matches what is reachable in game for that age; buy a shop
  item, mark its check, restart Clawshot, and confirm the mark persists and the shop's item is hidden in
  spoiler-free mode.

#### 8. Vanilla rows (D19)

- **8.1** With logic available, the state lists one vanilla row per world location that is not in the spoiler's
  `placements`, holds a vanilla item of class progression, is not `n64_only`, and is in the default scope (Q3). The
  list is built from the rebuilt world (1.1) in world order, once per loaded seed. With logic unavailable (1.3)
  there are no vanilla rows.
- **8.2** A vanilla row carries `vanilla: true`, the location's name and description where the location catalog has
  one (else the OoT Randomizer name), its area (the census area, else the area of the location's region), and its
  vanilla item. The item is shown in spoiler-free mode too: the settings, not the seed, decide it.
- **8.3** Collected: `true` when the vanilla item counts as held by 2.x (held now, or its acquired-once flag, D2),
  `false` when the save reads the item's cells and they say not held, `null` otherwise. This uses the item only when
  no shuffled check of the seed can also give it (the item is unique to this location among the world's vanilla
  items and absent from the seed's placements); otherwise the row's state is `null`. A `null` row can be marked
  done like any unknown check (section 4, same rules and storage).
- **8.4** An open vanilla row gets `in_logic` exactly as 3.2. The in-logic search is the same search as the
  shuffled checks' (no extra items).
- **8.5** Vanilla rows are counted separately per area (`vanilla` counts: total, done, in logic per age); the
  existing area counts and per-area check totals are unchanged.
- **8.6** The Tracker tab shows vanilla rows within their area, styled as vanilla (for example a "vanilla" tag), and
  a "Show vanilla pick-ups" toggle (default per Q4, persisted like 5.3). "Show only in-logic" (6.3) applies to them
  too.
- **8.7** The OBS payload and rendering stay unchanged (D13, 6.6): no vanilla rows or counts.
- **8.8** Synthetic-fixture tests: a custom world where a non-shuffled location holds an item that gates another
  region shows the row open and in logic, the gated check out of logic; after the save holds the item the row is
  collected and the gated check is in logic. Also: a vanilla item that a shuffled check could give yields
  `collected: null`; shuffled-check state and area counts are equal with and without vanilla rows.
- **8.9** `docs/tracker.md` "In logic" section explains vanilla rows and why they exist (a fixed pick-up such as
  Ruto's Letter can gate a whole area).

### Out of scope (v1)

- In-logic in the OBS view.
- Marking save-confirmed checks, or adding a marked check's item to the inventory.
- Live (unsaved) progress; the tracker still reads saved progress only.
- Entrance-aware or hint-aware tracking beyond what the seed's world already encodes.

### Maintainer questions (answered 2026-11-20)

- Q1: Rewording of the "nothing is created or changed by tracking" promise (7.1). **Approved**: "nothing in your
  game, seed or save folders", plus where the marks file lives.
- Q2: Whether the acquired-once rule (D2) should also apply to items without an audited acquired-once flag.
  **Held-now only** for items without a known acquired-once flag, matching D4.

### Questions answered by BBender (2026-11-21, grill-me; the maintainer still to approve)

- Q3: Default scope of vanilla rows (D19, 8.1). Proposed (Claude): only locations whose vanilla item no other world
  location gives (61 on a Chest-only seed: songs, ocarinas, trade chain, Ruto's and Zelda's Letters, Weird Egg,
  Gerudo card, spells, masks, unshuffled boss rewards). Gold Skulltula tokens, silver rupees, heart pieces and other
  repeated items stay out by default, since a single one rarely gates progress and 238 more rows would bury the
  list. Alternative: every progression item (299). **Answer (BBender): unique items only**, as proposed.
- Q4: Whether "Show vanilla pick-ups" (8.6) defaults on or off. Proposed (Claude): on, since the problem it solves
  is a gate the player does not know to look for. **Answer (BBender): on.**
- Q5: Vanilla rows whose item the save has no one-time record for (Treasure Chest Game heart piece, Granny's Blue
  Potion, the Magic Bean salesman). **Answer (BBender): keep them as `?` rows** with in-logic styling and Mark done,
  so a gate such as the bean salesman stays visible; finding save flags for them is later work needing in-game
  evidence.
- The app tab lists check names with spoilers off, items hidden (6.1 needs something to style): proposed by
  Claude, confirmed by BBender. (Bombchus once found, marks per seed and save folder and the missing marks file are
  the maintainer review's, 2026-11-20, at the top of this file.)
- Q6, open for the maintainer: the Goron Bracelet. Seed child logic reads `'Goron Bracelet'` from Darunia's native
  gift only (`world.toml` `Progressive_Strength_Upgrade`; `rounds/r14-progressive.md`: an early copy Bracelet works
  out of logic and logic never relies on it), while the strength cell grants `Progressive Strength` copies and lists
  the Bracelet unmapped. So the tracker never counts the Bracelet: a child who has Darunia's gift still sees the
  bomb-flower areas out of logic, and the vanilla row `GC Darunias Joy` shows `?` (markable). Claude first mapped
  every strength tier to the Bracelet as well; that was dropped before merge because it lets a copy or adult
  gauntlets stand in for it, against that note. Question: is there a saved record of Darunia's gift that the
  tracker could read for `Goron Bracelet`, or should it stay unmapped?

## Part 2: plan

Spec: Part 1 above. Criteria keep the spec's identifiers (e.g. `1.3`); criteria added by
this plan are marked `P` (e.g. `P2.a`). Touch points found in the code today:

- `src/clawshot/tracker/seeds.py` (`load_seed`, `Seed.metadata`, `installed_version`, `output_sha256`)
- `src/clawshot/tracker/state.py` (`build_state`, `areas`, `_check_entry`, `collected`, `_Reader`)
- `src/clawshot/tracker/saves.py` (`TrackerSession.configure` / `_poll`)
- `src/clawshot/ui/tracker.py` (`TrackerController`, `call`), `src/clawshot/ui/server.py` (token/Host/Origin checks)
- `src/clawshot/ui/static/tracker.html|js|css`
- `src/clawshot/world/search.py` (`Search`), `src/clawshot/generate/prepare.py` (`prepare`), `src/clawshot/app/schema.py` (`validate`)
- `src/clawshot/patch/gifts.py` (`shopkeeper_spec`, `seed_setup`), `src/clawshot/patch/scrubs.py` (`seed_setup`),
  `src/clawshot/patch/__init__.py` (`make_seed`), `src/clawshot/__main__.py` and `src/clawshot/app/jobs.py` (the two
  callers of `gifts.seed_setup` + `make_seed`)
- `src/clawshot/app/preferences.py` (`user_preferences_path`, the preferences folder the marks file sits in)
- `src/clawshot/world/search.py` (`Search.__init__` closed-return-gate child view, `can_access(location, age=None)`),
  `src/clawshot/world/rules.py` (`has_bottle`), `src/clawshot/generate/fill.py` (how the generator feeds items)

Revised 2026-11-20 after the main maintainer's review (see the spec's revision note); "(maint)" marks their calls.
Tests run with `uv run --with pytest-xdist pytest -n auto`; dump tests skip without `OOT_ROMFS`.

1. [x] Check prerequisites and open questions
    1.1 [x] `uv run ruff format --check`, `uv run ruff check` and `uv run --with pytest-xdist pytest -n auto` pass on `main` before any change (baseline recorded). Baseline 2026-11-20 on the branch's start: format and lint pass; 3806 passed, 499 skipped (12 min, -n auto).
    1.2 [x] Work happens on a feature branch (not `main`); the PR description records the maintainer's answers to Q1 (rewording approved) and Q2 (held-now only without a known acquired-once flag) and the review changes D9, D11, D14, D16–D18. Branch `feature/tracker-in-logic`; PR description pending (task 15).
    1.3 [x] Confirmed by reading code that `validate(text=...)` + `prepare(spec, settings)` is the generator's own path to the searched `World`; any difference is reported instead of worked around. Result: it is not (spec Background); resolved by D15 and task 2.

2. [x] Shared logic-world builder (D15; new module `src/clawshot/patch/logic_world.py`)
    2.1 [x] P2.a `scrubs.seed_setup`'s spec change (sale type and wallet-tier rule) is split into a dump-free `scrubs.logic_spec(spec, settings)`; `seed_setup` calls it, with no change to its results (existing scrub tests pass unchanged).
    2.2 [x] 1.5 `logic_world(settings, spec=None) -> (Settings, World)` applies `gifts.shopkeeper_spec` (Gift or NPC shuffled) and `scrubs.logic_spec` (Scrub shuffled), then `prepare`; it reads no dump (test runs it with no `OOT_ROMFS` and a monkeypatched romfs access that fails if called).
    2.3 [x] 1.5 `gifts.seed_setup` and `make_seed` take their reachability-changing spec steps from the shared builder's functions, so there is one definition of each step (no copied transform). Gift half's test (`test_gift_seed_setup_uses_the_shared_step`) is `dump`-marked: not yet run (no `OOT_ROMFS` on the agent's machine).
    2.4 [x] 1.5 Equivalence test: for synthetic settings with Gift/NPC and Scrub shuffle on and off, the world `make_seed` hands to `generate` (captured by monkeypatching `generate`) equals `logic_world`'s in regions, exits, events, locations, location rules (source text) and items. The test is `dump`-marked if `make_seed` needs a romfs, and a synthetic-spec variant covers the spec steps without one. Synthetic variant passes; `dump` variant `test_make_seed_searches_the_logic_world` not yet run (no `OOT_ROMFS`).
    2.5 [x] P2.b `logic_world` gives the same world for the user's settings string and the effective one the spoiler stores (gift types expanded from `Gift`), since the tracker only has the latter.
    2.6 [x] 1.6 Determinism: a seed generated before and after the refactor (synthetic world via `generate`, plus `make_seed` under `-m dump`) gives byte-identical output and spoiler. Synthetic: 12 spoilers (Chest/Scrub/Gift/Gift+Scrub x seeds 1-3, full spec) hashed before and after: identical (agent, 2026-11-20). `make_seed` half rests on the `dump` tests (`test_seed_dump.py`, the 2.4 dump test): not yet run.

3. [x] Logic world loader (new module `src/clawshot/tracker/logic.py`)
    3.1 [x] 1.1 For a seed whose `generator` equals `clawshot <installed version>`, the tracker rebuilds the seed's `World` from the spoiler's settings string with `validate` + `logic_world`.
    3.2 [x] 1.2 The world is built once per loaded seed and cached on the session; save polls do not rebuild it (test counts `logic_world` calls across several polls).
    3.3 [x] 1.3 Generator mismatch, missing settings string, an exception in validate/`logic_world`, or a spoiler location missing from the rebuilt world (D14; reason names the first missing location) yields `logic.available = false` with a human-readable `logic.reason`; no check carries in-logic data; every existing tracker field is unchanged (test compares the state with and without the logic layer).
    3.4 [x] 1.4 Computing logic writes nothing to seed, save, dump or game folders (test snapshots those synthetic folders' trees and mtimes before/after).
    3.5 [x] P3.a The `Seed` exposes the spoiler's `settings_string` and `generator` (read in `load_seed`), with no change to existing `Seed` fields.
    3.6 [x] 1.3 Spoiler-location gate test: a synthetic spoiler naming a location the rebuilt world lacks gives `logic.available = false` with that location in `logic.reason`; a spoiler whose locations all exist passes the gate.

4. [x] Logic inventory mapping data (new file `src/clawshot/data/tracker_logic.toml`)
    4.1 [x] 2.2 Mapping from tracker cells (items, upgrades, songs, rewards, hearts, tokens, bottles, magic, dungeon items) to logic item names lives in the TOML file, with an `unmapped` table giving a reason per progression item not mapped.
    4.2 [x] 2.2 A test fails when a progression item of the world is neither mapped nor listed as unmapped.
    4.3 [x] 2.3 Tier cells map each held tier to a copy count of the progressive logic item (e.g. Longshot = 2 Progressive Hookshot), checked against `clawshot.progressive` tiers by a test.
    4.4 [x] P4.a Every logic name in the file exists in the world's item table or event names (test), and every cell id exists in `tracker.state` (test).
    4.5 [x] 2.2 Story-step logic names (e.g. `Met Child Zelda`, `Field Owl Arrival`) map to their save flags where the flag is known, else appear in `unmapped` with a reason (D17); the 4.2 test is expected to list them until they are handled. Field Owl Arrival and Met Child Zelda map to their flags (sources in the TOML); the other remake-added story events are listed unmapped.

5. [x] Logic inventory builder (`tracker/logic.py`)
    5.1 [x] 2.1 The inventory is built only from the tracker's save-read state plus the world's starting items; a test with a spoiler whose placements differ shows no change in the inventory.
    5.2 [x] 2.4 A trade item, Ruto's Letter or a shield counts as held when held now or its acquired-once flag is set (test for each case: held, flag only, neither); an item without a known acquired-once flag counts only when held now (Q2, test).
    5.3 [x] 2.5 Small keys per dungeon use the found count including spent keys; boss keys, maps and compasses use their saved flags.
    5.4 [x] 2.6 A cell whose save value is unknown contributes nothing and is listed in `logic.unknown_items`.
    5.5 [x] 2.7 Bottles follow `has_bottle` (D18): each owned slot without the letter gives one bottle item; a slot holding Ruto's Letter gives one `Rutos Letter` and no bottle item (test: letter-only save has `has_bottle` false; letter plus an empty bottle has it true; letter counted once).
    5.6 [x] P5.a The inventory is a sorted, deterministic multiset (same save gives the same inventory, byte-equal JSON).
    5.7 [x] 2.1 The inventory goes to `Search` as the constructor's `items`, as the generator feeds assumed items (D16); test on a synthetic world with `age_return` closed: the tracker's child/adult/either results equal those of `Search(world, items)` built directly, and a child-only check reached via an item the save holds stays in logic for child.
    5.8 [x] P5.b `Search` adds `world.start_items` itself; to avoid counting starting items twice, the tracker passes per name the save's count minus the starting count (floored at 0), so each item counts as the larger of the two (test with a starting item the save also holds). Proposed by Claude; raised in the PR.

6. [x] In-logic per check (`tracker/logic.py` + `tracker/state.py`)
    6.1 [x] 3.1 A check is open when its save state is False, or None and not manually marked.
    6.2 [x] 3.2 Each open check carries `in_logic: {child, adult, either}`: `child`/`adult` from `Search.can_access(location, age)`, `either` from `Search.can_access(location)` with no age (test on a small synthetic custom world where one check is child-only, one adult-only, one neither, plus a case where `either` differs from `child or adult`, or, if the search cannot produce one, a test that `either` comes from the no-age call). either always equals child-or-adult in this search (_passes is any over ages), so the test checks either comes from the no-age call.
    6.3 [x] 3.3 Collected and marked checks carry no `in_logic` and never count as in logic.
    6.4 [x] 3.4 Each area reports `in_logic` counts for `child`, `adult` and `either` (the last from the checks' `either`).
    6.5 [x] 3.5 The search reruns only when the inventory changes (test counts `Search` constructions across polls with the same and a changed save).
    6.6 [x] 3.6 An open check's entry has no `item`/`item_label` unless spoiler mode is on (existing behaviour, test extended to logic-enabled state).
    6.7 [x] P6.a The state gains a top-level `logic` object: `available`, `reason`, `unknown_items`, `age` (task 10); field names documented in the module docstring.

7. [x] Manual marks storage (new module `src/clawshot/tracker/marks.py`)
    7.1 [x] 4.6 Marks are JSON in the preferences folder, the parent of `app.preferences.user_preferences_path()` (`%APPDATA%\Clawshot`, macOS/XDG equivalents; not the deletable `%LOCALAPPDATA%\Clawshot\Cache`), keyed by seed identity (`output_sha256`, else SHA-256 of the spoiler file) and save slot path.
    7.2 [x] 4.7 Marks survive a reload of the store and are separate per seed and per slot (test: another slot of the same seed starts empty; another seed starts empty).
    7.3 [x] 4.10 An unreadable or missing marks file gives a warning and is treated as empty; the file is not overwritten until a mark changes (test checks the bad file's bytes are kept after a read). A missing file reads as no marks without a warning (a fresh install has none): proposed by Claude, raised in the PR.
    7.4 [x] P7.a Writes are atomic (write temp file, replace) and deterministic (sorted keys); tests redirect the folder to `tmp_path`.

8. [x] Mark rules in the state (`tracker/state.py`, `tracker/saves.py`)
    8.1 [x] 4.2 A marked check is reported as `marked: true`, distinct from `collected: true`, and counts as done in area counts and the open list.
    8.2 [x] 4.3 A mark does not add the check's item to the logic inventory (test: inventory equal with and without the mark).
    8.3 [x] 4.4 In spoiler-free mode a marked check's entry has no `item`/`item_label`.
    8.4 [x] 4.5 When a save reads a marked check as True or False, the save's state is used and the mark is removed from storage.

9. [x] Mark and clear endpoints (`ui/tracker.py`)
    9.1 [x] 4.1 `POST tracker-mark {check, marked}` toggles a check between unknown and marked; checks with a save-confirmed state are rejected.
    9.2 [x] 4.8 `POST tracker-clear-marks` removes all marks of the current seed and slot (confirmation happens in the UI; the endpoint requires `confirmed: true`).
    9.3 [x] 4.9 Both endpoints are POST behind the server's token/Host/Origin checks and reject unknown check ids, checks not currently unknown, and requests without a configured seed and slot (tests in `tests/test_tracker_http.py`).

10. [x] Age selection
    10.1 [x] 5.2 The state reports `logic.save_age`: `child` when `Sequence_IsChildhood` is true, `adult` when false, `null` when unreadable (test with synthetic saves for all three).
    10.2 [x] 5.1 The Tracker tab has an age control: Either (default), Follow save, Child, Adult.
    10.3 [x] 5.2 Follow save with an unreadable Bool uses Either and shows a one-line note.
    10.4 [x] 5.3 A chosen non-default option persists in localStorage (each access in try/catch) and the page works with storage unavailable.
    10.5 [x] 5.4 In-logic styling, area counts and the filter follow the selected age.

11. [x] Tracker tab display (`ui/static/tracker.html|js|css`)
    11.1 [x] 6.1 Each open check is styled in-logic or out-of-logic; collected and marked checks keep their own styles.
    11.2 [x] 6.2 Each area heading shows "N in logic" for the selected age next to its existing counts.
    11.3 [x] 6.3 "Show only in-logic" hides open out-of-logic, collected and marked checks; areas with nothing visible collapse.
    11.4 [x] 6.4 With logic unavailable, the age control and filter are disabled and `logic.reason` is shown; the rest of the tab works as today.
    11.5 [x] 6.5 A non-empty `logic.unknown_items` shows one line saying in-logic may be conservative, naming the cells.
    11.6 [x] 4.1/4.2/4.8 Unknown checks have a mark toggle; marked checks look distinct from collected; a "Clear manual marks" button asks for confirmation before calling the endpoint.
    11.7 [x] P11.a Any new static file is added to `ui/server.py` STATIC and `ui/release.py`'s file list; `tests/test_ui_release.py` passes. No new static file was needed (test_no_new_static_files); test_ui_release passes.

12. [x] OBS view unchanged
    12.1 [x] 6.6 The `tracker-obs` payload strips `logic`, `marked` and `in_logic` data, and a test shows its payload equals the pre-feature payload for the same seed and save. Test compares the OBS payload with logic on and a mark set against logic off and no marks (equal), and pins the area keys to the pre-feature set.

13. [x] Docs
    13.1 [x] 7.1 `docs/tracker.md` gains an "In logic" section covering D1–D18 as the player sees them, including a note that Follow save reads `Sequence_IsChildhood`, which Longshot's debug age switch does not change.
    13.2 [x] 7.1 The "Nothing is created or changed by tracking" statement is reworded to "nothing in your game, seed or save folders", naming the marks file's location (Q1 approved by the maintainer).

14. [x] Tests and checks
    14.1 [x] 7.2 Synthetic-fixture tests cover the version gate and spoiler-location gate (1.3), the shared builder's equivalence (1.5), inventory mapping including tiers, acquired-once, found keys, unknown fields, the closed return gate and Ruto's Letter in a bottle (2.x), per-age and either-age in-logic on a small custom world (3.x), marks lifecycle and isolation per seed/slot (4.x), Follow save from `Sequence_IsChildhood` (5.2) and the unchanged OBS payload (6.6). No game data, saves or logs in fixtures or the PR (AGENTS.md rule 1).
    14.2 [x] 7.3 `uv run ruff format --check`, `uv run ruff check` and `uv run --with pytest-xdist pytest -n auto` pass; `OOT_ROMFS=<romfs> uv run pytest -m dump` passes for task 2 (it touches the seed pipeline). Format, lint and the full suite pass (3902 passed, 505 skipped, 2026-11-20). The dump run is not done: no OOT_ROMFS on the agent's machine; listed in pr.md for a maintainer.
    14.3 [x] P14.a Determinism: two builds of the state from the same seed, save and marks give equal JSON.

15. [ ] In-game acceptance (maintainer run)
    15.1 [x] 7.4 The PR gives the maintainer exact steps: with a Clawshot Play seed, save after collecting a few items, confirm the in-logic list matches what is reachable in game for that age; buy a shop item, mark its check, restart Clawshot, confirm the mark persists and the shop item stays hidden in spoiler-free mode. The result is recorded by the maintainer, not claimed by the agent. Steps are in the PR #36 description; the result is for the maintainer to record.
    15.2 [x] P15.a Decisions made during implementation are listed in the PR with who proposed them, including D15 (proposed by Claude, chosen by BBender, 2026-11-20), the maintainer's review changes (D9 folder, D11 default Either, D14 location check, D16–D18, Q1, Q2) and P5.b (proposed by Claude). Listed in the PR #36 description.
    15.3 [ ] P15.b Commits carry an `Assisted-by: <model>` trailer and add named paths only; the PR is MIT-compatible and contains no game files, saves or logs.
16. [ ] Vanilla rows (D19, spec section 8; added 2026-11-21, proposed by Claude, chosen by BBender; Q3/Q4 await the maintainer, so build to the proposed defaults behind one constant each and change only those if the answer differs)
    16.1 [ ] P16.a Record the maintainer's answers to Q3 (scope) and Q4 (toggle default) in the spec before merging; until then the PR lists them as open. BBender answered Q3 (unique), Q4 (on) and Q5 (keep `?` rows) on 2026-11-21, as built; the maintainer's approval is still open.
    16.2 [x] 8.1 Also skips `Shop`, `Event` and `Drop` locations (`VANILLA_SKIPPED_TYPES`, proposed by Claude). `tracker/logic.py` gains `vanilla_rows(seed, world) -> tuple[...]`: world locations not in the spoiler's placements, vanilla item of class progression, not `n64_only`, in the Q3 scope (proposed: the vanilla item is given by no other world location); world order; computed once per loaded seed beside the cached world (1.2). None when logic is unavailable.
    16.3 [x] 8.2 Each row has `id` (location name), `label`/`where` from the location catalog when present else the OoT Randomizer name and "", `area` (census area via `location_index`, else the region's area), `item`/`item_label` (vanilla item, display name as `seeds.py` does), `vanilla: true`. Item fields are present in spoiler-free mode.
    16.4 [x] 8.3 Collected from the logic inventory (task 5): `true` when the inventory counts the vanilla item, `false` when every cell that maps to it was read and says not held, `null` when any such cell is unknown, the item is not mapped in `tracker_logic.toml`, or the item also appears in the seed's placements. Reuse the TOML mapping (inverted: logic name to cells); no new per-item Python branches (AGENTS.md rule 6 spirit). Fixed tiers of a progressive item (e.g. Golden Scale) count once the chain reaches the tier (proposed by Claude). On BBender's seed 2445192976 four rows stay `null` for want of a cell (Treasure Chest Game heart, Blue Potion, Goron Bracelet, Magic Bean): Q5 and Q6.
    16.5 [x] 8.3 Marks: vanilla rows with `collected: null` go through the existing mark rules (tasks 7–9); `tracker-mark` accepts their ids; a save-confirmed state drops a mark (4.5).
    16.6 [x] 8.4 `SeedLogic.annotate` gives open vanilla rows `in_logic` from the same `Search` as the shuffled checks (no extra items, no second search).
    16.7 [x] 8.5 Each area gains `vanilla: {total, done, in_logic: {child, adult, either}}`; existing area fields unchanged (test compares them with vanilla rows on and off). Built as a top-level `state["vanilla_areas"]` list (same shape as `areas`, plus `in_logic`) instead of a key inside each area, so areas that hold only vanilla rows need no new `areas` entry and the OBS payload stays equal by dropping one key; the tab merges them by area name (Claude).
    16.8 [x] 8.6 `ui/static/tracker.js|css`: vanilla rows inside their area with a "vanilla" tag; "Show vanilla pick-ups" toggle (default per Q4, localStorage in try/catch as 10.4); "Show only in-logic" applies to them.
    16.9 [x] 8.7 OBS payload strips vanilla rows and counts; the task-12 test still shows it equal to the pre-feature payload.
    16.10 [x] 8.8 Synthetic tests (`tests/test_tracker_vanilla_rows.py`): custom world with a non-shuffled gate item (letter-like) and a gated check: row open and in logic, gated check out; save holding the item: row collected, gated check in logic. A vanilla item also in the seed's placements gives `collected: null`. Shuffled-check state equal with and without vanilla rows. Deterministic JSON (P14.a).
    16.11 [x] 8.9 `docs/tracker.md` "In logic" section: vanilla rows, the toggle, and the Ruto's Letter / Jabu-Jabu example.
    16.12 [x] 7.3 Format, lint and the full suite pass; the PR description lists D19, Q3, Q4 and a maintainer in-game step: on a Chest-only seed as child with Silver Scale reachable, the tracker shows "LH Underwater Item" open and in logic before the letter is taken and collected after, and Jabu-Jabu's checks turn in logic once the letter is held. Full suite 2026-11-21: 4155 passed, 2 failed, 799 skipped; the two failures (`test_unavailable_logic_leaves_every_existing_field_unchanged`, an empty `vanilla_areas` key added while logic was unavailable) were fixed by leaving the key out, and the tracker tests then passed (128). Format and lint pass.
