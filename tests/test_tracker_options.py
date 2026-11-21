"""Exercise the shipped tracker.js under Node: its fragment parser, and its rendering of a tracker snapshot in a
minimal stand-in DOM. Node is optional and is not an app dependency."""

import json
import shutil
import subprocess

import pytest

from clawshot.ui.server import ASSETS

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node is needed only for frontend fragment-parser tests")
ALL = ["items", "quest", "dungeons"]


def parse_sections(tmp_path, fragments):
    # The renderer exits without a root; the actual pure parser runs with Node's URLSearchParams.
    script = """
const fs = require('node:fs');
const vm = require('node:vm');
const context = {document: {getElementById: () => null}, URLSearchParams};
vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'), context);
const fragments = JSON.parse(fs.readFileSync(0, 'utf8'));
console.log(JSON.stringify(fragments.map(value => context.parseTrackerSections(value))));
"""
    runner = tmp_path / "tracker-options.cjs"
    runner.write_text(script, encoding="utf-8")
    result = subprocess.run(
        [NODE, str(runner), str(ASSETS / "tracker.js")],
        input=json.dumps(fragments),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, {"stdout": result.stdout, "stderr": result.stderr}
    return json.loads(result.stdout)


# A stand-in for the few DOM calls tracker.js makes; fetch answers every tracker poll with one snapshot.
RENDER = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const {fragment, obs, snapshot, actions = [], storage = {}, confirm = false, after = null} = input;

class Element {
  constructor(tag, text = '') {
    this.tagName = tag.toUpperCase();
    this.childNodes = [];
    this.parentElement = null;
    this.className = '';
    this.dataset = {};
    this.attributes = {};
    this.style = {setProperty() {}};
    this.hidden = false;
    this.ownText = text;
    this.listeners = {};
  }
  get classList() {
    const names = () => this.className.split(/\s+/).filter(Boolean);
    const set = (list) => { this.className = [...new Set(list)].join(' '); };
    return {
      add: (...add) => set([...names(), ...add]),
      remove: (...drop) => set(names().filter((name) => !drop.includes(name))),
      toggle: (name, force = !names().includes(name)) => {
        set(force ? [...names(), name] : names().filter((other) => other !== name));
        return force;
      },
      contains: (name) => names().includes(name),
    };
  }
  append(...nodes) {
    for (const child of nodes) {
      const el = typeof child === 'string' ? new Element('#text', child) : child;
      el.remove();
      el.parentElement = this;
      this.childNodes.push(el);
    }
  }
  replaceChildren(...nodes) {
    for (const child of this.childNodes) child.parentElement = null;
    this.childNodes = [];
    this.append(...nodes);
  }
  remove() {
    if (!this.parentElement) return;
    const siblings = this.parentElement.childNodes;
    siblings.splice(siblings.indexOf(this), 1);
    this.parentElement = null;
  }
  get textContent() { return this.ownText + this.childNodes.map((child) => child.textContent).join(''); }
  set textContent(value) { this.replaceChildren(); this.ownText = String(value); }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  addEventListener(type, listener) { (this.listeners[type] ||= []).push(listener); }
  dispatch(type) { for (const listener of this.listeners[type] || []) listener({preventDefault() {}}); }
  focus() {}
  select() {}
  descendants() { return this.childNodes.flatMap((child) => [child, ...child.descendants()]); }
  querySelector(selector) { return this.querySelectorAll(selector)[0] ?? null; }
  querySelectorAll(selector) {
    const data = /^\[data-([a-z-]+)\]$/.exec(selector);
    const key = data && data[1].replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
    return this.descendants().filter((el) => data ? key in el.dataset : el.tagName === selector.toUpperCase());
  }
}
class Option extends Element {
  constructor(text = '', value = text) { super('option', text); this.value = value; }
}

const root = new Element('div');
const body = new Element('body');
if (obs) body.dataset.tracker = 'obs';
const documentElement = new Element('html');
const document = {
  body, documentElement,
  getElementById: (id) => (id === 'tracker-root' ? root : null),
  createElement: (tag) => new Element(tag),
  createTextNode: (text) => new Element('#text', text),
};
const requested = [], posts = [];
async function fetch(url, init = {}) {
  const route = url.slice(url.lastIndexOf('/api/') + 5);
  requested.push(route);
  if (init.method === 'POST') posts.push({route, body: JSON.parse(init.body)});
  const data = route === 'schema' ? {dialogs_available: false} : init.method === 'POST' && after ? after : snapshot;
  return {ok: true, json: async () => data};
}
// localStorage: a plain store, or (storage null) one whose every access throws, as in a private window.
const stored = storage === null ? null : {...storage};
const localStorage = {
  getItem(key) { if (!stored) throw new Error('storage unavailable'); return key in stored ? stored[key] : null; },
  setItem(key, value) { if (!stored) throw new Error('storage unavailable'); stored[key] = String(value); },
  removeItem(key) { if (!stored) throw new Error('storage unavailable'); delete stored[key]; },
};
const location = {
  pathname: obs ? '/s/secret/tracker.html' : '/s/secret/', hash: fragment, origin: 'http://127.0.0.1:9',
};
const context = {
  document, location, fetch, URL, URLSearchParams, Option, console, navigator: {},
  window: {addEventListener() {}, confirm: () => confirm, localStorage}, setInterval: () => 1, clearInterval() {},
};
(async () => {
  vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'), context);
  for (let turn = 0; turn < 100 && documentElement.dataset.trackerReady !== 'true'; turn++) {
    await new Promise((resolve) => setImmediate(resolve));
  }
  const settle = async () => {
    for (let turn = 0; turn < 20; turn++) await new Promise((resolve) => setImmediate(resolve));
  };
  const byId = (id) => root.descendants().find((el) => el.id === id);
  for (const action of actions) {
    const target = action.id
      ? byId(action.id)
      : root.descendants().filter((el) => el.classList.contains(action.class))[action.index || 0];
    if ('value' in action) target.value = action.value;
    if ('checked' in action) target.checked = action.checked;
    target.dispatch(action.event);
    await settle();
  }
  const text = (name) => root.descendants().filter((el) => el.classList.contains(name)).map((el) => el.textContent);
  const shown = (el) => { for (let at = el; at; at = at.parentElement) if (at.hidden) return false; return true; };
  const control = (id) => {
    const el = byId(id);
    return el ? {value: el.value, checked: el.checked, disabled: !!el.disabled} : null;
  };
  console.log(JSON.stringify({
    checks: root.descendants().filter((el) => el.classList.contains('tracker-check')).map((el) => ({
      id: el.dataset.check, text: el.textContent, className: el.className, shown: shown(el),
    })),
    areaHeads: root.descendants().filter((el) => el.classList.contains('tracker-area-counts')).map((el) => ({
      text: el.textContent, shown: shown(el),
    })),
    notes: text('tracker-logic-note'),
    controls: {
      age: control('tracker-age'), only: control('tracker-logic-only'), vanilla: control('tracker-vanilla'),
      clear: control('tracker-clear-marks'),
    },
    posts,
    storage: stored,
    ready: documentElement.dataset.trackerReady === 'true',
    requested,
    compact: body.classList.contains('tracker-no-labels'),
    status: text('tracker-status'),  // a render error lands here, so a failed render prints its cause
    counts: text('tracker-counts'),
    areas: text('tracker-area'),
  }));
})();
"""


def render_tracker(tmp_path, snapshot, *, obs, fragment="", **page):
    """The shipped renderer drawing one tracker ``snapshot``: the app tab, or (``obs``) the OBS page opened with URL
    ``fragment``. Returns the rendered text by element class (``status``, ``counts``, ``areas``) and the routes it
    polled; for the in-logic controls also ``checks``, ``areaHeads``, ``notes``, ``controls``, ``posts`` and
    ``storage``. ``page`` may give ``actions`` (``{id or class, value/checked, event}``, dispatched in order after the
    first render), ``storage`` (localStorage's contents; None makes every access throw), ``confirm`` (what
    ``window.confirm`` answers) and ``after`` (the snapshot a POST answers)."""
    runner = tmp_path / "tracker-render.cjs"
    runner.write_text(RENDER, encoding="utf-8")
    result = subprocess.run(
        [NODE, str(runner), str(ASSETS / "tracker.js")],
        input=json.dumps({"fragment": fragment, "obs": obs, "snapshot": snapshot, **page}),
        capture_output=True,
        encoding="utf-8",  # the rendered text has non-ASCII separators; Windows' locale default would garble them
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, {"stdout": result.stdout, "stderr": result.stderr}
    rendered = json.loads(result.stdout)
    assert rendered["ready"], rendered
    return rendered


def test_sections_select_groups_without_reordering_or_duplicate_groups(tmp_path):
    fragments = [
        "#columns=4&labels=0&sections=dungeons",
        "#sections=items%2Cquest",
        "#sections=quest,items,quest",
        "#sections=%20quest%20",
    ]
    assert parse_sections(tmp_path, fragments) == [["dungeons"], ["items", "quest"], ["items", "quest"], ["quest"]]


def test_missing_empty_or_unknown_section_selection_falls_back_to_all(tmp_path):
    fragments = [
        "#labels=0",
        "#sections=",
        "#sections=unknown",
        "#sections=items,unknown",
        "#sections=items,,quest",
        "#sections=%20%20",
    ]
    assert parse_sections(tmp_path, fragments) == [ALL for _ in fragments]
