(() => {
  "use strict";
  const KEY = "stilla.character-library.v1";
  const MAX_PROFILE_COUNT = 30;
  const MAX_REFERENCE_BYTES = 512 * 1024;
  const MAX_TOTAL_BYTES = 3 * 1024 * 1024;
  let selectedId = null;
  let draftPreviews = {};
  let query = "";

  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
  const splitList = (value) => value.split(",").map((item) => item.trim()).filter(Boolean);
  const joinList = (value) => Array.isArray(value) ? value.join(", ") : "";
  const readLibrary = () => {
    try {
      const value = JSON.parse(localStorage.getItem(KEY) || "[]");
      return Array.isArray(value) ? value.filter((item) =>
        item && item.profile && typeof item.profile.id === "string"
      ) : [];
    } catch {
      return [];
    }
  };
  const writeLibrary = (items) => {
    const encoded = JSON.stringify(items);
    if (encoded.length > MAX_TOTAL_BYTES) {
      throw new Error("Character library reached its 3 MB browser-storage limit. Export profiles and reduce reference image sizes.");
    }
    localStorage.setItem(KEY, encoded);
  };
  const freshId = () => {
    if (window.crypto && typeof window.crypto.randomUUID === "function") {
      return window.crypto.randomUUID().replace(/-/g, "").slice(0, 24);
    }
    return "char" + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
  };
  const emptyProfile = () => ({
    schema_version: 1,
    id: freshId(),
    name: "",
    species_or_type: "Original cartoon character",
    visual: {
      silhouette: "", body_proportions: "", face_shape: "", eyes: "", nose: "", mouth: "",
      primary_colors: [], surface_or_skin_detail: "", hairstyle_or_head_shape: "", outfit: "",
      accessories: [], distinguishing_marks: [], art_style: "original stylized 3D cartoon",
      fixed_features: []
    },
    personality: {
      archetype: "lovable mischief-maker", core_traits: [], strength: "", comic_flaw: "",
      humor_mechanics: [], speech_pattern: "", catchphrase: "", reaction_style: "",
      relationship_dynamic: "", running_gag: "", avoid: []
    },
    references: [], voice_description: "", language: "en", canonical_seed: null
  });
  const selectedRecord = () => readLibrary().find((item) => item.profile.id === selectedId) || null;
  const field = (label, name, value, hint = "", area = false) =>
    '<label class="character-field"><span>' + esc(label) + '</span>' +
    (area ? '<textarea name="' + name + '" rows="2">' + esc(value) + '</textarea>' :
      '<input name="' + name + '" value="' + esc(value) + '">') +
    (hint ? '<small>' + esc(hint) + '</small>' : "") + '</label>';
  const profileForm = (record) => {
    const p = record ? record.profile : emptyProfile();
    const v = p.visual;
    const c = p.personality;
    return '<form id="characterForm" class="character-form">' +
      '<section class="character-section"><div class="character-section-head"><div><span class="eyebrow">01 / IDENTITY</span><h2>Character basics</h2></div><span class="pill">Original design</span></div>' +
      '<div class="character-fields two">' + field("Character name", "name", p.name, "A unique name used in stories and the library.") +
      field("Species / character type", "species_or_type", p.species_or_type) +
      field("Dialogue language", "language", p.language, "Examples: en, my, th, ja") +
      field("Canonical seed", "canonical_seed", p.canonical_seed ?? "", "Optional unsigned 32-bit seed; only applied when supported.") + '</div></section>' +
      '<section class="character-section"><div class="character-section-head"><div><span class="eyebrow">02 / VISUAL DNA</span><h2>Lock the appearance</h2></div><span class="pill good">Identity anchors</span></div>' +
      '<div class="character-fields two">' +
      field("Silhouette", "visual.silhouette", v.silhouette, "Overall outline and recognizable shape.", true) +
      field("Body proportions", "visual.body_proportions", v.body_proportions, "Head/body ratio, limb length, build.", true) +
      field("Face shape", "visual.face_shape", v.face_shape, "", true) +
      field("Eyes", "visual.eyes", v.eyes, "Shape, size, spacing, color.", true) +
      field("Nose", "visual.nose", v.nose, "", true) +
      field("Mouth", "visual.mouth", v.mouth, "", true) +
      field("Primary colors", "visual.primary_colors", joinList(v.primary_colors), "Comma-separated color names.") +
      field("Surface / skin detail", "visual.surface_or_skin_detail", v.surface_or_skin_detail, "", true) +
      field("Hair / head shape", "visual.hairstyle_or_head_shape", v.hairstyle_or_head_shape, "", true) +
      field("Outfit", "visual.outfit", v.outfit, "Default canonical costume.", true) +
      field("Accessories", "visual.accessories", joinList(v.accessories), "Comma-separated; keep stable.") +
      field("Distinguishing marks", "visual.distinguishing_marks", joinList(v.distinguishing_marks), "Scars, spots, patterns, etc.") +
      field("Art style", "visual.art_style", v.art_style) +
      field("Fixed features", "visual.fixed_features", joinList(v.fixed_features), "Features that must never change.") + '</div></section>' +
      '<section class="character-section"><div class="character-section-head"><div><span class="eyebrow">03 / PERSONALITY DNA</span><h2>Make the character memorable</h2></div><span class="pill">Original comedy</span></div>' +
      '<div class="character-fields two">' +
      field("Personality archetype", "personality.archetype", c.archetype) +
      field("Core traits", "personality.core_traits", joinList(c.core_traits), "Comma-separated traits.") +
      field("Strength", "personality.strength", c.strength, "", true) +
      field("Comic flaw", "personality.comic_flaw", c.comic_flaw, "A lovable weakness that drives original situations.", true) +
      field("Humor mechanics", "personality.humor_mechanics", joinList(c.humor_mechanics), "e.g. overconfidence, visual timing, harmless misunderstandings.") +
      field("Speech pattern", "personality.speech_pattern", c.speech_pattern, "", true) +
      field("Catchphrase", "personality.catchphrase", c.catchphrase) +
      field("Reaction style", "personality.reaction_style", c.reaction_style, "", true) +
      field("Relationship dynamic", "personality.relationship_dynamic", c.relationship_dynamic, "", true) +
      field("Running gag", "personality.running_gag", c.running_gag, "", true) +
      field("Avoid list", "personality.avoid", joinList(c.avoid), "Behaviors or visual traits to avoid.") +
      field("Voice description", "voice_description", p.voice_description, "Voice design only; no voice model is generated here.", true) +
      '</div></section>' +
      '<div class="character-form-actions"><span class="small muted" id="characterFormStatus">Changes are drafts until saved.</span><button type="submit" class="primary">' + (record ? "Save new revision" : "Save character") + '</button></div>' +
      '</form>';
  };
  const render = () => {
    const items = readLibrary();
    const current = selectedRecord();
    const visible = items.filter((item) => item.profile.name.toLowerCase().includes(query));
    const library = visible.length ? visible.map((item) =>
      '<button class="character-library-item ' + (item.profile.id === selectedId ? "active" : "") + '" data-character-id="' + esc(item.profile.id) + '">' +
      '<span class="character-avatar">' + esc(item.profile.name.slice(0, 1).toUpperCase() || "?") + '</span><span class="character-library-meta"><strong>' + esc(item.profile.name) + '</strong><small>Revision ' + esc(item.revision) + ' · ' + item.profile.references.length + ' reference(s)</small></span><span class="pill">' + (item.profile.references.length ? "Refs saved" : "No refs") + '</span></button>'
    ).join("") : '<div class="character-empty">No characters yet. Create an original character to begin your library.</div>';
    const refs = current ? current.profile.references.map((ref) => {
      const preview = current.reference_previews && current.reference_previews[ref.asset_id];
      return '<div class="character-ref-card">' + (preview ? '<img src="' + preview + '" alt="Reference image ' + esc(ref.role) + '">' : '<div class="character-ref-placeholder">Image stored in project bundle</div>') +
        '<div><strong>' + esc(ref.role) + '</strong><small>' + esc(ref.asset_id) + '</small></div><button type="button" class="quiet" data-remove-ref="' + esc(ref.asset_id) + '" aria-label="Remove reference">Remove</button></div>';
    }).join("") : "";
    return '<div class="page-head"><div><div class="eyebrow">STILLA STUDIO / CHARACTER WORKSPACE</div><h1>Character Creator</h1><p>Build original characters once, preserve their visual DNA and reuse them in future stories.</p></div><div class="head-actions"><button id="newCharacter">＋ New character</button><button id="importCharacterBundle">Import bundle</button><input id="characterBundleInput" type="file" accept="application/json,.json" hidden><button id="exportCharacter" ' + (current ? "" : "disabled") + '>Export bundle</button><button id="deleteCharacter" class="quiet" ' + (current ? "" : "disabled") + '>Delete</button></div></div>' +
      '<div class="character-prototype-notice"><strong>Local browser prototype</strong><span>Profiles and small reference previews are saved in this browser only. Export a bundle to back up or move a character. This is not yet connected to project-folder storage or ComfyUI reference conditioning.</span></div>' +
      '<div class="character-workspace"><aside class="card character-library"><div class="card-head"><div><span class="eyebrow">YOUR CAST</span><h2>Character Library</h2></div><span class="pill">' + items.length + ' / ' + MAX_PROFILE_COUNT + '</span></div><input id="characterSearch" type="search" placeholder="Search characters…" value="' + esc(query) + '" aria-label="Search characters"><div class="character-library-list">' + library + '</div><div class="character-library-foot small muted">Each save creates a revision. Deletion requires confirmation.</div></aside>' +
      '<div class="character-editor">' + profileForm(current) +
      '<section class="card character-reference-section"><div class="character-section-head"><div><span class="eyebrow">04 / REFERENCE IMAGES</span><h2>Canonical visual references</h2><p class="small muted">Import approved images to help preserve identity. Use front, side, back and expression views where available.</p></div><label class="button-like" for="characterReferenceInput">＋ Add reference</label><input id="characterReferenceInput" type="file" accept="image/png,image/jpeg,image/webp" multiple hidden></div>' +
      '<div class="character-reference-grid">' + (refs || '<div class="character-empty">No reference images added yet.</div>') + '</div>' +
      '<div class="row between character-sheet-row"><div><strong>Character reference sheet</strong><p class="small muted">Turnaround / expression sheet generation will be enabled after a verified local image workflow adapter is connected.</p></div><button type="button" disabled title="Local reference-sheet workflow is not connected">Generate sheet · unavailable</button></div></section>' +
      '<div class="character-use-row"><div><strong>Reuse in Script & Storyboard</strong><p class="small muted">The selected profile can be exported as a validated M7a-compatible JSON bundle. Storyboard binding is a later integration step.</p></div><button type="button" id="copyCharacterPrompt" ' + (current ? "" : "disabled") + '>Copy identity brief</button></div>' +
      '</div></div>';
  };
  const setPath = (object, path, value) => {
    const parts = path.split(".");
    let target = object;
    for (const part of parts.slice(0, -1)) target = target[part];
    target[parts[parts.length - 1]] = value;
  };
  const collectProfile = (form, prior) => {
    const profile = prior ? JSON.parse(JSON.stringify(prior)) : emptyProfile();
    const data = new FormData(form);
    for (const [key, raw] of data.entries()) {
      let value = String(raw).trim();
      if (key === "canonical_seed") {
        if (!value) value = null;
        else if (!/^\d+$/.test(value) || Number(value) > 4294967295) throw new Error("Canonical seed must be an integer from 0 to 4294967295.");
        else value = Number(value);
      } else if (["visual.primary_colors", "visual.accessories", "visual.distinguishing_marks", "visual.fixed_features", "personality.core_traits", "personality.humor_mechanics", "personality.avoid"].includes(key)) {
        value = splitList(value);
      }
      setPath(profile, key, value);
    }
    if (!profile.name) throw new Error("Please enter a character name.");
    for (const key of ["silhouette", "body_proportions", "face_shape", "eyes"]) {
      if (!profile.visual[key].trim()) throw new Error("Complete the required visual identity fields: silhouette, body proportions, face shape and eyes.");
    }
    return profile;
  };
  const downloadBundle = (record) => {
    const payload = JSON.stringify({ format: "stilla-character-bundle", bundle_version: 1,
      profile: record.profile, reference_previews: record.reference_previews || {},
      revision: record.revision, updated_at: record.updated_at }, null, 2);
    const url = URL.createObjectURL(new Blob([payload], { type: "application/json" }));
    const anchor = document.createElement("a");
    anchor.href = url; anchor.download = record.profile.name.toLowerCase().replace(/[^a-z0-9]+/g, "-") + ".stilla-character.json";
    anchor.click(); URL.revokeObjectURL(url);
  };
  const wire = () => {
    const $ = (id) => document.getElementById(id);
    $("newCharacter")?.addEventListener("click", () => { selectedId = null; draftPreviews = {}; render(); });
    $("characterSearch")?.addEventListener("input", (event) => { query = event.target.value.toLowerCase(); const pos = event.target.selectionStart; render(); const input = $("characterSearch"); input.focus(); input.setSelectionRange(pos, pos); });
    document.querySelectorAll("[data-character-id]").forEach((button) => button.addEventListener("click", () => { selectedId = button.dataset.characterId; draftPreviews = {}; render(); }));
    $("characterForm")?.addEventListener("submit", (event) => {
      event.preventDefault();
      try {
        const items = readLibrary();
        const prior = selectedRecord();
        const profile = collectProfile(event.currentTarget, prior?.profile || null);
        if (!prior && items.length >= MAX_PROFILE_COUNT) throw new Error("The browser prototype supports up to 30 saved characters.");
        const record = { profile, revision: (prior?.revision || 0) + 1,
          updated_at: new Date().toISOString(),
          reference_previews: { ...(prior?.reference_previews || {}), ...draftPreviews } };
        const next = items.filter((item) => item.profile.id !== profile.id);
        next.unshift(record);
        writeLibrary(next);
        selectedId = profile.id; draftPreviews = {}; render();
        $("characterFormStatus")?.replaceChildren(document.createTextNode("Saved as revision " + record.revision + "."));
        document.getElementById("saveState").textContent = "Character saved · browser";
      } catch (error) {
        const status = $("characterFormStatus");
        if (status) { status.textContent = error.message; status.classList.add("error"); }
      }
    });
    $("characterReferenceInput")?.addEventListener("change", async (event) => {
      const files = Array.from(event.target.files || []);
      try {
        const record = selectedRecord();
        if (!record) throw new Error("Save the character first, then add reference images.");
        const items = readLibrary();
        const current = items.find((item) => item.profile.id === selectedId);
        if (current.profile.references.length + files.length > 20) throw new Error("A character can have up to 20 reference images.");
        for (const file of files) {
          if (!["image/png", "image/jpeg", "image/webp"].includes(file.type)) throw new Error("Only PNG, JPEG and WebP reference images are supported.");
          if (file.size > MAX_REFERENCE_BYTES) throw new Error("Each reference image must be 512 KB or smaller in this prototype.");
          const dataUrl = await new Promise((resolve, reject) => {
            const reader = new FileReader(); reader.onload = () => resolve(reader.result); reader.onerror = () => reject(new Error("Could not read the selected image.")); reader.readAsDataURL(file);
          });
          const assetId = freshId();
          const extension = file.type === "image/jpeg" ? "jpg" : file.type.split("/")[1];
          current.profile.references.push({ asset_id: assetId, relative_path: "references/" + assetId + "." + extension, role: "reference", sha256: "" });
          current.reference_previews = current.reference_previews || {};
          current.reference_previews[assetId] = dataUrl;
        }
        current.revision += 1; current.updated_at = new Date().toISOString();
        writeLibrary([current, ...items.filter((item) => item.profile.id !== selectedId)]);
        render();
      } catch (error) {
        alert(error.message);
      } finally {
        event.target.value = "";
      }
    });
    document.querySelectorAll("[data-remove-ref]").forEach((button) => button.addEventListener("click", () => {
      const items = readLibrary(); const record = items.find((item) => item.profile.id === selectedId);
      if (!record) return;
      const id = button.dataset.removeRef;
      record.profile.references = record.profile.references.filter((ref) => ref.asset_id !== id);
      delete record.reference_previews[id]; record.revision += 1; record.updated_at = new Date().toISOString();
      try { writeLibrary(items); render(); } catch (error) { alert(error.message); }
    }));
    $("importCharacterBundle")?.addEventListener("click", () => $("characterBundleInput")?.click());
    $("characterBundleInput")?.addEventListener("change", async (event) => {
      const file = event.target.files?.[0];
      try {
        if (!file) return;
        if (file.size > MAX_TOTAL_BYTES) throw new Error("Character bundle exceeds the 3 MB import limit.");
        const bundle = JSON.parse(await file.text());
        if (bundle.format !== "stilla-character-bundle" || bundle.bundle_version !== 1) throw new Error("Unsupported character bundle format.");
        const profile = bundle.profile;
        if (!profile || profile.schema_version !== 1 || typeof profile.name !== "string" ||
            !profile.visual || !profile.personality || !Array.isArray(profile.references)) {
          throw new Error("Character bundle does not contain a valid profile.");
        }
        const items = readLibrary();
        if (items.length >= MAX_PROFILE_COUNT) throw new Error("The browser prototype supports up to 30 saved characters.");
        const previews = {};
        const refs = profile.references.map((ref) => {
          const assetId = freshId();
          const dataUrl = bundle.reference_previews?.[ref.asset_id];
          let extension = "png";
          if (typeof dataUrl === "string") {
            const match = dataUrl.match(/^data:image\/(png|jpeg|webp);base64,([A-Za-z0-9+/=]+)$/);
            if (!match || dataUrl.length > MAX_REFERENCE_BYTES * 1.5) throw new Error("A reference image in this bundle is invalid or too large.");
            extension = match[1] === "jpeg" ? "jpg" : match[1];
            previews[assetId] = dataUrl;
          }
          return { asset_id: assetId, relative_path: "references/" + assetId + "." + extension,
            role: typeof ref.role === "string" ? ref.role.slice(0, 100) : "reference", sha256: "" };
        });
        profile.id = freshId();
        profile.references = refs;
        const record = { profile, revision: 1, updated_at: new Date().toISOString(), reference_previews: previews };
        writeLibrary([record, ...items]);
        selectedId = profile.id; draftPreviews = {}; render();
      } catch (error) {
        alert("Could not import character bundle: " + error.message);
      } finally {
        event.target.value = "";
      }
    });
    $("exportCharacter")?.addEventListener("click", () => { const record = selectedRecord(); if (record) downloadBundle(record); });
    $("deleteCharacter")?.addEventListener("click", () => {
      const record = selectedRecord(); if (!record) return;
      if (!confirm('Delete "' + record.profile.name + '" from this browser library? Export a backup first if needed.')) return;
      writeLibrary(readLibrary().filter((item) => item.profile.id !== selectedId));
      selectedId = null; draftPreviews = {}; render();
    });
    $("copyCharacterPrompt")?.addEventListener("click", async () => {
      const record = selectedRecord(); if (!record) return;
      const p = record.profile; const v = p.visual; const c = p.personality;
      const brief = ["Original character: " + p.name + " (" + p.species_or_type + ").",
        "Visual identity: " + [v.silhouette, v.body_proportions, v.face_shape, v.eyes, v.primary_colors.join(", "), v.outfit, v.accessories.join(", "), v.distinguishing_marks.join(", "), v.art_style].filter(Boolean).join("; "),
        "Personality: " + [c.archetype, c.core_traits.join(", "), c.comic_flaw, c.humor_mechanics.join(", "), c.catchphrase].filter(Boolean).join("; "),
        "Keep all canonical visual anchors unchanged between scenes."].join("\n");
      try { await navigator.clipboard.writeText(brief); alert("Identity brief copied."); }
      catch { alert(brief); }
    });
  };
  window.STILLACharacterUI = { render, wire };
})();