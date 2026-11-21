# Item tracker

The **Tracker** tab reads the selected seed and a saved game. Dungeon keys come first: **Held**
is the number available to spend now; **Found / total** is the acquired count, including spent
keys, out of that seed's dungeon total. Keys found outside their dungeon still appear under the
correct dungeon. Boss key, map and compass are separate saved flags.

The **Gerudo Fortress** row includes the four jail keys, including keys found in remote chests
with the separate experimental jail-key option. The four guard-floor checks and the Well/Shadow
floor-key checks read their native saved collection Bools, not actor-Hash records. Defeating a
guard or finding a jail key elsewhere does not by itself complete its floor-reward check.
These new source adapters and their played tracker updates still await in-game acceptance.

## Start tracking

1. Generate a seed, or **View seed** under Generate → My seeds.
2. Open **Tracker** and press **Use selected seed**. Alternatively Browse to, or paste, the
   seed's output folder and press **Track seed**. Both `output/seed/spoiler.json` and a raw
   generator folder containing `spoiler.json` are accepted.
3. Leave **Save folder** empty for this seed's own Play saves (`output/user`). Tracking creates
   or changes nothing in your game, seed or save folders; the only file it writes holds your manual
   marks (see **In logic**). Before a new game is saved, the tracker waits for a save.
4. The newest `slot_NN/progress.sav` by modification time is selected automatically. Use
   **Slot** to pin another slot; choose **Newest saved slot** to follow the newest again.
5. Save in the game. The page polls once a second and updates without reloading. This is
   saved progress, not live process memory: unsaved pickups will not appear yet.

Items show current holdings and tiers, songs, stones, medallions, hearts/pieces and Gold Skulltula
tokens. Bottles show the number owned and each slot's current contents, not every content ever
acquired. An acquired-once flag is not proof a consumed trade item or broken shield is still held.
Plain boots have no saved pouch row; the tracker shows Iron/Hover Boots, not an invented normal-boot
ownership flag. Hearts are the meter's capacity; pieces are the raw saved stock, not a claimed
lifetime total. `?` means the field or collection contract is unknown, not zero. Checks are grouped
by area; repeatable purchases and unaudited event gates cannot be treated as permanently collected.
A partial/unreadable save keeps the previous good state with a warning until it can be read again.

With Gold Skulltula tokens shuffled, each Skulltula is one check, however many age copies it has. It
counts as collected once its reward has been picked up, whatever that reward is: the game saves two
records for that Skulltula, and the tracker needs both. Killing it without collecting the drop does not
count. The **Gold Skulltulas** number is the game's own token count, so it rises for a token found in a
chest or at a Skulltula and stays the same for any other reward at a Skulltula. Beside it, **Skulltula checks**
counts collected Skulltulas out of the seed's total (in brackets, how many are unknown), in the tab and in
every OBS view that shows the quest group, labels on or off; seeds without Token shuffle don't show it.
A Skulltula shows `?` when only one of its two records is set, or when the save is not the save layout
those records were checked on.

## In logic

**Checks by area** lists each area's checks by name; their rewards stay hidden unless spoiler mode is
on. Every open check (not collected, or `?` and not marked done) is shown **in logic** (highlighted)
when the seed's own logic says you can reach it with what your save holds, or **out of logic** (dimmed)
otherwise. Each area heading adds "N in logic". **Show only in-logic** hides the rest, and areas with
nothing left to show fold away.

- **What counts as held.** Only what your save holds: items, upgrades, songs, stones and medallions,
  hearts, Gold Skulltula tokens, bottles, magic and dungeon items, plus the seed's starting items.
  The spoiler's placements are never used, so in-logic gives nothing away.
- **Used-up items.** A trade item, Ruto's Letter or a shield counts once the save shows you got it,
  even after you traded it on, delivered it, or lost the shield. Bombchus count once found, even when
  used. Other items count only while you hold them.
- **Small keys** count every key you found in that dungeon, spent ones included. Boss keys, maps and
  compasses count once you have them.
- **Bottles.** Each bottle you own counts as a bottle, except one holding Ruto's Letter, which counts as
  the letter only: as in the seed's logic, the letter is not also an empty bottle.
- **Hearts** count whole hearts; loose Pieces of Heart are not added.
- **Story steps.** Meeting Zelda (Impa's send-off) and the owl's arrival in Hyrule Field are read from
  the save. Other story steps are worked out from the logic itself.
- **Unknown fields.** Anything the save cannot show counts as not held, and the tab says so in one line
  naming it: in-logic may then be more cautious than the game.

**In logic for** chooses the age: **Either age** (the default: a check counts when either age can reach
it, as the seed's logic does), **Follow save**, **Child** or **Adult**. Follow save reads the save's
`Sequence_IsChildhood` flag, which normal play keeps right but Longshot's debug age switch does not
change. When the save does not say, Follow save shows either age and says so. Your choice is remembered
in this browser. Styling, area counts and the filter all follow it.

In-logic needs a seed made by this same Clawshot version, whose settings rebuild into the seed's logic
and whose every location is in this version's world. Otherwise the age control and filter are greyed
out with the reason, and the rest of the tracker works as before. A save, not live play, is read: pick
something up and save before it counts.

**Marking checks done.** Some checks the save cannot show (`?`): shop items, a few gifts, some floor
pickups. Use **Mark done** on such a check once you have it, so it leaves the open list; **Unmark**
undoes it. A marked check shows as marked by you, not as collected, never adds its item to what you
hold, and keeps its reward hidden in spoiler-free mode. If a later save does show that check, the save
wins and the mark is removed. Marks are kept per seed and per save folder (the game writes each save to
its next slot, so they follow you from slot to slot), survive a restart of Clawshot, and **Clear manual
marks** removes this seed and save folder's marks after asking. They live in
`tracker-marks.json` in Clawshot's preferences folder: `%APPDATA%/Clawshot` on Windows,
`~/Library/Application Support/Clawshot` on macOS, `$XDG_CONFIG_HOME/clawshot` (default
`~/.config/clawshot`) on Linux. If that file cannot be read, the tracker warns, shows no marks and
leaves the file alone until you change a mark.

**Vanilla pick-ups.** Some places your seed does not shuffle still hold an item the logic needs.
Ruto's Letter at the bottom of Lake Hylia is one: until you hold it, Jabu-Jabu's Belly stays out of
logic. So the tracker also lists these places in their area, tagged **vanilla**, with their usual item
shown even in spoiler-free mode (your settings decide it, not the seed). They get the same in-logic
styling, and the area heading counts them separately ("vanilla 0 / 1 · 1 in logic"), leaving the
seed's own counts unchanged. One counts as collected once the save shows you hold its item (or ever
had it, for used-up items as above). If the save cannot tell, or a shuffled check could also give that
item, it shows `?` and you can mark it done. Only items that come from that one place are listed: every
song, the ocarinas, the trade items, Ruto's and Zelda's Letters, the Weird Egg, the Gerudo card, Great
Fairy gifts, masks, and stones and medallions when they are not shuffled. Gold Skulltulas, silver rupees,
Pieces of Heart and other repeated items are not. **Show vanilla pick-ups** turns them off; the choice
is remembered in this browser. They need in-logic, so they are hidden when in-logic is unavailable.

The OBS view shows none of this: no in-logic data, no vanilla pick-ups and no marks.

## Hookshot Play

Use Clawshot's **Play**, or the pack's Play launcher. These isolate saves under the seed's
`user` folder. Leave **Save folder** empty. Installing a mod manually in Hookshot instead uses
Hookshot's normal user folder: choose that folder explicitly and back up saves before New Game.
Do not choose the game dump or a generated `romfs` folder as a save folder.

## Longshot and emulators

Clawshot **Play** uses the same per-seed `user` layout for a supported Longshot installation.
Leave **Save folder** empty when using it. If you manually copied the seed to Longshot's mods,
choose the Longshot **user** folder where that run saves instead. Clawshot only reads it.

For an emulator, choose this game's save folder (containing `slot_NN`), or its enclosing
user/save folder. Nested user-ID/title-ID folders are searched. Multiple profiles can contain
identically named slots: use the full listed slot path to distinguish them. Back up your normal
emulator saves before starting a randomizer; the tracker does not isolate or repair them.

A save does not reliably identify its seed. The tracker reports any mismatch it can establish,
but **cannot certify that a vanilla/older save belongs to this seed**. Confirm the game is loading
only the intended seed and select its matching save folder; a warning is not permission to ignore
this. Never use similar inventory or check counts as seed-identity proof.

## Spoilers

Default mode does not return an unvisited location's reward. **Show locations (spoilers)**
requires confirmation and then reveals the seed's location list and rewards. Turn it off to
return to spoiler-free tracking. The spoiler log, play note and screenshots of revealed locations
must not be shared with players avoiding spoilers. The OBS view is always location-spoiler-free,
even while the app tab's spoiler mode is on.

## OBS Browser Source

1. Configure the Tracker tab and keep Clawshot running.
2. Choose **OBS columns** (1–8), **OBS item labels**, the **OBS items/quest/dungeons** checkboxes,
   and **Transparent OBS background**, then **Copy URL**.
   These OBS-only controls do not change the in-app tracker layout.
3. In OBS add a **Browser Source** and use that URL. Groups stack vertically in a narrow block.
   Four columns is the default: about 340 pixels wide with labels, suitable for a side overlay.
   Start at 350×3000 with labels, or 290×2400 without, then crop/scale or increase columns to fit
   your scene. Text fallbacks can increase height. Check save/seed warnings in the app tab.
   The surface has no controls and follows the same seed/save/slot as the app tracker.
4. Disable OBS's shutdown-when-not-visible option if you want continuous refresh while hidden.

The URL includes a private, random per-run token. Do not publish it or paste it into a public
chat. Closing/restarting Clawshot invalidates it; copy the new URL into OBS. Nothing is exposed
on the network: the server binds only `127.0.0.1` on a random port, keeps its Host/Origin checks,
and makes no external requests. OBS must run on the same computer.

The URL fragment defaults to `columns=4&labels=1&icons=1&transparent=0&sections=items,quest,dungeons`.
`columns` accepts whole numbers 1–8; missing/invalid values use four. Copy the updated URL into
OBS after changing controls. With labels off, successfully loaded icons sit in close cells:
top-left badges show upgrade tiers and bottom-right badges show counts (bottles, ammo, rupees
or magic capacity). Greyed-out items are not held; dashed cells and `?` mean unknown.
Heart, piece, token and Skulltula check counts stay visible. Names/details remain available as tooltips and
accessible labels. Without a usable item icon, text stays visible even with labels off.

Compact quest cells use flat CSS, not game art: songs are `ZL`, `Ep`, `Sa`, `Su`, `SoT`, `SoS`,
`Min`, `Bol`, `Ser`, `Req`, `Noc`, `Pre`, `Scr`; stones are `Kok`, `Gor`, `Zor`.
Medallions are circles: forest green, fire red, water blue, shadow purple, spirit orange,
light yellow. Missing holdings use the same grey-out. Full names remain in tooltips and accessible
labels. Single-tier entries never display a tier number, in either the tab or OBS.

With labels off, OBS hides the heading's extra text, warning paragraphs and **Checks by area**.
Normal following needs no status line; waiting/unavailable states show one short line. The app tab
keeps its status, warnings and area checks. Use that tab to inspect compatibility/read warnings.

Each dungeon keeps its name and a compact row of small key, boss key, map and compass icons.
The small-key badge is **held**, available to spend; the number below is **found / seed total**,
including spent keys. Other icons are greyed out when missing. Hover for the full description;
unknown flags show `?`. With icons disabled or unavailable, each indicator uses its name and
saved value instead. Dungeon names and collection counts stay visible with item labels off.

`sections` accepts comma-separated `items`, `quest` and `dungeons`. Quest includes hearts/tokens/Skulltula checks,
songs, stones and medallions; Items includes inventory and equipment. Missing, empty or any unknown
section value shows all. The original group order is preserved, not the order typed in the URL.
Clearing the last section checkbox restores all three. Partial views omit **Checks by area**;
the app tab always keeps every group.

### Two browser sources for a 1080p stream

1. Choose four columns, turn **OBS item labels** off, and leave **Local item icons** on.
2. Check only **OBS dungeons**, **Copy URL**, and use it for the first Browser Source
   (`sections=dungeons`).
3. Check only **OBS items** and **OBS quest**, copy that URL, and use it for the second source
   (`sections=items,quest`). Place the sources side by side; both follow the same seed/save.

Start each source at **290×1080**. Increase columns if text fallbacks make a part taller.
Changing checkboxes updates the copied URL, not URLs already configured in OBS; paste each new URL
into its corresponding source.


## Local icons and fallback

No game art or fonts are included. Icons are decoded at runtime from **your own** checked Game
dump (`UI/Tex/Icon/*.bntx.zs`), including `.nup` and `.nx` inputs and a separately chosen update
(its copy of an icon wins), using the optional UI texture decoder.
The optional `ui` extra includes [texture2ddecoder 1.0.6](https://pypi.org/project/texture2ddecoder/1.0.6/)
([MIT licence](https://github.com/K0lb3/texture2ddecoder/blob/master/LICENSE)); compatible wheels exist
for Windows, Linux and macOS. Use `uv run --extra ui python -m clawshot.ui` from source.
Windows's starter installs the extra; the current Linux/macOS starter omits it and uses text fallback
unless you install the extra yourself. Dependency installation may need internet; the running
interface and icon extraction make no network requests. Linux/macOS icon execution is not certified here.

Decoded PNGs are private game-derived data, never shipped in this repository or a seed pack.
Cache folders: Windows `%LOCALAPPDATA%/Clawshot/Cache/icons`; macOS
`~/Library/Caches/Clawshot/icons`; Linux `$XDG_CACHE_HOME/clawshot/icons` (default `~/.cache/clawshot/icons`).
Do not share them. Filenames include the source icon's hash; changing the dump or its update invalidates that icon.
Small keys, boss keys, maps and compasses use the game's `Item_Dungeon_*` icon files through
the same decoder/cache. Songs, stones and medallions have no file in `UI/Tex/Icon`: labelled views
use text, and compact OBS uses the CSS quest chips described above.
If a dump, decoder or texture is unavailable, the same view still works; uncheck **Local item icons**
to force text/CSS.
All fonts are installed system fonts.

## Safe headless operation

`uv run python -m clawshot.ui --no-open` prints a token URL without opening any window or dialog.
Paste paths to track saves; Browse/Open/Play remain disabled. The standalone OBS view is also
available in this mode. The tracker never starts a game, writes a save, or changes seed contents;
it writes only its manual-marks file in the preferences folder.

The automated evidence uses synthetic saves, read-only copies of real saves and headless browser
captures. Those checks do not prove in-game pickup/update behavior; the maintainers' staged
Longshot acceptance checklist is in `plans/rounds/r14-tracker.md`.
