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
      "Scenes":"Scene များ",
      "M7F / VERSIONED CHARACTER BINDING":"M7F / ဗားရှင်းလိုက် ဇာတ်ကောင်ချိတ်ဆက်မှု",
      "Unsaved changes are local to this view":"မသိမ်းရသေးသော ပြောင်းလဲမှုများသည် ဤမြင်ကွင်းအတွင်းသာ ရှိနေပါသည်။",
      "Describe the action in this shot.":"ဤရိုက်ကွက်အတွင်း လုပ်ဆောင်ချက်ကို ဖော်ပြပါ။",
      "Storyboard unavailable":"Storyboard ကို ဖွင့်၍မရပါ။",
      "Saved storyboard data is invalid JSON. Existing data was preserved; no replacement was made.":"သိမ်းထားသော Storyboard ဒေတာ၏ JSON ပုံစံ မမှန်ပါ။ မူလဒေတာကို မပြောင်းလဲဘဲ ထိန်းသိမ်းထားပါသည်။",
      "Saved storyboard data has an invalid structure. Existing data was preserved; no replacement was made.":"သိမ်းထားသော Storyboard ဒေတာဖွဲ့စည်းပုံ မမှန်ပါ။ မူလဒေတာကို မပြောင်းလဲဘဲ ထိန်းသိမ်းထားပါသည်။",
      "Saved storyboard data failed validation. Existing data was preserved; no replacement was made.":"သိမ်းထားသော Storyboard ဒေတာ စစ်ဆေးမှု မအောင်မြင်ပါ။ မူလဒေတာကို မပြောင်းလဲဘဲ ထိန်းသိမ်းထားပါသည်။",
      "Character binding":"ဇာတ်ကောင်ချိတ်ဆက်မှု","Select or create a project before editing its storyboard.":"Storyboard မပြင်ဆင်မီ ပရောဂျက်တစ်ခုကို ရွေးချယ်ပါ သို့မဟုတ် အသစ်ဖန်တီးပါ။","Storyboard data could not be loaded.":"Storyboard ဒေတာကို ဖွင့်၍မရပါ။","Loading storyboard and project characters…":"Storyboard နှင့် ပရောဂျက်ဇာတ်ကောင်များကို ဖွင့်နေသည်…","Scene description":"မြင်ကွင်းဖော်ပြချက်","Duration (seconds)":"ကြာချိန် (စက္ကန့်)","Camera":"ကင်မရာ","Pin character revision":"ဇာတ်ကောင် Revision ကို ချိတ်ပါ","Choose a saved character…":"သိမ်းထားသော ဇာတ်ကောင်ကို ရွေးပါ…","Bind to shot":"Shot နှင့် ချိတ်ပါ","Unbind":"ချိတ်ဆက်မှုဖြုတ်ရန်","Remove":"ဖယ်ရှားရန်","Storyboard character consistency":"Storyboard ဇာတ်ကောင်ပုံစံ တစ်သမတ်တည်းဖြစ်မှု","Pin an exact character profile revision to each shot. Historical snapshots remain embedded in the saved storyboard.":"Shot တစ်ခုချင်းစီတွင် သတ်မှတ်ထားသော Character Profile Revision ကို ချိတ်ဆက်ပါ။ ယခင် Snapshot များကို သိမ်းဆည်းထားသော Storyboard ထဲတွင် ထိန်းသိမ်းထားပါမည်။","＋ Add shot":"＋ Shot ထည့်ရန်","Save storyboard":"Storyboard သိမ်းရန်","Saved to this project":"ဤပရောဂျက်တွင် သိမ်းပြီးပါပြီ","Storyboard saved":"Storyboard သိမ်းပြီးပါပြီ","No saved characters in this project. Create a character in Character Creator first.":"ဤပရောဂျက်တွင် သိမ်းထားသော ဇာတ်ကောင်မရှိပါ။ Character Creator တွင် အရင်ဖန်တီးပါ။","No character is pinned to this shot.":"ဤ Shot တွင် ဇာတ်ကောင်မချိတ်ဆက်ရသေးပါ။","No shots yet. Add a shot to start binding characters.":"Shot မရှိသေးပါ။ ဇာတ်ကောင်ချိတ်ဆက်ရန် Shot တစ်ခုထည့်ပါ။","Revision numbers are based on the local character library and embedded snapshots. A durable revision ledger remains future work.":"Revision နံပါတ်များသည် Local Character Library နှင့် Snapshot များအပေါ် အခြေခံထားသည်။ အမြဲတမ်း Revision Ledger ကို နောက်အဆင့်တွင် ဆောင်ရွက်ပါမည်။","Every shot needs a scene description.":"Shot တိုင်းတွင် မြင်ကွင်းဖော်ပြချက် လိုအပ်သည်။","Choose a saved character before binding.":"မချိတ်ဆက်မီ သိမ်းထားသော ဇာတ်ကောင်ကို ရွေးပါ။","Selected character is not available in this project.":"ရွေးချယ်ထားသော ဇာတ်ကောင်ကို ဤပရောဂျက်တွင် မတွေ့ပါ။","Shot duration must be between 0 and 86400 seconds.":"Shot ကြာချိန်သည် ၀ မှ ၈၆၄၀၀ စက္ကန့်အတွင်း ဖြစ်ရပါမည်။","Binding updated · save storyboard to persist":"ချိတ်ဆက်မှု ပြင်ဆင်ပြီးပါပြီ · သိမ်းရန် Storyboard ကို Save လုပ်ပါ။","Binding removed · save storyboard to persist":"ချိတ်ဆက်မှု ဖြုတ်ပြီးပါပြီ · သိမ်းရန် Storyboard ကို Save လုပ်ပါ။","Reset sample":"နမူနာပြန်ထားရန်","Save draft":"Draft သိမ်းရန်",
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
      "16:9 — landscape":"16:9 — အလျားလိုက်","9:16 — vertical":"9:16 — ဒေါင်လိုက်","1:1 — square":"1:1 — စတုရန်း",
      "Sample jobs only. No model or export process is running.":"နမူနာ Job များသာဖြစ်သည်။ Model သို့မဟုတ် Export လုပ်ငန်း မလည်ပတ်ပါ။",
      "Local image runtime unavailable in prototype":"နမူနာတွင် Local Image Runtime မရနိုင်သေးပါ။",
      "Illustrative status only":"အခြေအနေကို နမူနာပြသခြင်းသာ ဖြစ်သည်။",
      "Task states must come from real workers.":"လုပ်ငန်းအခြေအနေများကို တကယ့် Worker များထံမှသာ ရယူရမည်။",
      "Last edited just now · 3 scenes · 00:42":"ယခုလေးတင် ပြင်ဆင်ထားသည် · Scene ၃ ခု · 00:42",
      "Morning in the city":"မြို့၏ နံနက်ခင်း",
      "Script draft · 6 scenes":"ဇာတ်ညွှန်း Draft · Scene ၆ ခု",
      "Visual mood exploration":"ရုပ်ပုံအငွေ့အသက် စမ်းသပ်မှု",
      "2 sample jobs · no real outputs":"နမူနာ Job ၂ ခု · တကယ့် Output မရှိပါ",
      "One unavailable runtime":"အသုံးမပြုနိုင်သေးသော Runtime တစ်ခု",
      "Scene list is sample data; reorder is not implemented yet.":"Scene စာရင်းသည် နမူနာဒေတာဖြစ်သည်။ အစီအစဉ်ပြန်စီခြင်း မထည့်သွင်းရသေးပါ။",
      "Version 1":"Version ၁","Unsaved sample text":"မသိမ်းဆည်းရသေးသော နမူနာစာသား",
      "Add scene note":"Scene မှတ်ချက်ထည့်ရန်","Scene note added to this prototype view.":"ဤနမူနာမြင်ကွင်းတွင် Scene မှတ်ချက် ထည့်ပြီးပါပြီ။",
      "Scene properties":"Scene ဂုဏ်သတ္တိများ","8 seconds":"၈ စက္ကန့်","12 seconds":"၁၂ စက္ကန့်",
      "15 seconds":"၁၅ စက္ကန့်","30 seconds":"၃၀ စက္ကန့်",
      "Still image":"ငြိမ်ပုံ","Video clip":"ဗီဒီယို Clip",
      "Prompt":"Prompt","Local model / runtime":"Local Model / Runtime",
      "Not detected — choose after runtime check":"မတွေ့ရှိပါ — Runtime စစ်ဆေးပြီးမှ ရွေးပါ",
      "Text planning · Bionic/Qwen (connection unverified)":"Text Planning · Bionic/Qwen (ချိတ်ဆက်မှု အတည်မပြုရသေးပါ)",
      "Image runtime · not configured":"Image Runtime · မသတ်မှတ်ရသေးပါ",
      "Video runtime · not configured":"Video Runtime · မသတ်မှတ်ရသေးပါ",
      "No model is connected in this prototype. Hardware fit, installed model availability and supported controls must be checked before a real job starts.":"ဤနမူနာတွင် Model မချိတ်ဆက်ရသေးပါ။ တကယ့် Job မစတင်မီ Hardware ကိုက်ညီမှု၊ ထည့်သွင်းထားသော Model ရရှိမှုနှင့် ပံ့ပိုးသော Controls များကို စစ်ဆေးရမည်။",
      "Result preview":"ရလဒ် Preview","Placeholder":"နေရာယူပြသချက်","Creation preview":"ဖန်တီးမှု Preview",
      "Generated output will appear here":"ဖန်တီးပြီး Output ကို ဤနေရာတွင် ပြသပါမည်","No output file exists":"Output ဖိုင် မရှိသေးပါ",
      "View assets":"မီဒီယာများ ကြည့်ရန်","RUNTIME":"RUNTIME","HARDWARE":"HARDWARE",
      "Capability check pending":"စွမ်းဆောင်ရည်စစ်ဆေးရန် ကျန်ရှိသည်","TASK CONTROL":"လုပ်ငန်းထိန်းချုပ်မှု",
      "Queue / cancel / retry":"တန်းစီ / ပယ်ဖျက် / ပြန်စမ်း","Only illustrative controls here; no worker is launched.":"ဤနေရာတွင် နမူနာ Controls များသာ ရှိသည်။ Worker မစတင်ထားပါ။",
      "Undo":"နောက်ပြန်","Redo":"ပြန်လုပ်","Open Export →":"Export ဖွင့်ရန် →",
      "Media bin":"မီဒီယာဖိုင်တွဲ","Video · 00:08":"ဗီဒီယို · 00:08","Audio · 00:42":"အသံ · 00:42",
      "Subtitle file":"စာတန်းဖိုင်","Sample media names only. No media files are bundled.":"မီဒီယာအမည် နမူနာများသာဖြစ်သည်။ မီဒီယာဖိုင်များ မပါဝင်ပါ။",
      "Preview monitor":"Preview Monitor","Timeline preview":"Timeline Preview","00:00:12:08 · paused":"00:00:12:08 · ရပ်ထားသည်",
      "▶ Play sample":"▶ နမူနာဖွင့်ရန်","00:42 total":"စုစုပေါင်း 00:42","Inspector":"စစ်ဆေးရန်",
      "Clip selected":"Clip ရွေးထားသည်","Clip name":"Clip အမည်","Speed":"အမြန်နှုန်း","Audio gain":"အသံအတိုးအကျယ်",
      "Real editing requires an engine adapter and atomic, undoable timeline operations.":"တကယ့်တည်းဖြတ်မှုအတွက် Engine Adapter နှင့် နောက်ပြန်လုပ်နိုင်သော Atomic Timeline လုပ်ဆောင်ချက်များ လိုအပ်သည်။",
      "Timeline":"Timeline","VIDEO 1":"ဗီဒီယို ၁","AUDIO 1":"အသံ ၁","CAPTIONS":"စာတန်းများ",
      "Caption 01":"စာတန်း ၀၁","Caption 02":"စာတန်း ၀၂","Caption 03":"စာတန်း ၀၃",
      "Imported video · Untitled film · 00:08":"ထည့်သွင်းထားသော ဗီဒီယို · အမည်မပေးရသေးသော ရုပ်ရှင် · 00:08",
      "Illustrative generation record · prompt unavailable":"နမူနာဖန်တီးမှုမှတ်တမ်း · Prompt မရနိုင်ပါ",
      "Job history · runtime unavailable":"Job မှတ်တမ်း · Runtime မရနိုင်ပါ",
      "Real provenance should preserve source, model/runtime version, prompt/settings when available, and job outcome without inventing missing metadata.":"တကယ့် Provenance တွင် Source၊ Model/Runtime Version၊ ရရှိနိုင်ပါက Prompt/Settings နှင့် Job ရလဒ်တို့ကို ထိန်းသိမ်းရမည်။ မရှိသော Metadata ကို မဖန်တီးရပါ။",
      "MP4 · H.264 · compatible":"MP4 · H.264 · ကိုက်ညီသောပုံစံ",
      "WebM · VP9 (engine support required)":"WebM · VP9 (Engine ပံ့ပိုးမှုလိုအပ်သည်)",
      "ProRes (engine support required)":"ProRes (Engine ပံ့ပိုးမှုလိုအပ်သည်)",
      "1080 × 1920 vertical":"1080 × 1920 ဒေါင်လိုက်","Balanced":"မျှတသောအရည်အသွေး",
      "High quality":"အရည်အသွေးမြင့်","Smaller file":"ဖိုင်အရွယ်အစားသေး",
      "Validation required: no actual media, output path or rendering engine is connected.":"စစ်ဆေးရန်လိုအပ်သည်။ တကယ့်မီဒီယာ၊ Output Path သို့မဟုတ် Rendering Engine မချိတ်ဆက်ရသေးပါ။",
      "Not verified":"အတည်မပြုရသေးပါ","Source media":"မူရင်းမီဒီယာ",
      "Missing-media scan not implemented":"မီဒီယာပျောက်ဆုံးမှု စစ်ဆေးခြင်း မထည့်သွင်းရသေးပါ",
      "Export destination":"Export သိမ်းဆည်းမည့်နေရာ","No filesystem permission in prototype":"နမူနာတွင် Filesystem ခွင့်ပြုချက်မရှိပါ",
      "Codec support":"Codec ပံ့ပိုးမှု","Must reflect installed engine":"ထည့်သွင်းထားသော Engine အခြေအနေအတိုင်း ဖြစ်ရမည်",
      "Disk space":"Disk နေရာလွတ်","Not detectable here":"ဤနေရာမှ မသိရှိနိုင်ပါ",
      "A completed job must verify that the output file exists and can be inspected. Never report success just because a process returned.":"ပြီးဆုံးသော Job တစ်ခုတွင် Output ဖိုင်ရှိကြောင်းနှင့် ဖွင့်စစ်ဆေးနိုင်ကြောင်း အတည်ပြုရမည်။ Process ပြီးဆုံးရုံဖြင့် အောင်မြင်သည်ဟု မကြေညာရပါ။",
      "RTX 3050 6 GB / 16 GB RAM target profile":"RTX 3050 6 GB / 16 GB RAM ရည်မှန်းထားသော Hardware",
      "Required before bundling engines":"Engine များ ထည့်သွင်းမထုပ်ပိုးမီ လိုအပ်သည်",
      "Logs should redact prompts, secrets and local paths where appropriate":"Log များတွင် Prompt၊ Secret နှင့် Local Path များကို သင့်လျော်သလို ဖုံးကွယ်ရမည်",
      "Design":"ဒီဇိုင်း","Not run":"မစစ်ဆေးရသေးပါ","Pending":"စောင့်ဆိုင်းနေသည်",
      "A unique name used in stories and the library.":"ဇာတ်လမ်းများနှင့် စာကြည့်တိုက်တွင် အသုံးပြုမည့် သီးသန့်အမည်။",
      "Examples: en, my, th, ja":"ဥပမာ - en, my",
      "Optional unsigned 32-bit seed; only applied when supported.":"ရွေးချယ်နိုင်သော 32-bit Seed ဖြစ်သည်။ ပံ့ပိုးသောအခါမှသာ အသုံးပြုမည်။",
      "Overall outline and recognizable shape.":"အလုံးစုံအပြင်ပုံနှင့် ခွဲခြားသိနိုင်သော ပုံသဏ္ဌာန်။",
      "Head/body ratio, limb length, build.":"ဦးခေါင်းနှင့် ကိုယ်ခန္ဓာအချိုး၊ ခြေလက်အရှည်နှင့် ကိုယ်ထည်ဖွဲ့စည်းပုံ။",
      "Shape, size, spacing, color.":"ပုံစံ၊ အရွယ်အစား၊ အကွာအဝေးနှင့် အရောင်။",
      "Comma-separated color names.":"ကော်မာဖြင့် ခွဲရေးထားသော အရောင်အမည်များ။",
      "Comma-separated; keep stable.":"ကော်မာဖြင့် ခွဲရေးပါ။ ပုံစံတည်ငြိမ်စွာ ထိန်းထားပါ။",
      "Scars, spots, patterns, etc.":"အမာရွတ်၊ အစက်အပြောက်၊ ပုံစံများ စသည်။",
      "Default canonical costume.":"မူရင်းအမြဲတမ်းဝတ်စုံ။",
      "Features that must never change.":"မည်သည့်အခါမျှ မပြောင်းလဲရမည့် လက္ခဏာများ။",
      "Comma-separated traits.":"ကော်မာဖြင့် ခွဲရေးထားသော စရိုက်လက္ခဏာများ။",
      "A lovable weakness that drives original situations.":"စိတ်ဝင်စားဖွယ် မူရင်းအခြေအနေများ ဖြစ်ပေါ်စေသော ချစ်စရာအားနည်းချက်။",
      "e.g. overconfidence, visual timing, harmless misunderstandings.":"ဥပမာ - ကိုယ့်ကိုယ်ကို ယုံကြည်လွန်ခြင်း၊ အချိန်ကိုက်ဟာသ၊ အန္တရာယ်မရှိသော နားလည်မှုလွဲခြင်း။",
      "Voice design only; no voice model is generated here.":"အသံပုံစံဖော်ပြချက်သာ ဖြစ်သည်။ ဤနေရာတွင် Voice Model မဖန်တီးပါ။",
      "Import approved images to help preserve identity. Use front, side, back and expression views where available.":"ဇာတ်ကောင်ပုံစံတူညီမှု ထိန်းသိမ်းရန် အတည်ပြုထားသော ကိုးကားပုံများ ထည့်ပါ။ ရှေ့၊ ဘေး၊ နောက်နှင့် မျက်နှာအမူအရာပုံများ အသုံးပြုနိုင်သည်။",
      "Turnaround / expression sheet generation will be enabled after a verified local image workflow adapter is connected.":"Local Image Workflow Adapter ကို စမ်းသပ်အတည်ပြုပြီး ချိတ်ဆက်ပြီးမှ Turnaround / Expression Sheet ဖန်တီးမှုကို ဖွင့်ပါမည်။",
      "Build original characters once, preserve their visual DNA and reuse them in future stories.":"မူရင်းဇာတ်ကောင်ကို တစ်ကြိမ်ဖန်တီးပြီး ရုပ်သွင် DNA ကို ထိန်းသိမ်းကာ နောက်ဇာတ်လမ်းများတွင် ပြန်သုံးပါ။",
      "Profiles and small reference previews are saved in this browser only. Export a bundle to back up or move a character. This is not yet connected to project-folder storage or ComfyUI reference conditioning.":"Profile နှင့် ကိုးကားပုံ Preview များကို ဤ Browser ထဲတွင်သာ သိမ်းထားသည်။ Backup ပြုလုပ်ရန် သို့မဟုတ် အခြားနေရာသို့ ရွှေ့ရန် Bundle ထုတ်ယူပါ။ Project Folder Storage သို့မဟုတ် ComfyUI Reference Conditioning နှင့် မချိတ်ဆက်ရသေးပါ။",
      "Each save creates a revision. Deletion requires confirmation.":"သိမ်းဆည်းမှုတိုင်းသည် Revision အသစ်ဖန်တီးသည်။ ဖျက်ရန် အတည်ပြုချက်လိုအပ်သည်။",
      "The selected profile can be exported as a validated M7a-compatible JSON bundle. Storyboard binding is a later integration step.":"ရွေးချယ်ထားသော Profile ကို M7a နှင့် ကိုက်ညီသည့် JSON Bundle အဖြစ် ထုတ်ယူနိုင်သည်။ Storyboard ချိတ်ဆက်မှုကို နောက်အဆင့်တွင် ဆောင်ရွက်မည်။",
      "Image stored in project bundle":"Project Bundle ထဲတွင် ပုံသိမ်းထားသည်",
      "Could not import character bundle: ":"Character Bundle ထည့်သွင်း၍ မရပါ: ",
      "Please enter a character name.":"ဇာတ်ကောင်အမည် ထည့်သွင်းပါ။",
      "A character can have up to 20 reference images.":"ဇာတ်ကောင်တစ်ခုလျှင် ကိုးကားပုံ အများဆုံး ၂၀ ပုံ ထည့်နိုင်သည်။",
      "Save the character first, then add reference images.":"ကိုးကားပုံမထည့်မီ ဇာတ်ကောင်ကို အရင်သိမ်းဆည်းပါ။",
      "Only PNG, JPEG and WebP reference images are supported.":"PNG၊ JPEG နှင့် WebP ကိုးကားပုံများကိုသာ ပံ့ပိုးသည်။",
      "Delete this character from this browser library? Export a backup first if needed.":"ဤ Browser စာကြည့်တိုက်မှ ဇာတ်ကောင်ကို ဖျက်မည်လား။ လိုအပ်ပါက Backup ကို အရင်ထုတ်ယူပါ။",
      "Identity brief copied.":"ဇာတ်ကောင်အချက်အလက်ကို ကူးယူပြီးပါပြီ။",
      "This prototype does not make network requests. Connection testing will be implemented in the desktop application.":"ဤနမူနာသည် Network Request မပြုလုပ်ပါ။ Desktop Application တွင် ချိတ်ဆက်မှုစမ်းသပ်ခြင်းကို ထည့်သွင်းမည်။",
      "Theme is interactive. Other preferences are sample form values and are not persisted.":"Theme ကို ပြောင်းလဲနိုင်သည်။ အခြားစိတ်ကြိုက်တန်ဖိုးများသည် နမူနာသာဖြစ်ပြီး အမြဲတမ်းမသိမ်းဆည်းပါ။",
      "Never move or delete existing model files automatically. Local/remote selection and data disclosure must be explicit.":"ရှိပြီးသား Model ဖိုင်များကို အလိုအလျောက် မရွှေ့ပါနှင့်၊ မဖျက်ပါနှင့်။ Local/Remote ရွေးချယ်မှုနှင့် ဒေတာပေးပို့မှုကို အသုံးပြုသူက အတိအလင်း အတည်ပြုရမည်။"
,
      "A unique name used in stories and the library.":"ဇာတ်လမ်းများနှင့် စာကြည့်တိုက်တွင် အသုံးပြုမည့် သီးသန့်အမည်။",
      "Examples: en, my, th, ja":"ဥပမာ - en, my",
      "Optional unsigned 32-bit seed; only applied when supported.":"ရွေးချယ်နိုင်သော 32-bit Seed ဖြစ်သည်။ ပံ့ပိုးသောအခါမှသာ အသုံးပြုမည်။",
      "Overall outline and recognizable shape.":"အလုံးစုံအပြင်ပုံနှင့် ခွဲခြားသိနိုင်သော ပုံသဏ္ဌာန်။",
      "Head/body ratio, limb length, build.":"ဦးခေါင်းနှင့် ကိုယ်ခန္ဓာအချိုး၊ ခြေလက်အရှည်နှင့် ကိုယ်ထည်ဖွဲ့စည်းပုံ။",
      "Shape, size, spacing, color.":"ပုံစံ၊ အရွယ်အစား၊ အကွာအဝေးနှင့် အရောင်။",
      "Comma-separated color names.":"ကော်မာဖြင့် ခွဲရေးထားသော အရောင်အမည်များ။",
      "Comma-separated; keep stable.":"ကော်မာဖြင့် ခွဲရေးပါ။ ပုံစံတည်ငြိမ်စွာ ထိန်းထားပါ။",
      "Scars, spots, patterns, etc.":"အမာရွတ်၊ အစက်အပြောက်၊ ပုံစံများ စသည်။",
      "Default canonical costume.":"မူရင်းအမြဲတမ်းဝတ်စုံ။",
      "Features that must never change.":"မည်သည့်အခါမျှ မပြောင်းလဲရမည့် လက္ခဏာများ။",
      "Comma-separated traits.":"ကော်မာဖြင့် ခွဲရေးထားသော စရိုက်လက္ခဏာများ။",
      "A lovable weakness that drives original situations.":"စိတ်ဝင်စားဖွယ် မူရင်းအခြေအနေများ ဖြစ်ပေါ်စေသော ချစ်စရာအားနည်းချက်။",
      "e.g. overconfidence, visual timing, harmless misunderstandings.":"ဥပမာ - ကိုယ့်ကိုယ်ကို ယုံကြည်လွန်ခြင်း၊ အချိန်ကိုက်ဟာသ၊ အန္တရာယ်မရှိသော နားလည်မှုလွဲခြင်း။",
      "Voice design only; no voice model is generated here.":"အသံပုံစံဖော်ပြချက်သာ ဖြစ်သည်။ ဤနေရာတွင် Voice Model မဖန်တီးပါ။",
      "Import approved images to help preserve identity. Use front, side, back and expression views where available.":"ဇာတ်ကောင်ပုံစံတူညီမှု ထိန်းသိမ်းရန် အတည်ပြုထားသော ကိုးကားပုံများ ထည့်ပါ။ ရှေ့၊ ဘေး၊ နောက်နှင့် မျက်နှာအမူအရာပုံများ အသုံးပြုနိုင်သည်။",
      "Turnaround / expression sheet generation will be enabled after a verified local image workflow adapter is connected.":"Local Image Workflow Adapter ကို စမ်းသပ်အတည်ပြုပြီး ချိတ်ဆက်ပြီးမှ Turnaround / Expression Sheet ဖန်တီးမှုကို ဖွင့်ပါမည်။",
      "Build original characters once, preserve their visual DNA and reuse them in future stories.":"မူရင်းဇာတ်ကောင်ကို တစ်ကြိမ်ဖန်တီးပြီး ရုပ်သွင် DNA ကို ထိန်းသိမ်းကာ နောက်ဇာတ်လမ်းများတွင် ပြန်သုံးပါ။",
      "Profiles and small reference previews are saved in this browser only. Export a bundle to back up or move a character. This is not yet connected to project-folder storage or ComfyUI reference conditioning.":"Profile နှင့် ကိုးကားပုံ Preview များကို ဤ Browser ထဲတွင်သာ သိမ်းထားသည်။ Backup ပြုလုပ်ရန် သို့မဟုတ် အခြားနေရာသို့ ရွှေ့ရန် Bundle ထုတ်ယူပါ။ Project Folder Storage သို့မဟုတ် ComfyUI Reference Conditioning နှင့် မချိတ်ဆက်ရသေးပါ။",
      "Each save creates a revision. Deletion requires confirmation.":"သိမ်းဆည်းမှုတိုင်းသည် Revision အသစ်ဖန်တီးသည်။ ဖျက်ရန် အတည်ပြုချက်လိုအပ်သည်။",
      "The selected profile can be exported as a validated M7a-compatible JSON bundle. Storyboard binding is a later integration step.":"ရွေးချယ်ထားသော Profile ကို M7a နှင့် ကိုက်ညီသည့် JSON Bundle အဖြစ် ထုတ်ယူနိုင်သည်။ Storyboard ချိတ်ဆက်မှုကို နောက်အဆင့်တွင် ဆောင်ရွက်မည်။",
      "Character reference sheet":"ဇာတ်ကောင်ကိုးကား Sheet",
      "Please enter a character name.":"ဇာတ်ကောင်အမည် ထည့်သွင်းပါ။",
      "A character can have up to 20 reference images.":"ဇာတ်ကောင်တစ်ခုလျှင် ကိုးကားပုံ အများဆုံး ၂၀ ပုံ ထည့်နိုင်သည်။",
      "Save the character first, then add reference images.":"ကိုးကားပုံမထည့်မီ ဇာတ်ကောင်ကို အရင်သိမ်းဆည်းပါ။",
      "Only PNG, JPEG and WebP reference images are supported.":"PNG၊ JPEG နှင့် WebP ကိုးကားပုံများကိုသာ ပံ့ပိုးသည်။",
      "Delete this character from this browser library? Export a backup first if needed.":"ဤ Browser စာကြည့်တိုက်မှ ဇာတ်ကောင်ကို ဖျက်မည်လား။ လိုအပ်ပါက Backup ကို အရင်ထုတ်ယူပါ။",
      "Identity brief copied.":"ဇာတ်ကောင်အချက်အလက်ကို ကူးယူပြီးပါပြီ။",
      "Could not import character bundle: ":"Character Bundle ထည့်သွင်း၍ မရပါ: ",
      "Could not save character: ":"ဇာတ်ကောင်သိမ်း၍ မရပါ: ",
      "Changes are drafts until saved.":"မသိမ်းမချင်း ပြောင်းလဲမှုများသည် Draft အဖြစ်သာ ရှိနေပါမည်။",
      "This prototype does not make network requests. Connection testing will be implemented in the desktop application.":"ဤနမူနာသည် Network Request မပြုလုပ်ပါ။ Desktop Application တွင် ချိတ်ဆက်မှုစမ်းသပ်ခြင်းကို ထည့်သွင်းမည်။",
      "Theme is interactive. Other preferences are sample form values and are not persisted.":"Theme ကို ပြောင်းလဲနိုင်သည်။ အခြားစိတ်ကြိုက်တန်ဖိုးများသည် နမူနာသာဖြစ်ပြီး အမြဲတမ်းမသိမ်းဆည်းပါ။",
      "Never move or delete existing model files automatically. Local/remote selection and data disclosure must be explicit.":"ရှိပြီးသား Model ဖိုင်များကို အလိုအလျောက် မရွှေ့ပါနှင့်၊ မဖျက်ပါနှင့်။ Local/Remote ရွေးချယ်မှုနှင့် ဒေတာပေးပို့မှုကို အသုံးပြုသူက အတိအလင်း အတည်ပြုရမည်။",
      "This prototype does not make network requests.":"ဤနမူနာသည် Network Request မပြုလုပ်ပါ။",
      "Not connected":"မချိတ်ဆက်ထားပါ",
      "Choose a local folder…":"စက်တွင်း Folder ရွေးပါ…",
      "No destination is selected in this browser prototype.":"ဤ Browser နမူနာတွင် သိမ်းဆည်းမည့်နေရာ မရွေးချယ်ရသေးပါ။",
      "No actual media, output path or rendering engine is connected.":"တကယ့်မီဒီယာ၊ Output Path သို့မဟုတ် Rendering Engine မချိတ်ဆက်ရသေးပါ။",
      "Project does not exist":"ပရောဂျက် မရှိပါ။",
      "Search characters":"ဇာတ်ကောင်ရှာရန်"

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
    let result = language === "my" ? (dictionaries.my[key] || trimmed) : key;
    if (language === "my") {
      const revision = trimmed.match(/^Revision (\d+) · (\d+) reference\(s\)$/);
      if (revision) result = "Revision " + revision[1] + " · ကိုးကားပုံ " + revision[2] + " ပုံ";
      const shot = trimmed.match(/^SHOT (\d+)$/);
      if (shot) result = "ရိုက်ကွက် " + shot[1];
      const shots = trimmed.match(/^(\d+) shot\(s\)$/);
      if (shots) result = shots[1] + " ရိုက်ကွက်";
      const bindings = trimmed.match(/^(\d+) binding\(s\)$/);
      if (bindings) result = bindings[1] + " ချိတ်ဆက်မှု";
      const pinned = trimmed.match(/^Revision (\d+) · SHA ([a-f0-9]{12})…$/i);
      if (pinned) result = "ဗားရှင်း " + pinned[1] + " · SHA " + pinned[2] + "…";
      if (trimmed.startsWith("Could not bind character: ")) {
        result = "ဇာတ်ကောင်ချိတ်ဆက်၍ မရပါ: " + trimmed.slice("Could not bind character: ".length);
      }
      if (trimmed.startsWith("Could not import character bundle: ")) {
        result = "Character Bundle ထည့်သွင်း၍ မရပါ: " + trimmed.slice(35);
      }
    } else {
      const revision = trimmed.match(/^Revision (\d+) · ကိုးကားပုံ (\d+) ပုံ$/);
      if (revision) result = "Revision " + revision[1] + " · " + revision[2] + " reference(s)";
      const shot = trimmed.match(/^ရိုက်ကွက် (\d+)$/);
      if (shot) result = "SHOT " + shot[1];
      const shots = trimmed.match(/^(\d+) ရိုက်ကွက်$/);
      if (shots) result = shots[1] + " shot(s)";
      const bindings = trimmed.match(/^(\d+) ချိတ်ဆက်မှု$/);
      if (bindings) result = bindings[1] + " binding(s)";
      const pinned = trimmed.match(/^ဗားရှင်း (\d+) · SHA ([a-f0-9]{12})…$/i);
      if (pinned) result = "Revision " + pinned[1] + " · SHA " + pinned[2] + "…";
      if (trimmed.startsWith("ဇာတ်ကောင်ချိတ်ဆက်၍ မရပါ: ")) {
        result = "Could not bind character: " + trimmed.slice("ဇာတ်ကောင်ချိတ်ဆက်၍ မရပါ: ".length);
      }
      if (trimmed.startsWith("Character Bundle ထည့်သွင်း၍ မရပါ: ")) {
        result = "Could not import character bundle: " + trimmed.slice(35);
      }
    }
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
    const originalAlert = window.alert.bind(window);
    const originalConfirm = window.confirm.bind(window);
    const originalPrompt = window.prompt.bind(window);
    window.alert = (message) => originalAlert(translate(String(message)));
    window.confirm = (message) => originalConfirm(translate(String(message)));
    window.prompt = (message, value) => originalPrompt(translate(String(message)), value == null ? value : translate(String(value)));
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
  window.STILLAI18N = { init, setLanguage, refresh: apply, getLanguage: () => language, translate };
})();