"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(
  path.join(__dirname, "../../apps/desktop-prototype/comfyui-capabilities-ui.js"),
  "utf8",
);

class FakeElement {
  constructor(tagName) {
    this.tagName = tagName;
    this.children = [];
    this.className = "";
    this._text = "";
  }
  appendChild(child) {
    this.children.push(child);
    return child;
  }
  replaceChildren(...children) {
    this.children = [...children];
    this._text = "";
  }
  set textContent(value) {
    this._text = String(value);
    this.children = [];
  }
  get textContent() {
    return this._text + this.children.map((child) => child.textContent).join("");
  }
}

function setup(translate = (value) => value) {
  const window = { STILLAI18N: { translate } };
  const document = { createElement: (tagName) => new FakeElement(tagName) };
  vm.runInNewContext(source, { window, document });
  return { window, root: new FakeElement("div") };
}

function sampleReport() {
  return {
    status: "partial",
    comfyui_version: "0.3.26",
    node_count: 3,
    generation_ready: false,
    capabilities: [
      {
        capability: "ipadapter",
        status: "available",
        nodes: [
          {
            class_name: "IPAdapterModelLoader",
            required_inputs: ["ipadapter_file"],
            schema_valid: true,
          },
          {
            class_name: "IPAdapterApply",
            required_inputs: ["ipadapter", "clip_vision", "image", "model", "weight"],
            schema_valid: true,
          },
        ],
        missing_nodes: [],
      },
      {
        capability: "instantid",
        status: "partial",
        nodes: [{
          class_name: "ApplyInstantID",
          required_inputs: ["model", "positive"],
          schema_valid: false,
        }],
        missing_nodes: ["InstantIDModelLoader (required input schema mismatch)"],
      },
    ],
  };
}

test("capability UI renders node schemas and keeps generation explicitly disabled", () => {
  const { window, root } = setup();
  window.STILLAComfyUICapabilityUI.render(root, sampleReport());

  assert.match(root.textContent, /IPAdapter/);
  assert.match(root.textContent, /InstantID/);
  assert.match(root.textContent, /IPAdapterApply/);
  assert.match(root.textContent, /Required sockets/);
  assert.match(root.textContent, /generation ready/i);
  assert.match(root.textContent, /No — discovery only/);
});

test("capability UI uses translated labels", () => {
  const { window, root } = setup((value) => "MY:" + value);
  window.STILLAComfyUICapabilityUI.render(root, sampleReport());

  assert.match(root.textContent, /MY:Installed ComfyUI conditioning capabilities/);
  assert.match(root.textContent, /MY:Required sockets/);
});

test("capability UI treats server-derived node names as text, not HTML", () => {
  const { window, root } = setup();
  const report = sampleReport();
  report.capabilities[0].nodes[0].class_name = "<img src=x onerror=alert(1)>";
  window.STILLAComfyUICapabilityUI.render(root, report);

  assert.match(root.textContent, /<img src=x onerror=alert\(1\)>/);
  assert.equal(root.children.some((child) => child.tagName === "img"), false);
});

test("capability UI rejects any report that claims generation readiness", () => {
  const { window, root } = setup();
  const report = sampleReport();
  report.generation_ready = true;

  assert.throws(
    () => window.STILLAComfyUICapabilityUI.render(root, report),
    /generation remains disabled/,
  );
});


test("capability UI accepts the complete three-node InstantID contract", () => {
  const { window, root } = setup();
  const report = sampleReport();
  report.status = "available";
  report.node_count = 5;
  report.capabilities[1] = {
    capability: "instantid",
    status: "available",
    nodes: [
      { class_name: "InstantIDModelLoader", required_inputs: ["instantid_file"], schema_valid: true },
      { class_name: "InstantIDFaceAnalysis", required_inputs: ["provider"], schema_valid: true },
      { class_name: "ApplyInstantID", required_inputs: ["instantid", "insightface", "image", "model", "positive", "negative"], schema_valid: true },
    ],
    missing_nodes: [],
  };
  window.STILLAComfyUICapabilityUI.render(root, report);
  assert.match(root.textContent, /InstantIDModelLoader/);
  assert.match(root.textContent, /InstantIDFaceAnalysis/);
  assert.match(root.textContent, /ApplyInstantID/);
});

test("capability UI accepts all three missing InstantID nodes as unsupported", () => {
  const { window, root } = setup();
  const report = sampleReport();
  report.capabilities[1] = {
    capability: "instantid",
    status: "unsupported",
    nodes: [],
    missing_nodes: ["InstantIDModelLoader", "InstantIDFaceAnalysis", "ApplyInstantID"],
  };
  window.STILLAComfyUICapabilityUI.render(root, report);
  assert.match(root.textContent, /InstantIDModelLoader/);
  assert.match(root.textContent, /InstantIDFaceAnalysis/);
  assert.match(root.textContent, /ApplyInstantID/);
});
