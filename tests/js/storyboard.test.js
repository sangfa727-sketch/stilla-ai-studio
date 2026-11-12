"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(
  path.join(__dirname, "../../apps/desktop-prototype/storyboard.js"),
  "utf8",
);

function createHarness(rawValue = null) {
  const key = "stilla.storyboard.v1.project-1";
  const store = new Map();
  if (rawValue !== null) store.set(key, rawValue);
  const elements = new Map();
  const alerts = [];
  const fields = {
    "[data-description]": [{ dataset: { description: "shot_001" }, value: "Edited opening scene" }],
    "[data-duration]": [{ dataset: { duration: "shot_001" }, value: "8" }],
    "[data-camera]": [{ dataset: { camera: "shot_001" }, value: "Wide shot" }],
  };

  function element(id) {
    if (!elements.has(id)) {
      const handlers = {};
      elements.set(id, {
        id,
        textContent: "",
        innerHTML: "",
        disabled: false,
        addEventListener(type, callback) { handlers[type] = callback; },
        click() { return handlers.click?.({ currentTarget: this }); },
      });
    }
    return elements.get(id);
  }

  const document = {
    getElementById: element,
    querySelectorAll(selector) { return fields[selector] || []; },
    querySelector() { return null; },
  };
  const localStorage = {
    getItem(name) { return store.has(name) ? store.get(name) : null; },
    setItem(name, value) { store.set(name, String(value)); },
  };
  const window = {
    STILLACharacterUI: {
      async loadProject() {},
      getProfiles() { return []; },
    },
    STILLAI18N: { refresh() {} },
  };

  vm.runInNewContext(source, {
    window,
    document,
    localStorage,
    alert(message) { alerts.push(String(message)); },
    CSS: { escape(value) { return String(value); } },
  });

  return { key, store, elements, alerts, window, document };
}

test("adding a shot preserves edits made in existing shot fields", async () => {
  const harness = createHarness();
  await harness.window.STILLAStoryboardUI.mount("project-1");

  await harness.elements.get("addStoryboardShot").click();
  await harness.elements.get("saveStoryboard").click();

  const saved = JSON.parse(harness.store.get(harness.key));
  assert.equal(saved.shot_plan.shots.length, 4);
  assert.equal(saved.shot_plan.shots[0].description, "Edited opening scene");
  assert.equal(saved.shot_plan.shots[0].camera, "Wide shot");
});

test("malformed browser storyboard JSON is preserved and fails closed", async () => {
  const malformed = "{not valid JSON";
  const harness = createHarness(malformed);
  await harness.window.STILLAStoryboardUI.mount("project-1");

  assert.equal(harness.store.get(harness.key), malformed);
  assert.match(harness.elements.get("storyboardBindingRoot").innerHTML, /invalid JSON/);
  assert.equal(harness.elements.get("saveStoryboard"), undefined);
});

test("valid JSON with an invalid storyboard shape is preserved and fails closed", async () => {
  const malformed = JSON.stringify({ schema_version: 1, shot_plan: { shots: [] } });
  const harness = createHarness(malformed);
  await harness.window.STILLAStoryboardUI.mount("project-1");

  assert.equal(harness.store.get(harness.key), malformed);
  assert.match(harness.elements.get("storyboardBindingRoot").innerHTML, /invalid structure/);
});
