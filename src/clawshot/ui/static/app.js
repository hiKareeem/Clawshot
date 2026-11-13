"use strict";

const $ = (id) => document.getElementById(id);
const base = location.pathname;
const token = base.split("/")[2];
const screens = ["game", "settings", "generate"];
let metadata = [],
  values = {},
  inputs = {},
  initialStages = [];
let inactive = {};
let settingsString = "CS1",
  valid = false,
  syncing = false,
  revision = 0,
  timer,
  pollTimer;
let shareString = "";
let busy = false,
  resultShown = false,
  activeScreen = "game";
let outputRoot = "",
  outputCustom = false,
  dialogsAvailable = false;
let playAvailable = false,
  playUnavailableReason = "",
  gameCanPlay = false,
  gameLabel = "",
  playState = { running: false },
  resultOutput = "";
let openAvailable = false,
  libraryActions = [],
  lastLibraryOutput = "";
let emulatorFolder = "",
  edenFolder = "",
  copyAvailable = false;

function element(tag, className = "", text) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text !== undefined) el.textContent = text;
  return el;
}
function error(message) {
  $("alert").textContent = message;
  $("alert").hidden = !message;
}
async function api(route, body) {
  const response = await fetch(base + "api/" + route, {
    method: body === undefined ? "GET" : "POST",
    credentials: "omit",
    cache: "no-store",
    headers: {
      "X-Clawshot-Token": token,
      ...(body === undefined ? {} : { "Content-Type": "application/json" }),
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const data = await response.json();
  if (!response.ok)
    throw new Error(data.error || "Local server request failed");
  return data;
}

// All contextual setting labels and descriptions come from the application schema.
function bindHelp(el, info) {
  if (!info) return;
  el.dataset.helpTitle = info.label;
  el.dataset.help = info.help;
  el.dataset.helpNote = info.note || "";
}
function describe(el) {
  if (!el?.dataset.help) return;
  $("description-title").textContent = el.dataset.helpTitle;
  $("description-text").textContent = el.dataset.help;
  let note = el.dataset.helpNote;
  if (el.dataset.interface === "dump")
    note = $("dump-status").textContent + ". " + note;
  if (el.dataset.interface === "runtime")
    note = $("game-status").textContent + ". " + note;
  $("description-note").textContent = note;
  $("description-note").hidden = !note;
}
function show(name, focusTab = false) {
  if (!screens.includes(name)) name = "game";
  activeScreen = name;
  document
    .querySelectorAll(".screen")
    .forEach((el) => (el.hidden = el.id !== name));
  document.querySelectorAll("[data-screen]").forEach((el) => {
    const selected = el.dataset.screen === name;
    el.classList.toggle("selected", selected);
    if (selected) el.setAttribute("aria-current", "page");
    else el.removeAttribute("aria-current");
  });
  $("result").hidden = name !== "generate" || !resultShown;
  bindHelp($(name), inputs[name]);
  describe($(name));
  history.replaceState(null, "", "#" + name);
  document.querySelector(".main-panel").scrollTop = 0;
  if (focusTab) document.querySelector(`[data-screen=${name}]`).focus();
  updateHints();
}
function updateHints() {
  const hints = $("key-hints");
  hints.replaceChildren();
  const add = (keys, label) => {
    const span = element("span");
    for (const key of keys) span.append(element("kbd", "", key));
    span.append(document.createTextNode(label));
    hints.append(span);
  };
  if (document.querySelector("dialog[open]")) {
    add(["Esc"], "Back");
    return;
  }
  const focused = document.activeElement;
  const editing = focused?.matches("input:not([type=checkbox]), textarea");
  const usable =
    focused?.getClientRects().length &&
    !focused.disabled &&
    focused.getAttribute("aria-disabled") !== "true";
  if (focused?.matches("textarea")) add(["Tab"], "Next field");
  else add(["↑", "↓"], "Move");
  if (editing) {
    add(["Esc"], "Back");
    return;
  }
  if (usable && focused.matches("select, .shuffle-card, .switch-control"))
    add(["←", "→"], "Change");
  add(["Q", "E"], "Tabs");
  if (usable && focused.matches(".shuffle-card, .switch-control"))
    add(["Enter"], "Toggle");
  else if (usable && focused.matches("summary"))
    add(["Enter"], focused.parentElement.open ? "Close" : "Open");
  else if (usable && focused.matches("button"))
    add(["Enter"], focused.dataset.keyAction || "Open");
}
function navigable() {
  const areas = [$(activeScreen)];
  if (activeScreen === "generate" && resultShown) areas.push($("result"));
  return areas
    .flatMap((area) => [
      ...area.querySelectorAll(
        "input, select, textarea, button, summary, [data-nav]",
      ),
    ])
    .filter(
      (el) =>
        !el.hidden &&
        !el.disabled &&
        el.tabIndex >= 0 &&
        el.getClientRects().length,
    );
}
function changeValue(target, direction) {
  if (target.matches("select")) {
    const options = [...target.options].filter((option) => !option.disabled);
    const index = options.findIndex((option) => option.value === target.value);
    target.value =
      options[(index + direction + options.length) % options.length].value;
    target.dispatchEvent(new Event("change", { bubbles: true }));
    return true;
  }
  const id = target.dataset.control;
  if (id) {
    const input = $(id);
    if (input.disabled) return true;
    input.checked = direction === 0 ? !input.checked : direction > 0;
    input.dispatchEvent(new Event("change", { bubbles: true }));
    return true;
  }
  return false;
}
document.addEventListener("keydown", (event) => {
  if (
    event.ctrlKey ||
    event.altKey ||
    event.metaKey ||
    document.querySelector("dialog[open]")
  )
    return;
  const target = event.target;
  const editing = target.matches("input:not([type=checkbox]), textarea");
  if (event.key === "Escape" && editing) {
    event.preventDefault();
    target.blur();
    document.querySelector(`[data-screen=${activeScreen}]`).focus();
    return;
  }
  if (!editing && ["q", "e"].includes(event.key.toLowerCase())) {
    event.preventDefault();
    const delta = event.key.toLowerCase() === "q" ? -1 : 1;
    show(
      screens[
        (screens.indexOf(activeScreen) + delta + screens.length) %
          screens.length
      ],
      true,
    );
    return;
  }
  if (
    ["ArrowUp", "ArrowDown"].includes(event.key) &&
    !target.matches("textarea")
  ) {
    const items = navigable();
    if (!items.length) return;
    event.preventDefault();
    const current = items.indexOf(target),
      delta = event.key === "ArrowDown" ? 1 : -1;
    const next =
      current < 0
        ? delta > 0
          ? 0
          : items.length - 1
        : (current + delta + items.length) % items.length;
    items[next].focus();
    items[next].scrollIntoView({ block: "nearest" });
    return;
  }
  if (!editing && ["ArrowLeft", "ArrowRight"].includes(event.key)) {
    if (changeValue(target, event.key === "ArrowRight" ? 1 : -1))
      event.preventDefault();
  }
  if (
    event.key === "Enter" &&
    target.matches(".shuffle-card, .switch-control")
  ) {
    event.preventDefault();
    changeValue(target, 0);
  }
});
document.addEventListener("focusin", (event) => {
  describe(event.target.closest("[data-help]"));
  updateHints();
});
document.addEventListener("pointerover", (event) =>
  describe(event.target.closest("[data-help]")),
);

function control(info) {
  const cards = info.display === "cards";
  const full = cards || info.kind === "multi" || info.kind === "json";
  const field = element(
    "div",
    "field" + (full ? " full" : "") + (cards ? " cards-field" : " menu-row"),
  );
  bindHelp(field, info);
  field.dataset.setting = info.key;
  const label = element("label", "", info.label);
  label.htmlFor = "setting-" + info.key;
  field.append(label);
  const valueCell = cards ? null : element("div", "value-cell");
  let input;
  if (info.kind === "multi") {
    input = element("div", "options" + (cards ? " cards-grid" : ""));
    input.setAttribute("role", "group");
    input.setAttribute("aria-label", info.label);
    info.options.forEach((choice, index) => {
      const wrap = element("label", cards ? "shuffle-card" : "check-label");
      const check = document.createElement("input");
      check.type = "checkbox";
      check.id = `option-${info.key}-${index}`;
      check.value = choice.value;
      check.checked = values[info.key].includes(choice.value);
      check.disabled = choice.disabled;
      check.dataset.unavailable = String(choice.disabled);
      if (cards) {
        check.hidden = true;
        wrap.tabIndex = 0;
        wrap.dataset.nav = "";
        wrap.dataset.control = check.id;
        wrap.setAttribute("role", "checkbox");
        wrap.setAttribute("aria-disabled", String(choice.disabled));
        const name = element("strong", "", choice.label),
          status = element("span", "choice-status");
        wrap.append(check, name, status);
        const update = () => {
          wrap.classList.toggle("checked", check.checked);
          wrap.classList.toggle("unavailable", choice.disabled);
          wrap.setAttribute("aria-checked", String(check.checked));
          status.textContent = choice.disabled
            ? "Not available yet"
            : check.checked
              ? info.status_labels?.on || "On"
              : info.status_labels?.off || "Off";
        };
        check.addEventListener("change", update);
        update();
      } else wrap.append(check, document.createTextNode(choice.label));
      bindHelp(wrap, {
        label: choice.label,
        help: choice.help,
        note: choice.reason || "",
      });
      input.append(wrap);
    });
  } else if (info.kind === "choice") {
    input = document.createElement("select");
    valueCell.classList.add("choice");
    for (const choice of info.options) {
      const option = element("option", "", choice.label);
      option.value = choice.value;
      option.disabled = choice.disabled;
      option.title = choice.reason;
      input.append(option);
    }
    input.value = values[info.key];
    field.dataset.helpNote = info.options
      .filter((option) => option.reason)
      .map((option) => option.label + ": " + option.reason)
      .join(" ");
  } else if (info.kind === "boolean") {
    input = document.createElement("input");
    input.type = "checkbox";
    input.checked = values[info.key];
    input.hidden = true;
    const toggle = element("div", "switch-control");
    toggle.tabIndex = 0;
    toggle.dataset.nav = "";
    toggle.dataset.control = "setting-" + info.key;
    toggle.setAttribute("role", "switch");
    toggle.setAttribute("aria-label", info.label);
    const off = element("button", "", "Off"),
      on = element("button", "", "On");
    off.tabIndex = on.tabIndex = -1;
    const update = () => {
      off.classList.toggle("chosen", !input.checked);
      on.classList.toggle("chosen", input.checked);
      toggle.setAttribute("aria-checked", String(input.checked));
    };
    off.addEventListener("click", () => {
      input.checked = false;
      input.dispatchEvent(new Event("change", { bubbles: true }));
      toggle.focus();
    });
    on.addEventListener("click", () => {
      input.checked = true;
      input.dispatchEvent(new Event("change", { bubbles: true }));
      toggle.focus();
    });
    input.addEventListener("change", update);
    update();
    toggle.append(input, off, on);
    valueCell.append(toggle);
  } else if (info.kind === "json") {
    input = document.createElement("textarea");
    input.value = JSON.stringify(values[info.key], null, 2);
    input.spellcheck = false;
  } else {
    input = document.createElement("input");
    input.type = info.kind === "integer" ? "number" : "text";
    input.value = values[info.key] ?? "";
    if (info.kind === "integer") {
      input.min = info.min;
      input.max = info.max;
      input.step = 1;
    }
  }
  input.id = "setting-" + info.key;
  input.addEventListener("change", () => syncControls(info));
  if (["json", "nullable-text", "integer"].includes(info.kind))
    input.addEventListener("input", () => {
      valid = false;
      $("start-job").disabled = true;
      clearTimeout(timer);
      timer = setTimeout(() => syncControls(info), 350);
    });
  if (cards) field.append(input);
  else {
    if (info.kind === "integer") {
      const decrease = element("button", "", "−"),
        increase = element("button", "", "+");
      decrease.dataset.keyAction = "Decrease";
      increase.dataset.keyAction = "Increase";
      decrease.setAttribute("aria-label", "Decrease " + info.label);
      increase.setAttribute("aria-label", "Increase " + info.label);
      const step = (direction) => {
        input.value = Math.max(
          info.min,
          Math.min(info.max, Number(input.value) + direction),
        );
        input.dispatchEvent(new Event("change", { bubbles: true }));
      };
      decrease.addEventListener("click", () => step(-1));
      increase.addEventListener("click", () => step(1));
      valueCell.classList.add("number");
      valueCell.append(decrease, input, increase);
    } else if (info.kind !== "boolean") valueCell.append(input);
    field.append(valueCell);
  }
  field.dataset.baseNote = field.dataset.helpNote || "";
  return field;
}
function applyDependencies() {
  for (const info of metadata) {
    const field = document.querySelector(`[data-setting="${info.key}"]`),
      reason = inactive[info.key];
    field.classList.toggle("inactive", Boolean(reason));
    field.setAttribute("aria-disabled", String(Boolean(reason)));
    field.tabIndex = reason ? 0 : -1;
    if (reason) field.dataset.nav = "";
    else delete field.dataset.nav;
    field.dataset.helpNote = [reason, field.dataset.baseNote]
      .filter(Boolean)
      .join(" ");
    field.querySelectorAll("input,select,textarea,button").forEach((el) => {
      el.disabled = Boolean(reason) || el.dataset.unavailable === "true";
    });
    field
      .querySelectorAll(".switch-control")
      .forEach((el) => (el.tabIndex = reason ? -1 : 0));
  }
  updateHints();
}
function renderSettings() {
  $("settings-groups").replaceChildren();
  const groups = [...new Set(metadata.map((info) => info.group))];
  groups.sort((a, b) => Number(a === "Advanced") - Number(b === "Advanced"));
  for (const group of groups) {
    const section = element(
      group === "Advanced" ? "details" : "div",
      "settings-section",
    );
    section.append(
      element(
        group === "Advanced" ? "summary" : "h2",
        group === "Advanced" ? "" : "section-title",
        group,
      ),
    );
    const grid = element("div", "field-grid");
    metadata
      .filter((info) => info.group === group)
      .forEach((info) => grid.append(control(info)));
    section.append(grid);
    $("settings-groups").append(section);
  }
  applyDependencies();
  $("settings-string").value = shareString;
  markPreset();
}
function markPreset() {
  for (const button of document.querySelectorAll("[data-preset]")) {
    const selected = button.dataset.settings === settingsString;
    button.classList.toggle("primary", selected);
    button.setAttribute("aria-pressed", String(selected));
  }
}
function readValues() {
  const result = {};
  for (const info of metadata) {
    const input = $("setting-" + info.key);
    if (info.kind === "multi")
      result[info.key] = [...input.querySelectorAll("input:checked")].map(
        (el) => el.value,
      );
    else if (info.kind === "boolean") result[info.key] = input.checked;
    else if (info.kind === "integer") {
      result[info.key] = Number(input.value);
      if (!input.value || !Number.isSafeInteger(result[info.key]))
        throw new Error(info.label + " needs a whole number");
    } else if (info.kind === "json") {
      try {
        result[info.key] = JSON.parse(input.value);
      } catch {
        throw new Error(info.label + " is not valid JSON");
      }
    } else result[info.key] = input.value || null;
  }
  return result;
}
async function syncControls(changed) {
  clearTimeout(timer);
  const current = ++revision;
  valid = false;
  syncing = true;
  $("start-job").disabled = true;
  try {
    const next = readValues();
    for (const [target, keys] of Object.entries(changed?.clears || {}))
      for (const key of keys) delete next[target][key];
    const data = await api("settings", { values: next });
    if (current !== revision) return;
    values = data.values;
    inactive = data.inactive;
    applyDependencies();
    settingsString = data.settings_string;
    shareString = data.share_string;
    $("settings-string").value = shareString;
    markPreset();
    for (const target of Object.keys(changed?.clears || {}))
      $("setting-" + target).value = JSON.stringify(values[target], null, 2);
    valid = true;
    $("settings-state").textContent =
      "Settings validated · string is up to date";
    error("");
  } catch (e) {
    if (current === revision) {
      $("settings-state").textContent =
        "Not applied — fix the setting before generating";
      error(e.message);
    }
  } finally {
    if (current === revision) {
      syncing = false;
      $("start-job").disabled = !valid || busy;
    }
  }
}
async function applyString() {
  clearTimeout(timer);
  const current = ++revision;
  valid = false;
  syncing = true;
  $("start-job").disabled = true;
  try {
    const data = await api("import-settings", {
      settings_string: $("settings-string").value,
    });
    if (current !== revision) return;
    values = data.values;
    inactive = data.inactive;
    settingsString = data.settings_string;
    shareString = data.share_string;
    $("settings-string").value = shareString;
    renderSettings();
    valid = true;
    $("settings-state").textContent = "Settings string applied to all controls";
    error("");
  } catch (e) {
    if (current === revision) error(e.message);
  } finally {
    if (current === revision) {
      syncing = false;
      $("start-job").disabled = !valid || busy;
    }
  }
}
function suggestOutput() {
  if (!outputCustom && outputRoot)
    $("output").value =
      outputRoot +
      (outputRoot.includes("\\") ? "\\" : "/") +
      "seed-" +
      $("seed").value;
}
function preferenceWarning(message) {
  $("preferences-warning").textContent = message || "";
  $("preferences-warning").hidden = !message;
}
function updateLibraryActions() {
  for (const { button, kind, entry } of libraryActions) {
    button.disabled =
      kind === "play"
        ? busy ||
          playState.running ||
          !entry.playable ||
          !playAvailable ||
          !gameCanPlay
        : kind === "open"
          ? !openAvailable
          : kind === "note"
            ? !entry.note_available
            : busy || !entry.playable;
  }
}
async function selectSavedSeed(output) {
  renderJob(await api("select-seed", { output }));
}
async function refreshSeeds() {
  try {
    const data = await api("seeds");
    preferenceWarning(data.warning);
    $("seed-list").replaceChildren();
    libraryActions = [];
    for (const entry of data.seeds) {
      const card = element("article", "seed-entry"),
        title = entry.seed === undefined ? entry.name : "Seed " + entry.seed;
      card.append(
        element(
          "h3",
          "",
          title + (entry.short_hash ? " · " + entry.short_hash : ""),
        ),
      );
      card.append(element("code", "seed-folder", entry.output));
      card.append(
        element(
          "p",
          "help",
          entry.playable
            ? "Clawshot " +
                entry.clawshot_version +
                " · checked when you Play or View"
            : entry.reason,
        ),
      );
      if (!entry.playable) {
        $("seed-list").append(card);
        continue;
      }
      const actions = element("div", "result-actions");
      const add = (label, kind, action) => {
        const button = element("button", "", label);
        button.dataset.keyAction = label;
        button.addEventListener("click", async () => {
          error("");
          try {
            await action();
          } catch (e) {
            error(e.message);
          }
        });
        libraryActions.push({ button, kind, entry });
        actions.append(button);
      };
      add("View seed", "view", () => selectSavedSeed(entry.output));
      add("Play", "play", async () => {
        await selectSavedSeed(entry.output);
        $("play-seed").click();
      });
      add("Open folder", "open", () =>
        api("open", { target: "folder", output: entry.output }),
      );
      add("Play note (spoilers)", "note", () =>
        documentView("note", entry.output),
      );
      card.append(actions);
      bindHelp(card, {
        ...inputs.seeds,
        label: title,
        note: entry.reason || "Hash: " + entry.short_hash,
      });
      $("seed-list").append(card);
    }
    $("seed-library-status").textContent = data.seeds.length
      ? "Saved seeds are checked before Play. Find seeds opens another folder."
      : "No saved seeds found. Generate one, or choose Find seeds.";
    updateLibraryActions();
  } catch (e) {
    error(e.message);
  }
}
async function browse(kind) {
  $("dump-dialog").close();
  document
    .querySelectorAll("[data-browse], #browse-dump")
    .forEach((el) => (el.disabled = true));
  try {
    const data = await api("browse", {
      kind,
      seed: Number($("seed").value),
      window: {
        x: Math.round(window.screenX),
        y: Math.round(window.screenY),
        width: Math.round(window.outerWidth),
        height: Math.round(window.outerHeight),
      },
    });
    if (!data.path) return;
    preferenceWarning(data.warning);
    if (kind === "seeds") {
      await refreshSeeds();
      return;
    }
    if (kind === "emulator_mods") {
      emulatorFolder = data.path;
      renderEmulator();
      return;
    }
    const field = kind.startsWith("dump-") ? "dump" : kind;
    $(field === "game" ? "game-folder" : field).value = data.path;
    if (field === "output") outputCustom = true;
    else await detect(field);
  } catch (e) {
    error(e.message);
  } finally {
    document
      .querySelectorAll("[data-browse], #browse-dump")
      .forEach((el) => (el.disabled = !dialogsAvailable));
  }
}
async function detect(kind, fillDump = true) {
  if (kind === "game") gameCanPlay = false;
  const field = $(kind === "game" ? "game-folder" : kind),
    checkedPath = field.value,
    button = $(kind === "dump" ? "check-dump" : "check-game"),
    status = $(kind + "-status");
  button.disabled = true;
  status.textContent = "Checking…";
  status.className = "value-cell detection";
  try {
    const data = await api("detect", { [kind]: checkedPath }),
      info = data[kind];
    // Game blur normalization may finish in flight. Dump detection can also redirect a picked layer to its root.
    if (kind === "game" && field.value !== checkedPath && field.value !== info.selected_folder) return;
    preferenceWarning(data.warning);
    status.className = "value-cell detection good";
    if (kind === "dump") {
      $("dump").value = info.path;
      status.textContent = "Verified " + info.kind + " · build " + info.build;
    } else {
      gameCanPlay = info.supports_mods && !info.reason;
      gameLabel = info.game;
      field.value = info.selected_folder;
      status.textContent =
        gameLabel + " " +
        (info.version || "unknown version") +
        (info.reason ? " · " + info.reason : " · mods supported");
      if (info.reason) status.className = "value-cell detection bad";
      if (fillDump && !$("dump").value.trim()) {
        $("dump").value = info.romfs || info.nups[0] || "";
        if ($("dump").value) await detect("dump");
      }
    }
    error("");
  } catch (e) {
    status.className = "value-cell detection bad";
    status.textContent = e.message;
  } finally {
    button.disabled = false;
    describe(document.querySelector(`[data-interface=${kind === "game" ? "runtime" : kind}]`));
    renderPlay();
    updateLibraryActions();
  }
}
function renderEmulator() {
  $("emulator-folder").textContent =
    emulatorFolder || "Choose your emulator's mod folder for this game.";
  $("confirm-emulator").disabled = !emulatorFolder || !copyAvailable || busy;
  $("use-eden").hidden = !edenFolder;
  $("use-eden").textContent = "Use Eden folder: " + edenFolder;
}
function renderPlay() {
  const selected = Boolean($("game-folder").value.trim());
  $("play-seed").disabled =
    !playAvailable || !gameCanPlay || busy || playState.running;
  $("save-isolation").hidden = !selected;
  $("emulator-steps").hidden = playAvailable && gameCanPlay;
  $("copy-emulator").disabled = !copyAvailable || busy;
  $("play-status").textContent = playState.running
    ? "A seed is running. Quit that game before starting another."
    : !selected
      ? "Play needs a Hookshot or Longshot folder. Choose and Detect it on Game."
      : !playAvailable
        ? playUnavailableReason
        : !gameCanPlay
          ? "Choose Detect beside your Hookshot or Longshot folder on Game to enable Play."
          : "Ready to play in " + gameLabel + " with separate saves for this seed.";
  $("play-paths").textContent =
    playState.output === resultOutput && playState.user
      ? "Seed saves: " + playState.user + " · Log: " + playState.log +
        (playState.options?.message ? " · " + playState.options.message : "")
      : "";
}
function renderJob(state) {
  busy = ["running", "cancelling"].includes(state.status);
  resultShown = ["succeeded", "loaded"].includes(state.status);
  playState = state.play || { running: false };
  resultOutput = state.result?.output || "";
  const loaded = state.status === "loaded";
  $("generation-inputs").hidden = loaded;
  $("job-progress").hidden = loaded;
  $("generate-title").textContent = loaded
    ? "Saved seed " + state.result.seed
    : "Generate a seed";
  $("generate-subtitle").textContent = loaded
    ? "Ready to play. Your current settings are unchanged."
    : "Each seed is checked to make sure you can finish before it is written.";
  $("start-job").textContent = resultShown
    ? "Make another seed"
    : "Generate seed";
  $("start-job").dataset.keyAction = resultShown ? "Edit" : "Generate";
  const stages = state.stages.length ? state.stages : initialStages;
  $("stages").replaceChildren();
  const names = {
    pending: "Waiting",
    active: "Working",
    done: "✓ Done",
    failed: "Failed",
    cancelled: "Cancelled",
  };
  for (const stage of stages) {
    const row = element("div", "progress-step " + stage.status);
    bindHelp(row, inputs["stage-" + stage.key]);
    const value = element("div", "stage-value"),
      time = element(
        "time",
        "",
        stage.status === "pending"
          ? "—"
          : Math.floor(stage.seconds / 60) +
              ":" +
              String(Math.floor(stage.seconds % 60)).padStart(2, "0"),
      );
    value.append(element("span", "", names[stage.status]), time);
    row.append(element("span", "stage-label", stage.label), value);
    $("stages").append(row);
  }
  const done = stages.filter((stage) => stage.status === "done").length;
  $("progress-fill").style.width = (100 * done) / stages.length + "%";
  document.querySelector(".progress-track").setAttribute("aria-valuenow", done);
  $("start-job").disabled = busy || !valid || syncing;
  $("cancel-job").hidden = !busy;
  $("cancel-job").disabled = state.status === "cancelling";
  $("generation-inputs")
    .querySelectorAll("input, button")
    .forEach(
      (el) =>
        (el.disabled =
          busy || (el.matches("[data-browse]") && !dialogsAvailable)),
    );
  $("job-state").textContent = busy
    ? "Working locally · " + Math.floor(state.seconds) + "s"
    : state.status === "cancelled"
      ? "Cancelled. Existing seeds were left alone."
      : state.status === "succeeded"
        ? "Complete. Previous seeds are unchanged."
        : loaded
          ? "Loaded from My seeds."
          : "Your current game stays as it is.";
  $("result").hidden = activeScreen !== "generate" || !resultShown;
  if (state.error) error(state.error.type + ": " + state.error.message);
  if (state.result) {
    const count = (number, noun) =>
      number + " " + noun + (number === 1 ? "" : "s");
    $("result-summary").textContent =
      "Seed " +
      state.result.seed +
      " · " +
      count(state.result.shuffled, "shuffled check") +
      " · " +
      count(state.result.resources, "mod file");
    $("result-number").value = state.result.seed;
    $("result-settings").value = state.result.share_string;
    $("result-hash").value = state.result.short_hash;
    $("result-path").textContent = state.result.output;
  }
  renderPlay();
  updateLibraryActions();
  if (state.status === "succeeded" && resultOutput !== lastLibraryOutput) {
    lastLibraryOutput = resultOutput;
    refreshSeeds();
  }
  updateHints();
}
async function refreshJob() {
  clearTimeout(pollTimer);
  try {
    renderJob(await api("job"));
    if (busy || playState.running)
      pollTimer = setTimeout(refreshJob, busy ? 500 : 1000);
  } catch (e) {
    error(
      e.message + ". Check the local server terminal; reload to reconnect.",
    );
  }
}
async function normalizePath(input) {
  const original = input.value;
  if (!original) return;
  const data = await api("normalize-path", {
    path: original, kind: input.id === "game-folder" ? "game" : input.id,
  });
  if (input.value === original) input.value = data.path;
}
async function startJob() {
  if (resultShown) {
    try {
      renderJob(await api("select-seed", { output: null }));
    } catch (e) {
      error(e.message);
    }
    return;
  }
  if (!valid || syncing) {
    error("Apply or correct your settings before generating");
    return;
  }
  const seed = Number($("seed").value);
  if (!$("seed").value || !Number.isSafeInteger(seed)) {
    error("Seed needs a whole number in the exact integer range");
    return;
  }
  $("start-job").disabled = true;
  error("");
  try {
    for (const input of document.querySelectorAll("[data-path]"))
      await normalizePath(input);
    renderJob(
      await api("generate", {
        dump: $("dump").value,
        game: $("game-folder").value,
        output: $("output").value,
        seed,
        settings: settingsString,
      }),
    );
    refreshJob();
  } catch (e) {
    error(e.message);
    $("start-job").disabled = !valid;
  }
}
function openDialog(id) {
  $(id).showModal();
  updateHints();
}
function closeDialog(id) {
  $(id).close();
  updateHints();
}
function renderNote(text, target) {
  target.replaceChildren();
  let paragraph = [],
    table = null;
  const flush = () => {
    if (paragraph.length) target.append(element("p", "", paragraph.join(" ")));
    paragraph = [];
  };
  for (const line of text.split(/\r?\n/)) {
    const heading = line.match(/^(#{1,6}) (.*)$/);
    if (heading) {
      flush();
      table = null;
      target.append(
        element(heading[1].length === 1 ? "h3" : "h4", "", heading[2]),
      );
    } else if (line.startsWith("|")) {
      flush();
      const cells = line
        .trim()
        .slice(1, -1)
        .split(/(?<!\\)\|/)
        .map((cell) => cell.trim().replace(/\\\|/g, "|"));
      if (cells.every((cell) => /^:?-+:?$/.test(cell))) continue;
      const header = table === null;
      if (header) {
        table = element("table");
        target.append(table);
      }
      const row = element("tr");
      for (const cell of cells)
        row.append(element(header ? "th" : "td", "", cell));
      table.append(row);
    } else {
      table = null;
      if (!line.trim()) flush();
      else paragraph.push(line);
    }
  }
  flush();
}
async function documentView(file, output) {
  const confirmed =
    file !== "spoiler" ||
    confirm(
      "Reveal the spoiler? This shows all shuffled item locations and hints.",
    );
  if (!confirmed) return;
  try {
    const data = await api("result", {
      file,
      confirmed,
      ...(output ? { output } : {}),
    });
    $("document-title").textContent =
      file === "note" ? "Play note (spoilers)" : data.name;
    $("document-text").textContent = data.text;
    $("document-text").hidden = file === "note";
    $("document-note").hidden = file !== "note";
    if (file === "note") renderNote(data.text, $("document-note"));
    openDialog("document-dialog");
  } catch (e) {
    error(e.message);
  }
}

document
  .querySelectorAll("[data-screen]")
  .forEach((el) => el.addEventListener("click", () => show(el.dataset.screen)));
document
  .querySelectorAll("[data-next]")
  .forEach((el) => el.addEventListener("click", () => show(el.dataset.next)));
$("check-dump").addEventListener("click", () => detect("dump"));
$("check-game").addEventListener("click", () => detect("game"));
$("browse-dump").addEventListener("click", () => openDialog("dump-dialog"));
$("close-dump").addEventListener("click", () => closeDialog("dump-dialog"));
document
  .querySelectorAll("[data-browse]")
  .forEach((el) =>
    el.addEventListener("click", () => browse(el.dataset.browse)),
  );
document.querySelectorAll("[data-path]").forEach((input) =>
  input.addEventListener("change", async () => {
    try {
      await normalizePath(input);
    } catch (e) {
      error(e.message);
    }
  }),
);
for (const [id, action] of Object.entries({
  "check-game": "Detect",
  "check-dump": "Check",
  "random-seed": "Randomize",
  "copy-string": "Copy",
  "apply-string": "Apply",
  "cancel-job": "Cancel",
  "reveal-spoiler": "Reveal",
}))
  $(id).dataset.keyAction = action;
$("output").addEventListener("input", () => (outputCustom = true));
$("seed").addEventListener("input", suggestOutput);
function randomizeSeed() {
  const number = new Uint32Array(1);
  crypto.getRandomValues(number);
  $("seed").value = String(number[0]);
  suggestOutput();
}
$("random-seed").addEventListener("click", randomizeSeed);
$("apply-string").addEventListener("click", applyString);
async function copyField(id, status, discord = false) {
  const input = $(id);
  try {
    await navigator.clipboard.writeText(discord ? "`" + input.value + "`" : input.value);
    $(status).textContent = discord ? "Copied for Discord (in backticks)" : "Copied";
  } catch {
    input.focus();
    input.select();
    $(status).textContent = "Selected — press Ctrl+C or Command+C to copy" +
      (discord ? ", then wrap it in single backticks on Discord." : "");
  }
}
document
  .querySelectorAll("[data-copy]")
  .forEach((button) =>
    button.addEventListener("click", () =>
      copyField(button.dataset.copy, "share-status", button.hasAttribute("data-discord")),
    ),
  );
$("enter-shared").addEventListener("click", () => openDialog("shared-dialog"));
$("close-shared").addEventListener("click", () => closeDialog("shared-dialog"));
$("apply-shared").addEventListener("click", async () => {
  try {
    if (
      !$("shared-number").value ||
      !Number.isSafeInteger(Number($("shared-number").value))
    )
      throw new Error("Enter a whole seed number.");
    const data = await api("shared-seed", {
      seed: Number($("shared-number").value),
      settings_string: $("shared-settings").value,
    });
    clearTimeout(timer);
    ++revision;
    values = data.values;
    inactive = data.inactive;
    settingsString = data.settings_string;
    shareString = data.share_string;
    $("seed").value = String(data.seed);
    renderSettings();
    valid = true;
    syncing = false;
    suggestOutput();
    renderJob(await api("select-seed", { output: null }));
    closeDialog("shared-dialog");
    error("");
  } catch (e) {
    $("shared-error").textContent = e.message;
  }
});
$("copy-string").addEventListener("click", () =>
  copyField("settings-string", "settings-state"),
);
$("copy-discord").addEventListener("click", () =>
  copyField("settings-string", "settings-state", true),
);
$("settings-string").addEventListener("input", () => {
  clearTimeout(timer);
  ++revision;
  valid = false;
  $("start-job").disabled = true;
  $("settings-state").textContent = "String edited — Apply to update controls";
});
$("start-job").addEventListener("click", startJob);
$("refresh-seeds").addEventListener("click", refreshSeeds);
$("play-seed").dataset.keyAction = "Play";
$("play-seed").addEventListener("click", async () => {
  $("play-seed").disabled = true;
  error("");
  try {
    playState = await api("play", { game: $("game-folder").value });
    await refreshJob();
  } catch (e) {
    error(e.message);
    renderPlay();
  }
});
$("game-folder").addEventListener("input", () => {
  gameCanPlay = false;
  $("game-status").textContent = "Not checked · choose Detect";
  $("game-status").className = "value-cell detection";
  renderPlay();
  updateLibraryActions();
});
$("cancel-job").addEventListener("click", async () => {
  try {
    renderJob(await api("cancel", {}));
    refreshJob();
  } catch (e) {
    error(e.message);
  }
});
$("open-folder").addEventListener("click", async () => {
  try {
    await api("open", { target: "folder" });
  } catch (e) {
    error(e.message);
  }
});
$("copy-emulator").addEventListener("click", () => {
  renderEmulator();
  $("emulator-copy-status").textContent = "";
  openDialog("emulator-dialog");
});
$("close-emulator").addEventListener("click", () =>
  closeDialog("emulator-dialog"),
);
$("use-eden").addEventListener("click", async () => {
  try {
    const data = await api("choose-eden", {});
    emulatorFolder = data.path;
    preferenceWarning(data.warning);
    renderEmulator();
  } catch (e) {
    $("emulator-copy-status").textContent = e.message;
  }
});
$("confirm-emulator").addEventListener("click", async () => {
  $("confirm-emulator").disabled = true;
  try {
    const data = await api("copy-emulator", {
      output: resultOutput,
      confirmed: true,
    });
    $("emulator-copy-status").textContent =
      "Copied to " + data.path + ". " + data.warning;
  } catch (e) {
    $("emulator-copy-status").textContent = e.message;
  } finally {
    renderEmulator();
  }
});
$("read-note").addEventListener("click", () => documentView("note"));
$("reveal-spoiler").addEventListener("click", () => documentView("spoiler"));
$("close-document").addEventListener("click", () =>
  closeDialog("document-dialog"),
);
document
  .querySelectorAll("dialog")
  .forEach((dialog) => dialog.addEventListener("close", updateHints));
window.addEventListener("beforeunload", (event) => {
  if (busy) {
    event.preventDefault();
    event.returnValue = "";
  }
});

(async () => {
  try {
    const data = await api("schema");
    metadata = data.schema;
    values = data.values;
    settingsString = data.settings_string;
    shareString = data.share_string;
    inputs = data.inputs;
    inactive = data.inactive;
    initialStages = data.stages;
    outputRoot = data.output_root;
    dialogsAvailable = data.dialogs_available;
    document.querySelectorAll("[data-browse], #browse-dump").forEach((el) => {
      el.disabled = !dialogsAvailable;
      if (!dialogsAvailable)
        el.title = "Disabled in --no-open; paste a path instead";
    });
    openAvailable = data.open_available;
    $("open-folder").disabled = !openAvailable;
    preferenceWarning(data.preferences_warning);
    $("dump").value = data.paths.dump || "";
    $("game-folder").value = data.paths.game || "";
    emulatorFolder = data.paths.emulator_mods || "";
    edenFolder = data.eden_folder || "";
    copyAvailable = data.copy_available;
    playAvailable = data.play_available;
    playUnavailableReason = data.play_unavailable_reason;
    randomizeSeed();
    document
      .querySelectorAll("[data-interface]")
      .forEach((el) => bindHelp(el, inputs[el.dataset.interface]));
    for (const preset of data.presets) {
      const button = element("button", "", preset.label);
      button.dataset.preset = preset.id;
      button.dataset.settings = preset.settings_string;
      bindHelp(button, preset);
      button.dataset.keyAction = "Apply";
      button.addEventListener("click", async () => {
        $("settings-string").value = preset.share_string;
        await applyString();
        if (valid)
          $("settings-state").textContent = preset.label + " preset applied";
      });
      $("presets").append(button);
    }
    $("version").textContent = "v" + data.version;
    renderSettings();
    valid = true;
    show(location.hash.slice(1));
    await refreshJob();
    await refreshSeeds();
    const hadDump = Boolean($("dump").value);
    if ($("game-folder").value) await detect("game", !hadDump);
    if (hadDump) await detect("dump");
    document.documentElement.dataset.ready = "true";
  } catch (e) {
    error(e.message);
  }
})();
