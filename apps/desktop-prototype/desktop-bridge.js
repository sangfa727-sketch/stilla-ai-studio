(() => {
  "use strict";

  const api = () => window.pywebview && window.pywebview.api ? window.pywebview.api : null;
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
    isDesktop: () => Boolean(api()),
    runtimeInfo: () => call("get_runtime_info"),
    chooseWorkspace: () => call("choose_workspace_directory"),
    listProjects: () => call("list_projects"),
    createProject: (title, language) => call("create_project", title, language),
    listCharacters: (projectId) => call("list_character_profiles", projectId),
    saveCharacter: (projectId, profile) => call("save_character_profile", projectId, profile),
    deleteCharacter: (projectId, characterId) => call("delete_character_profile", projectId, characterId),
    importCharacterReference: (projectId, characterId) => call("import_character_reference", projectId, characterId),
    saveDocument: (projectId, name, value) => call("save_document", projectId, name, value),
    loadDocument: (projectId, name) => call("load_document", projectId, name)
  });
})();
