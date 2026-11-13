"use strict";

// One renderer for the app tab and the control-free OBS surface. All labels are text nodes.
(() => {
  const root = document.getElementById("tracker-root");
  if (!root) return;
  const standalone = document.body.dataset.tracker === "obs";
  const prefix = location.pathname.slice(0, location.pathname.lastIndexOf("/") + 1);
  const token = prefix.split("/")[2];
  const options = new URLSearchParams(location.hash.slice(1));
  if (standalone && options.get("transparent") === "1") document.body.classList.add("tracker-transparent");
  let icons = options.get("icons") !== "0";
  let lastRevision = "", pending = false, initialized = false;
  const node = (tag, cls = "", text) => {
    const el = document.createElement(tag);
    el.className = cls;
    if (text !== undefined) el.textContent = text;
    return el;
  };
  async function request(route, body) {
    const response = await fetch(prefix + "api/" + route, {
      method: body === undefined ? "GET" : "POST", credentials: "omit", cache: "no-store",
      headers: {"X-Clawshot-Token": token, ...(body === undefined ? {} : {"Content-Type": "application/json"})},
      ...(body === undefined ? {} : {body: JSON.stringify(body)}),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Tracker request failed");
    return data;
  }
  const heading = node("div", "heading");
  heading.append(node("h1", "", "Tracker"), node("p", "", "Saved inventory · keys by dungeon · no location spoilers"));
  const status = node("p", "tracker-status");
  status.setAttribute("role", "status");
  const warnings = node("div", "tracker-warnings");
  const content = node("div", "tracker-content");
  root.append(heading);
  let controls, seedInput, saveInput, slotSelect, reveal, obsUrl, iconToggle, transparent;
  if (!standalone) {
    controls = node("form", "tracker-controls");
    function pathRow(label, placeholder, kind) {
      const row = node("div", "tracker-path");
      const input = node("input");
      input.placeholder = placeholder;
      input.autocomplete = "off";
      input.spellcheck = false;
      input.id = "tracker-" + kind;
      const caption = node("label", "", label);
      caption.htmlFor = input.id;
      const browse = node("button", "", "Browse…");
      browse.type = "button";
      browse.disabled = true;
      browse.dataset.trackerBrowse = kind;
      browse.addEventListener("click", async () => {
        try {
          const data = await request("tracker-browse", {kind});
          if (data.path) input.value = data.path;
        } catch (error) { status.textContent = error.message; }
      });
      row.append(caption, input, browse);
      controls.append(row);
      return input;
    }
    seedInput = pathRow("Seed output", "Use selected seed, or paste its output folder", "seed");
    saveInput = pathRow("Save folder", "Empty = this seed’s own Play saves", "save");
    const actions = node("div", "tracker-actions");
    const apply = node("button", "primary", "Track seed");
    apply.type = "submit";
    const useSelected = node("button", "", "Use selected seed");
    useSelected.type = "button";
    useSelected.addEventListener("click", async () => {
      seedInput.value = "";
      saveInput.value = "";
      slotSelect.value = "";
      reveal.checked = false;
      await configure();
    });
    slotSelect = node("select");
    slotSelect.id = "tracker-slot";
    slotSelect.append(new Option("Newest saved slot", ""));
    slotSelect.addEventListener("change", configure);
    const slotLabel = node("label", "", "Slot ");
    slotLabel.append(slotSelect);
    actions.append(apply, useSelected, slotLabel);
    controls.append(actions);
    const flags = node("div", "tracker-options");
    function checkbox(text, checked) {
      const label = node("label");
      const input = node("input");
      input.type = "checkbox";
      input.checked = checked;
      label.append(input, document.createTextNode(" " + text));
      flags.append(label);
      return input;
    }
    reveal = checkbox("Show locations (spoilers)", false);
    reveal.addEventListener("change", async () => {
      if (reveal.checked && !window.confirm("Reveal every seed location and its item? This spoils unvisited checks. OBS remains spoiler-free.")) {
        reveal.checked = false;
        return;
      }
      await configure();
    });
    iconToggle = checkbox("Local item icons", true);
    iconToggle.addEventListener("change", () => { icons = iconToggle.checked; lastRevision = ""; updateObs(); refresh(); });
    transparent = checkbox("Transparent OBS background", false);
    transparent.addEventListener("change", updateObs);
    controls.append(flags);
    const obs = node("div", "tracker-obs-link");
    const obsLabel = node("label", "", "OBS Browser Source URL (private; changes each app start)");
    obsUrl = node("input");
    obsUrl.id = "tracker-obs-url";
    obsUrl.readOnly = true;
    obsLabel.htmlFor = obsUrl.id;
    const copy = node("button", "", "Copy URL");
    copy.type = "button";
    copy.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(obsUrl.value); status.textContent = "OBS URL copied"; }
      catch { obsUrl.focus(); obsUrl.select(); status.textContent = "Press Ctrl+C or Command+C to copy"; }
    });
    obs.append(obsLabel, obsUrl, copy);
    controls.append(obs);
    controls.addEventListener("submit", (event) => { event.preventDefault(); configure(); });
    root.append(controls);
    updateObs();
  }
  root.append(status, warnings, content);
  function updateObs() {
    const fragment = new URLSearchParams({transparent: transparent.checked ? "1" : "0", icons: icons ? "1" : "0"});
    obsUrl.value = new URL(prefix + "tracker.html#" + fragment, location.origin).href;
  }
  async function configure() {
    if (pending) return;
    pending = true;
    try {
      const data = await request("tracker-configure", {
        seed: seedInput.value.trim() || null,
        save_folder: saveInput.value.trim() || null,
        slot: slotSelect.value || null,
        show_locations: reveal.checked,
        confirmed: reveal.checked,
      });
      initialized = true;
      lastRevision = "";
      render(data);
    } catch (error) { status.textContent = error.message; }
    finally { pending = false; }
  }
  const show = (value) => value === null || value === undefined ? "?" : String(value);
  const yes = (value) => value === null || value === undefined ? "?" : value ? "Yes" : "—";
  function section(title) {
    const section = node("section", "tracker-group");
    section.append(node("h2", "section-title", title));
    content.append(section);
    return section;
  }
  function cells(title, entries) {
    if (!entries?.length) return;
    const group = section(title), grid = node("div", "tracker-cells");
    for (const cell of entries) {
      const held = cell.held;
      const el = node("div", "tracker-cell" + (held === false ? " tracker-missing" : "") + (held == null ? " tracker-unknown" : ""));
      const label = cell.label || cell.name || cell.id;
      if (icons && cell.icon) {
        const image = node("img", "tracker-icon");
        image.alt = "";
        image.width = 40;
        image.height = 40;
        image.loading = "lazy";
        image.src = prefix + "tracker-icons/" + encodeURIComponent(cell.icon) + ".png";
        image.addEventListener("error", () => image.remove(), {once: true});
        el.append(image);
      }
      el.append(node("span", "tracker-cell-label", label));
      let detail = held == null ? "Unknown" : held ? "Held" : "Not held";
      if (cell.basis === "slots") detail = cell.count == null ? "Count unknown" : cell.count + " bottle" + (cell.count === 1 ? "" : "s");
      else {
        if (cell.tier != null && cell.tier > 0) detail = "Tier " + cell.tier;
        if (cell.count != null) detail += " · " + cell.count;
      }
      el.append(node("small", "", detail));
      if (cell.contents?.length) el.append(node("small", "", cell.contents.map((bottle) => bottle.content || "?").join(", ")));
      grid.append(el);
    }
    group.append(grid);
  }
  function render(data) {
    const idle = data.status === "idle" || data.status === "unconfigured";
    initialized = initialized || !idle;
    const state = data.state;
    const labels = {ok: "Following saved progress", ready: "Following saved progress", waiting: "Waiting for a saved game", stale: "Waiting for a complete save", no_save_folder: "Choose a save folder", error: "Unable to read this seed"};
    status.textContent = idle ? "Choose a seed to begin. Reads saves only; never changes them." :
      (labels[data.status] || data.status) +
      (data.selected_slot ? " · " + data.selected_slot : "") + (data.save_folder && !standalone ? " · " + data.save_folder : "");
    warnings.replaceChildren();
    for (const warning of [...new Set([...(data.warnings || []), ...(state?.warnings || [])])]) warnings.append(node("p", "", warning));
    if (!standalone) {
      const selected = slotSelect.value;
      const signature = JSON.stringify(data.slots || []);
      if (slotSelect.dataset.slots !== signature) {
        slotSelect.replaceChildren(new Option("Newest saved slot", ""));
        for (const slot of data.slots || []) slotSelect.append(new Option(slot.label || slot.id || slot.name, slot.id || slot.name));
        slotSelect.value = selected;
        slotSelect.dataset.slots = signature;
      }
    }
    if (!state) { content.replaceChildren(); return; }
    const revision = JSON.stringify([data.revision, state, icons]);
    if (revision === lastRevision) return;
    lastRevision = revision;
    content.replaceChildren();
    const seed = state.seed || {};
    heading.querySelector("p").textContent = "Seed " + show(seed.seed ?? seed.number) + " · saved inventory · " + (standalone ? "spoiler-free" : reveal.checked ? "LOCATION SPOILERS ON" : "spoiler-free");
    const dungeonGroup = section("Dungeon keys");
    const table = node("table", "tracker-dungeons");
    const head = node("thead"), row = node("tr");
    for (const title of ["Dungeon", "Held", "Found / total", "Boss", "Map", "Compass"]) row.append(node("th", "", title));
    head.append(row); table.append(head);
    const body = node("tbody");
    for (const dungeon of state.dungeons || []) {
      const tr = node("tr"), keys = dungeon.small_keys || {};
      for (const value of [dungeon.name, show(keys.held), show(keys.found) + " / " + show(keys.total), yes(dungeon.boss_key), yes(dungeon.map), yes(dungeon.compass)]) tr.append(node("td", "", value));
      body.append(tr);
    }
    table.append(body); dungeonGroup.append(table);
    const health = state.hearts || {};
    const counts = section("Collection");
    counts.append(node("p", "tracker-counts", "Hearts " + show(health.containers ?? health.capacity) + " · Pieces " + show(health.pieces) + " · Gold Skulltulas " + show(state.tokens)));
    cells("Items & equipment", state.items);
    cells("Songs", state.songs);
    cells("Stones & medallions", state.rewards);
    const areas = section("Checks by area");
    areas.append(node("p", "tracker-explanation", "Saved collection only; ? means the collection contract is not established. Repeatable shops are not permanent checks."));
    const areaGrid = node("div", "tracker-areas");
    for (const area of state.areas || []) {
      const item = node("div", "tracker-area");
      item.append(node("strong", "", area.name), node("span", "", show(area.collected) + " / " + show(area.total) + (area.unknown ? " · " + area.unknown + " unknown" : "")));
      if (!standalone && reveal.checked) for (const check of area.checks || []) {
        item.append(node("p", "tracker-check", (check.collected == null ? "? " : check.collected ? "✓ " : "— ") + (check.label || check.name || check.id) + (check.item ? ": " + (check.item_label || check.item) : "")));
      }
      areaGrid.append(item);
    }
    areas.append(areaGrid);
    document.documentElement.dataset.trackerReady = "true";
  }
  async function refresh() {
    if (pending || (!standalone && document.getElementById("tracker")?.hidden)) return;
    pending = true;
    try {
      const data = await request(standalone ? "tracker-obs" : "tracker");
      render(data);
      if (!standalone && !initialized && ["idle", "unconfigured"].includes(data.status)) {
        // Seed choice is explicit. Loading a tab never opens or reveals the selected seed's spoiler.
        status.textContent = "Use selected seed, or choose a seed output and Track seed.";
      }
    } catch (error) { status.textContent = error.message; }
    finally { pending = false; }
  }
  if (!standalone) request("schema").then((data) => {
    for (const button of root.querySelectorAll("[data-tracker-browse]")) {
      button.disabled = !data.dialogs_available;
      if (button.disabled) button.title = "Disabled in --no-open; paste a path instead";
    }
  }).catch((error) => { status.textContent = error.message; });
  refresh();
  const timer = setInterval(refresh, 1000);
  window.addEventListener("pagehide", () => clearInterval(timer), {once: true});
})();
