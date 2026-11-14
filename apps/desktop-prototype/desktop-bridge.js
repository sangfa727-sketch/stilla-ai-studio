(() => {
  "use strict";

  const api = () => window.pywebview && window.pywebview.api ? window.pywebview.api : null;
  const desktopHost = () => new URLSearchParams(window.location.search).get("runtime") === "desktop";
  const requireApi = () => {
    const value = api();
    if (!value) throw new Error("The native desktop bridge is unavailable.");
    return value;
  };
  const call = async (method, ...args) => {
    const target = requireApi();
    if (typeof target[method] !== "function") {
      throw new Error("The desktop bridge does not support " + method + ".");
    }
    return target[method](...args);
  };

  window.STILLABridge = Object.freeze({
    isDesktop: () => desktopHost() || Boolean(api()),
    ready: () => new Promise((resolve) => {
      if (api()) { resolve(true); return; }
      if (!desktopHost()) { resolve(false); return; }
      window.addEventListener("pywebviewready", () => resolve(Boolean(api())), { once: true });
    }),
    runtimeInfo: () => call("get_runtime_info"),
    chooseWorkspace: () => call("choose_workspace_directory"),
    listProjects: () => call("list_projects"),
    createProject: (title, language) => call("create_project", title, language),
    listCharacters: (projectId) => call("list_character_profiles", projectId),
    listCharacterRecords: (projectId) => call("list_character_profile_records", projectId),
    saveCharacter: (projectId, profile, expectedRevision) =>
      call("save_character_profile", projectId, profile, expectedRevision),
    deleteCharacter: (projectId, characterId) => call("delete_character_profile", projectId, characterId),
    importCharacterReference: (projectId, characterId) =>
      call("import_character_reference", projectId, characterId),
    importCharacterReferenceAndSave: (projectId, characterId, expectedRevision) =>
      call("import_character_reference_and_save", projectId, characterId, expectedRevision),
    saveDocument: (projectId, name, value) => call("save_document", projectId, name, value),
    loadDocument: (projectId, name) => call("load_document", projectId, name),
    saveDocumentVersioned: (projectId, name, value, expectedRevision) =>
      call("save_document_versioned", projectId, name, value, expectedRevision),
    loadDocumentVersioned: (projectId, name) => call("load_document_versioned", projectId, name)
  });
})();
