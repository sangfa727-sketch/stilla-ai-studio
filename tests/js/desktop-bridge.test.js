"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(
  path.join(__dirname, "../../apps/desktop-prototype/desktop-bridge.js"),
  "utf8",
);

test("desktop bridge forwards durable revision and document CAS tokens", async () => {
  const calls = [];
  const api = new Proxy({}, {
    get(_target, method) {
      return async (...args) => {
        calls.push([String(method), ...args]);
        if (method === "save_character_profile") {
          return { saved: true, revision: 4 };
        }
        if (method === "load_document_versioned") {
          return { value: { schema_version: 1 }, revision: "a".repeat(64) };
        }
        if (method === "save_document_versioned") {
          return { saved: true, revision: "b".repeat(64) };
        }
        return [];
      };
    },
  });
  const window = {
    location: { search: "?runtime=desktop" },
    pywebview: { api },
    addEventListener() {},
  };
  vm.runInNewContext(source, { window, URLSearchParams });
  const bridge = window.STILLABridge;

  assert.equal(bridge.isDesktop(), true);
  const character = await bridge.saveCharacter("project_1", { id: "hero_1" }, 3);
  const imported = await bridge.saveCharacter("project_1", { id: "hero_2" }, 0);
  const loaded = await bridge.loadDocumentVersioned("project_1", "storyboard");
  const saved = await bridge.saveDocumentVersioned(
    "project_1", "storyboard", { schema_version: 1 }, loaded.revision,
  );

  assert.equal(character.revision, 4);
  assert.equal(imported.revision, 4);
  assert.equal(loaded.revision, "a".repeat(64));
  assert.equal(saved.revision, "b".repeat(64));
  assert.deepEqual(calls, [
    ["save_character_profile", "project_1", { id: "hero_1" }, 3],
    ["save_character_profile", "project_1", { id: "hero_2" }, 0],
    ["load_document_versioned", "project_1", "storyboard"],
    ["save_document_versioned", "project_1", "storyboard", { schema_version: 1 }, "a".repeat(64)],
  ]);
});
