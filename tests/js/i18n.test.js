"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(
  path.join(__dirname, "../../apps/desktop-prototype/i18n.js"),
  "utf8",
);

function createI18n() {
  const document = {
    documentElement: {},
    body: { querySelectorAll() { return []; } },
    createTreeWalker() { return { nextNode() { return false; } }; },
    getElementById() { return null; },
  };
  const localStorage = { setItem() {}, getItem() { return "en"; } };
  const window = {};
  vm.runInNewContext(source, {
    window,
    document,
    localStorage,
    NodeFilter: { SHOW_TEXT: 4 },
  });
  return window.STILLAI18N;
}

test("storyboard dynamic labels translate in both directions", () => {
  const i18n = createI18n();
  i18n.setLanguage("my");
  assert.equal(
    i18n.translate("This document changed in another window. Reload it before saving."),
    "ဤဒေတာကို အခြား Window တစ်ခုတွင် ပြင်ဆင်ထားပါသည်။ မသိမ်းမီ ပြန်ဖွင့်ပါ။",
  );
  assert.equal(
    i18n.translate("This character changed in another window. Reload it before saving."),
    "ဤဇာတ်ကောင်ကို အခြား Window တစ်ခုတွင် ပြင်ဆင်ထားပါသည်။ မသိမ်းမီ ပြန်ဖွင့်ပါ။",
  );
  assert.equal(
    i18n.translate("Revision numbers come from the project-local durable ledger in desktop mode; browser mode keeps its local revision counter."),
    "Desktop mode တွင် Revision နံပါတ်များကို Project အတွင်းရှိ အမြဲတမ်း Ledger မှ ရယူပြီး Browser mode တွင် Browser ၏ Local Revision Counter ကို အသုံးပြုပါသည်။",
  );
  assert.equal(i18n.translate("SHOT 01"), "ရိုက်ကွက် 01");
  assert.equal(i18n.translate("3 shot(s)"), "3 ရိုက်ကွက်");
  assert.equal(i18n.translate("2 binding(s)"), "2 ချိတ်ဆက်မှု");
  assert.equal(
    i18n.translate("Revision 4 · SHA 0123456789ab…"),
    "ဗားရှင်း 4 · SHA 0123456789ab…",
  );
  assert.equal(
    i18n.translate("Could not bind character: Example"),
    "ဇာတ်ကောင်ချိတ်ဆက်၍ မရပါ: Example",
  );

  i18n.setLanguage("en");
  assert.equal(i18n.translate("ရိုက်ကွက် 01"), "SHOT 01");
  assert.equal(i18n.translate("3 ရိုက်ကွက်"), "3 shot(s)");
  assert.equal(i18n.translate("2 ချိတ်ဆက်မှု"), "2 binding(s)");
});
