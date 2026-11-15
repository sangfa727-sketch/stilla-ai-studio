"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(
  path.join(__dirname, "../../apps/desktop-prototype/characters.js"),
  "utf8",
);

function loadCharacterUI(dimensions = { width: 2, height: 3 }, decodeError = null) {
  class FakeImage {
    constructor() {
      this.naturalWidth = 0;
      this.naturalHeight = 0;
      this.decoding = "";
    }
    set src(value) {
      this._src = value;
      this.naturalWidth = dimensions.width;
      this.naturalHeight = dimensions.height;
    }
    get src() {
      return this._src;
    }
    decode() {
      return decodeError ? Promise.reject(decodeError) : Promise.resolve();
    }
  }
  const window = {};
  vm.runInNewContext(source, { window, Image: FakeImage });
  return window.STILLACharacterUI;
}

test("reference preview decoder accepts a decoded bounded image", async () => {
  const ui = loadCharacterUI();
  const result = await ui.decodeReferenceImage("data:image/png;base64,AQ==");
  assert.deepEqual({ width: result.width, height: result.height }, { width: 2, height: 3 });
});

test("reference preview decoder rejects non-data URLs and unsupported formats", async () => {
  const ui = loadCharacterUI();
  await assert.rejects(
    ui.decodeReferenceImage("file:///C:/private/reference.png"),
    /invalid or too large/,
  );
  await assert.rejects(
    ui.decodeReferenceImage("data:image/svg+xml;base64,PHN2Zy8+"),
    /invalid or too large/,
  );
});

test("reference preview decoder rejects oversized decoded dimensions", async () => {
  const ui = loadCharacterUI({ width: 10000, height: 4001 });
  await assert.rejects(
    ui.decodeReferenceImage("data:image/webp;base64,AQ=="),
    /dimensions exceed/,
  );
});

test("reference preview decoder rejects browser decode failures", async () => {
  const ui = loadCharacterUI({ width: 1, height: 1 }, new Error("corrupt image"));
  await assert.rejects(
    ui.decodeReferenceImage("data:image/jpeg;base64,AQ=="),
    /corrupt image/,
  );
});

test("character actions refresh the rendered workspace after local mutations", () => {
  assert.match(source, /const refresh = \(\) => \{[\s\S]*root\.innerHTML = render\(\);[\s\S]*wire\(\);/);
  assert.match(source, /data-character-id[\s\S]*refresh\(\)/);
  assert.match(source, /data-remove-ref[\s\S]*refresh\(\)/);
});
