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


test("desktop bridge uses the transactional reference attachment API", async () => {
  const calls = [];
  const profile = { id: "hero_1", references: [{ asset_id: "asset_1" }] };
  const api = new Proxy({}, {
    get(_target, method) {
      return async (...args) => {
        calls.push([String(method), ...args]);
        if (method === "import_character_reference_and_save") {
          return {
            cancelled: false,
            saved: true,
            profile,
            revision: 2,
            updated_at: "2026-11-14T00:00:00Z",
            mirror_recovery_pending: false,
          };
        }
        return null;
      };
    },
  });
  const window = {
    location: { search: "?runtime=desktop" },
    pywebview: { api },
    addEventListener() {},
  };
  vm.runInNewContext(source, { window, URLSearchParams });
  const result = await window.STILLABridge.importCharacterReferenceAndSave(
    "project_1", "hero_1", 1,
  );

  assert.equal(result.saved, true);
  assert.equal(result.revision, 2);
  assert.deepEqual(result.profile, profile);
  assert.deepEqual(calls, [[
    "import_character_reference_and_save", "project_1", "hero_1", 1,
  ]]);
});


test("desktop bridge retains the legacy reference import method", async () => {
  const calls = [];
  const api = new Proxy({}, {
    get(_target, method) {
      return async (...args) => {
        calls.push([String(method), ...args]);
        return { cancelled: true };
      };
    },
  });
  const window = {
    location: { search: "?runtime=desktop" },
    pywebview: { api },
    addEventListener() {},
  };
  vm.runInNewContext(source, { window, URLSearchParams });
  const result = await window.STILLABridge.importCharacterReference(
    "project_1", "hero_1",
  );

  assert.equal(result.cancelled, true);
  assert.deepEqual(calls, [[
    "import_character_reference", "project_1", "hero_1",
  ]]);
});
