(() => {
  "use strict";
  const STORAGE_KEY = "stilla.ui-language.v1";
  const dictionaries = {
    my: {
      "Projects":"ပရောဂျက်များ","Your work, organized in one place.":"သင့်အလုပ်များကို တစ်နေရာတည်းတွင် စုစည်းထားပါ။",
      "Script & Storyboard":"ဇာတ်ညွှန်းနှင့် Storyboard","Shape the story and review each scene before generating assets.":"မီဒီယာမဖန်တီးမီ ဇာတ်လမ်းပုံဖော်ပြီး Scene တစ်ခုချင်းစီကို စစ်ဆေးပါ။",
      "Generate":"ဖန်တီးရန်","Choose an available runtime and create assets as explicit, trackable jobs.":"အသုံးပြုနိုင်သော Runtime ကိုရွေးပြီး စောင့်ကြည့်နိုင်သည့် Job အဖြစ် ဖန်တီးပါ။",
      "Edit Studio":"တည်းဖြတ်ခန်း","Arrange clips, audio and captions in a focused editing workspace.":"Clip၊ အသံနှင့် စာတန်းများကို စနစ်တကျ စီစဉ်တည်းဖြတ်ပါ။",
      "Assets & History":"မီဒီယာနှင့် မှတ်တမ်း","Find imported media, generated results and prior job details.":"ထည့်သွင်းထားသော မီဒီယာ၊ ဖန်တီးပြီးရလဒ်နှင့် Job မှတ်တမ်းများကို ရှာပါ။",
      "Export":"ဖိုင်ထုတ်ရန်","Validate output settings before creating a final file.":"နောက်ဆုံးဖိုင်မထုတ်မီ Output ဆက်တင်များကို စစ်ဆေးပါ။",
      "Settings":"ဆက်တင်များ","Control appearance, language, local runtimes and data handling.":"အသွင်အပြင်၊ ဘာသာစကား၊ Local Runtime နှင့် ဒေတာကိုင်တွယ်မှုကို သတ်မှတ်ပါ။",
      "Character Creator":"ဇာတ်ကောင်ဖန်တီးရန်","Create original characters and preserve their identity across future stories.":"မူရင်းဇာတ်ကောင်များဖန်တီးပြီး နောက်ဇာတ်လမ်းများတွင်လည်း ပုံစံတူညီမှုကို ထိန်းသိမ်းပါ။",
      "WORKSPACE":"လုပ်ငန်းခွင်","LIBRARY":"စာကြည့်တိုက်","PREFERENCES":"စိတ်ကြိုက်သတ်မှတ်ချက်များ",
      "Untitled film":"အမည်မပေးရသေးသော ရုပ်ရှင်","Saved locally · prototype":"စက်တွင်းသိမ်းထားသည် · နမူနာ",
      "Prototype · no model connected":"နမူနာ · Model မချိတ်ဆက်ရသေးပါ","Queue":"လုပ်ငန်းတန်းစီမှု",
      "LOCAL-FIRST":"Local ကို ဦးစားပေး","Keep control of your work.":"သင့်အလုပ်ကို သင့်ထိန်းချုပ်မှုအောက်တွင်ထားပါ။",
      "Model, media and storage status will be explicit in the connected application.":"ချိတ်ဆက်ထားသော App တွင် Model၊ မီဒီယာနှင့် Storage အခြေအနေကို ရှင်းလင်းစွာ ပြသပါမည်။",
      "Recent Projects":"လတ်တလော ပရောဂျက်များ","RECENT PROJECTS":"လတ်တလော ပရောဂျက်များ","ASSETS":"မီဒီယာဖိုင်များ","TASK QUEUE":"လုပ်ငန်းတန်းစီမှု",
      "Illustrative sample":"နမူနာပြသချက်","Continue creating":"ဆက်လက်ဖန်တီးရန်","Demo data":"နမူနာဒေတာ",
      "Start with a workflow":"လုပ်ငန်းစဉ်တစ်ခုမှ စတင်ပါ","Plan a story":"ဇာတ်လမ်းအစီအစဉ်ဆွဲရန်",
      "Brief, script and storyboard":"အကျဉ်းချုပ်၊ ဇာတ်ညွှန်းနှင့် Storyboard","Create media":"မီဒီယာဖန်တီးရန်",
      "Model selection and generation jobs":"Model ရွေးချယ်ခြင်းနှင့် ဖန်တီးမှုလုပ်ငန်းများ",
      "Edit a video":"ဗီဒီယိုတည်းဖြတ်ရန်","Timeline, audio and captions":"Timeline၊ အသံနှင့် စာတန်းများ",
      "Prepare an export":"ဖိုင်ထုတ်ရန် ပြင်ဆင်ပါ","Output format and validation":"Output ပုံစံနှင့် စစ်ဆေးမှု",
      "Prototype only. Project counts, save states and recent items are not backed by persistent storage.":"နမူနာ UI သာဖြစ်သည်။ ပရောဂျက်အရေအတွက်၊ သိမ်းဆည်းမှုအခြေအနေနှင့် လတ်တလောစာရင်းများကို အမြဲတမ်း Storage တွင် မသိမ်းထားပါ။",
      "Scenes":"Scene များ","Reset sample":"နမူနာပြန်ထားရန်","Save draft":"Draft သိမ်းရန်",
      "Script draft":"ဇာတ်ညွှန်း Draft","Narration / scene description":"နောက်ခံပြောစကား / Scene ဖော်ပြချက်",
      "Target duration":"ရည်ရွယ်ထားသော ကြာချိန်","Visual mood":"မြင်ကွင်းအငွေ့အသက်","Aspect ratio":"ပုံအချိုး",
      "AI revisions must create a new version or explicit draft; never silently replace approved content.":"AI ပြင်ဆင်ချက်များကို Version အသစ် သို့မဟုတ် Draft အသစ်အဖြစ်သာ သိမ်းရမည်။ အတည်ပြုပြီးသားအကြောင်းအရာကို တိတ်တဆိတ် အစားမထိုးရပါ။",
      "Check runtime":"Runtime စစ်ဆေးရန်","Queue sample job":"နမူနာ Job တန်းစီရန်","Creation brief":"ဖန်တီးမှုအကျဉ်းချုပ်",
      "Output type":"Output အမျိုးအစား","Image / Video":"ပုံ / ဗီဒီယို","No model connected":"Model မချိတ်ဆက်ရသေးပါ",
      "Search assets…":"မီဒီယာရှာရန်…","Filter: All":"စစ်ထုတ်မှု: အားလုံး","Create asset":"မီဒီယာဖန်တီးရန်",
      "Project library":"ပရောဂျက်စာကြည့်တိုက်","Use in edit":"တည်းဖြတ်ရန် အသုံးပြုပါ","View job":"Job ကြည့်ရန်",
      "Retry flow":"လုပ်ငန်းစဉ် ပြန်စမ်းရန်","Output settings":"Output ဆက်တင်များ",
      "File name":"ဖိုင်အမည်","Container / codec preset":"ဖိုင်ပုံစံ / Codec Preset","Resolution":"Resolution",
      "Frame rate":"Frame Rate","Destination":"သိမ်းဆည်းမည့်နေရာ","Quality":"အရည်အသွေး",
      "Preflight checks":"မစတင်မီ စစ်ဆေးချက်များ","Validate settings":"ဆက်တင်စစ်ဆေးရန်",
      "Queue export":"ဖိုင်ထုတ်လုပ်ငန်း တန်းစီရန်","Appearance & language":"အသွင်အပြင်နှင့် ဘာသာစကား",
      "Theme":"အရောင်အသွင်အပြင်","Language":"ဘာသာစကား","English":"အင်္ဂလိပ်","Dark":"အမှောင်",
      "Light":"အလင်း","Motion":"လှုပ်ရှားမှု","Respect system preference":"စနစ်သတ်မှတ်ချက်အတိုင်း",
      "Reduced motion":"လှုပ်ရှားမှုလျှော့ရန်","Save preferences":"စိတ်ကြိုက်ဆက်တင် သိမ်းရန်",
      "Models & runtimes":"Model နှင့် Runtime များ","Local OpenAI-compatible endpoint":"Local OpenAI-compatible Endpoint",
      "Text model ID":"Text Model ID","Test connection":"ချိတ်ဆက်မှု စမ်းသပ်ရန်","Not tested":"မစမ်းသပ်ရသေးပါ",
      "Storage & privacy":"Storage နှင့် ကိုယ်ရေးလုံခြုံမှု","Project storage folder":"ပရောဂျက်သိမ်းဆည်းမည့် ဖိုင်တွဲ",
      "Performance & diagnostics":"စွမ်းဆောင်ရည်နှင့် စစ်ဆေးချက်များ","Hardware capability check":"Hardware စွမ်းဆောင်ရည်စစ်ဆေးရန်",
      "Dependency / license audit":"Dependency / License စစ်ဆေးရန်","Diagnostics":"စစ်ဆေးမှတ်တမ်းများ",
      "Character basics":"ဇာတ်ကောင်အခြေခံ","Original design":"မူရင်းဒီဇိုင်း","Character name":"ဇာတ်ကောင်အမည်",
      "Species / character type":"မျိုးစိတ် / ဇာတ်ကောင်အမျိုးအစား","Dialogue language":"စကားပြောဘာသာစကား",
      "Canonical seed":"သတ်မှတ်ထားသော Seed","VISUAL DNA":"ရုပ်သွင် DNA","Lock the appearance":"ရုပ်သွင်ကို တည်ငြိမ်စွာ သတ်မှတ်ပါ",
      "Identity anchors":"အထူးသတ်မှတ်လက္ခဏာများ","Silhouette":"အပြင်ပုံသဏ္ဌာန်","Body proportions":"ကိုယ်ခန္ဓာအချိုးအစား",
      "Face shape":"မျက်နှာပုံစံ","Eyes":"မျက်လုံး","Nose":"နှာခေါင်း","Mouth":"ပါးစပ်",
      "Primary colors":"အဓိကအရောင်များ","Surface / skin detail":"မျက်နှာပြင် / အရေပြားအသေးစိတ်",
      "Hair / head shape":"ဆံပင် / ဦးခေါင်းပုံစံ","Outfit":"ဝတ်စုံ","Accessories":"အသုံးအဆောင်များ",
      "Distinguishing marks":"ခွဲခြားသိနိုင်သော အမှတ်အသားများ","Art style":"အနုပညာပုံစံ",
      "Fixed features":"မပြောင်းလဲရမည့် လက္ခဏာများ","PERSONALITY DNA":"စရိုက် DNA",
      "Make the character memorable":"မှတ်မိလွယ်သော ဇာတ်ကောင်ဖြစ်အောင် ဖန်တီးပါ",
      "Personality archetype":"စရိုက်အမျိုးအစား","Core traits":"အဓိကစရိုက်လက္ခဏာများ",
      "Strength":"အားသာချက်","Comic flaw":"ဟာသဖြစ်စေသော အားနည်းချက်",
      "Humor mechanics":"ဟာသဖြစ်ပေါ်စေသည့် နည်းလမ်းများ","Speech pattern":"စကားပြောဟန်",
      "Catchphrase":"ထူးခြားသော ပြောစကား","Reaction style":"တုံ့ပြန်ပုံစံ",
      "Relationship dynamic":"ဆက်ဆံရေးပုံစံ","Running gag":"ထပ်ခါထပ်ခါ ပေါ်လာသော ဟာသ",
      "Avoid list":"ရှောင်ရန်စာရင်း","Voice description":"အသံဖော်ပြချက်",
      "REFERENCE IMAGES":"ကိုးကားပုံများ","Canonical visual references":"မူရင်းရုပ်သွင် ကိုးကားပုံများ",
      "＋ Add reference":"＋ ကိုးကားပုံထည့်ရန်","Character reference sheet":"ဇာတ်ကောင်ကိုးကား Sheet",
      "Generate sheet · unavailable":"Sheet ဖန်တီးရန် · မရနိုင်သေးပါ",
      "Reuse in Script & Storyboard":"ဇာတ်ညွှန်းနှင့် Storyboard တွင် ပြန်သုံးရန်",
      "Copy identity brief":"ဇာတ်ကောင်အချက်အလက် ကူးယူရန်","＋ New character":"＋ ဇာတ်ကောင်အသစ်",
      "Import bundle":"Bundle ထည့်သွင်းရန်","Export bundle":"Bundle ထုတ်ယူရန်","Delete":"ဖျက်ရန်",
      "Search characters…":"ဇာတ်ကောင်ရှာရန်…","No characters yet. Create an original character to begin your library.":"ဇာတ်ကောင်မရှိသေးပါ။ စာကြည့်တိုက်စတင်ရန် မူရင်းဇာတ်ကောင်တစ်ခု ဖန်တီးပါ။",
      "Changes are drafts until saved.":"မသိမ်းမချင်း ပြောင်းလဲမှုများသည် Draft အဖြစ်သာ ရှိနေပါမည်။",
      "Save character":"ဇာတ်ကောင်သိမ်းရန်","Save new revision":"Revision အသစ်သိမ်းရန်",
      "Add reference":"ကိုးကားပုံထည့်ရန်","Remove":"ဖယ်ရှားရန်",
      "Local browser prototype":"Browser ထဲရှိ နမူနာ","Your cast":"သင့်ဇာတ်ကောင်များ",
      "Character Library":"ဇာတ်ကောင်စာကြည့်တိုက်","No refs":"ကိုးကားပုံမရှိ",
      "Refs saved":"ကိုးကားပုံ သိမ်းထားသည်","Original comedy":"မူရင်းဟာသဇာတ်ကောင်",
      "Reference images":"ကိုးကားပုံများ","Identity anchors":"အထူးသတ်မှတ်လက္ခဏာများ",
      "Background tasks":"နောက်ကွယ်လုပ်ငန်းများ","Task queue":"လုပ်ငန်းတန်းစီမှု",
      "Paused":"ခေတ္တရပ်ထားသည်","Ready":"အသင့်ဖြစ်သည်","Storyboard frames":"Storyboard Frame များ",
      "Project autosave":"ပရောဂျက် အလိုအလျောက်သိမ်းဆည်းမှု","Dismiss sample":"နမူနာပိတ်ရန်",
      "Import media":"မီဒီယာထည့်သွင်းရန်","New project":"ပရောဂျက်အသစ်",
      "Wide shot · 8 sec":"မြင်ကွင်းကျယ် · ၈ စက္ကန့်","Close-up · 12 sec":"အနီးကပ် · ၁၂ စက္ကန့်",
      "Medium shot · 10 sec":"အလယ်အလတ်မြင်ကွင်း · ၁၀ စက္ကန့်",
      "Warm, natural light":"နွေးထွေးသော သဘာဝအလင်း","Cinematic, high contrast":"ရုပ်ရှင်ဆန်ပြီး အလင်းအမှောင်ကွာခြားမှုမြင့်",
      "Documentary realism":"မှတ်တမ်းရုပ်ရှင်ဆန်သော လက်တွေ့ပုံစံ","Soft illustration":"နူးညံ့သော သရုပ်ဖော်ပုံ",
      "16:9 — landscape":"16:9 — အလျားလိုက်","9:16 — vertical":"9:16 — ဒေါင်လိုက်","1:1 — square":"1:1 — စတုရန်း"
    }
  };
  const reverse = {};
  for (const [key, value] of Object.entries(dictionaries.my)) reverse[value] = key;
  let language = "en";
  let observer = null;
  const translate = (value) => {
    const source = String(value ?? "");
    const trimmed = source.trim();
    const leading = source.match(/^\s*/)?.[0] || "";
    const trailing = source.match(/\s*$/)?.[0] || "";
    const key = language === "my" ? trimmed : (reverse[trimmed] || trimmed);
    const result = language === "my" ? (dictionaries.my[key] || trimmed) : key;
    return leading + result + trailing;
  };
  const translateElement = (root) => {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    for (const node of nodes) {
      if (!node.nodeValue.trim()) continue;
      const translated = translate(node.nodeValue);
      if (translated !== node.nodeValue) node.nodeValue = translated;
    }
    const elements = root.querySelectorAll ? root.querySelectorAll("*") : [];
    for (const el of elements) {
      for (const attr of ["placeholder", "aria-label", "title"]) {
        if (el.hasAttribute(attr)) {
          const value = el.getAttribute(attr);
          const next = translate(value);
          if (next !== value) el.setAttribute(attr, next);
        }
      }
    }
  };
  const apply = () => {
    document.documentElement.lang = language;
    translateElement(document.body);
    const quick = document.getElementById("languageQuick");
    const settings = document.getElementById("language");
    if (quick) quick.value = language;
    if (settings) settings.value = language;
    try { localStorage.setItem(STORAGE_KEY, language); } catch { /* storage may be disabled */ }
  };
  const setLanguage = (value) => {
    language = value === "my" ? "my" : "en";
    apply();
  };
  const init = () => {
    try { language = localStorage.getItem(STORAGE_KEY) === "my" ? "my" : "en"; }
    catch { language = "en"; }
    const quick = document.getElementById("languageQuick");
    if (quick) quick.addEventListener("change", () => setLanguage(quick.value));
    if (observer) observer.disconnect();
    observer = new MutationObserver((records) => {
      for (const record of records) {
        if (record.type === "childList") {
          for (const node of record.addedNodes) {
            if (node.nodeType === Node.ELEMENT_NODE) translateElement(node);
            else if (node.nodeType === Node.TEXT_NODE && node.nodeValue.trim()) {
              const next = translate(node.nodeValue);
              if (next !== node.nodeValue) node.nodeValue = next;
            }
          }
        } else if (record.type === "characterData" && record.target.nodeValue.trim()) {
          const next = translate(record.target.nodeValue);
          if (next !== record.target.nodeValue) record.target.nodeValue = next;
        }
      }
    });
    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
    apply();
  };
  window.STILLAI18N = { init, setLanguage, getLanguage: () => language, translate };
})();