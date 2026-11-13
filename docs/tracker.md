# Item tracker

The **Tracker** tab reads the selected seed and a saved game. Dungeon keys come first: **Held**
is the number available to spend now; **Found / total** is the acquired count, including spent
keys, out of that seed's dungeon total. Keys found outside their dungeon still appear under the
correct dungeon. Boss key, map and compass are separate saved flags.

## Start tracking

1. Generate a seed, or **View seed** under Generate → My seeds.
2. Open **Tracker** and press **Use selected seed**. Alternatively Browse to, or paste, the
   seed's output folder and press **Track seed**. Both `output/seed/spoiler.json` and a raw
   generator folder containing `spoiler.json` are accepted.
3. Leave **Save folder** empty for this seed's own Play saves (`output/user`). Nothing is
   created or changed by tracking. Before a new game is saved, the tracker waits for a save.
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
2. Select **Transparent OBS background** if desired, then **Copy URL**.
3. In OBS add a **Browser Source**, use that URL, and start with 1000×900. Resize/crop as needed.
   The compact surface has no controls and follows the same seed/save/slot as the app tracker.
4. Disable OBS's shutdown-when-not-visible option if you want continuous refresh while hidden.

The URL includes a private, random per-run token. Do not publish it or paste it into a public
chat. Closing/restarting Clawshot invalidates it; copy the new URL into OBS. Nothing is exposed
on the network: the server binds only `127.0.0.1` on a random port, keeps its Host/Origin checks,
and makes no external requests. OBS must run on the same computer.

## Local icons and fallback

No game art or fonts are included. Icons are decoded at runtime from **your own** checked Game
dump (`UI/Tex/Icon/*.bntx.zs`), including `.nup` inputs, using the optional UI texture decoder.
The optional `ui` extra includes [texture2ddecoder 1.0.6](https://pypi.org/project/texture2ddecoder/1.0.6/)
([MIT licence](https://github.com/K0lb3/texture2ddecoder/blob/master/LICENSE)); compatible wheels exist
for Windows, Linux and macOS. Use `uv run --extra ui python -m clawshot.ui` from source.
Windows's starter installs the extra; the current Linux/macOS starter omits it and uses text fallback
unless you install the extra yourself. Dependency installation may need internet; the running
interface and icon extraction make no network requests. Linux/macOS icon execution is not certified here.

Decoded PNGs are private game-derived data, never shipped in this repository or a seed pack.
Cache folders: Windows `%LOCALAPPDATA%/Clawshot/Cache/icons`; macOS
`~/Library/Caches/Clawshot/icons`; Linux `$XDG_CACHE_HOME/clawshot/icons` (default `~/.cache/clawshot/icons`).
Do not share them. Filenames include the source icon's hash; changing the dump invalidates that icon.
Songs, stones and medallions have no file in `UI/Tex/Icon` and use text. If a dump, decoder or texture
is unavailable, the same view still works; uncheck **Local item icons** to force text/CSS.
All fonts are installed system fonts.

## Safe headless operation

`uv run python -m clawshot.ui --no-open` prints a token URL without opening any window or dialog.
Paste paths to track saves; Browse/Open/Play remain disabled. The standalone OBS view is also
available in this mode. The tracker never starts a game, writes a save, or changes seed contents.

The automated evidence uses synthetic saves, read-only copies of real saves and headless browser
captures. Those checks do not prove in-game pickup/update behavior; the maintainers' staged
Longshot acceptance checklist is in `plans/rounds/r14-tracker.md`.
