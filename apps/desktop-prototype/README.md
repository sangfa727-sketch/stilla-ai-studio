# STILLA Desktop UX Prototype

Open `index.html` directly in a modern browser. It uses only HTML, CSS, and vanilla JavaScript; no package install, server, or network access is required.

## Included interactions

- Seven separate navigation destinations: Projects, Script & Storyboard, Generate, Edit Studio, Assets & History, Export, Settings.
- Responsive desktop-first shell and compact/mobile navigation behavior.
- Dark/light theme toggle.
- Persistent sample task-queue panel across navigation.
- Demonstration interactions for script draft text, scene addition, asset search/filter, timeline zoom, settings fields, and export preflight messaging.

## Important limitations

This is a visual/interaction prototype, not the production application. Project counts and assets are sample data. Browser-only mode does not connect to Bionic/Qwen or ComfyUI and cannot test loopback services. When launched through the optional PyWebView desktop host, Settings can safely check the local Bionic OpenAI-compatible model list (GET /v1/models) and ComfyUI status (GET /system_stats), and persist non-secret endpoint/model preferences inside the selected workspace. These checks are metadata-only: they do not send prompts, run inference, submit workflows, import media, edit real video, launch generation, or render exports.

The Qwen model file remains managed by Bionic; a GGUF file path is not needed for the API connection. Direct GGUF loading, real Qwen inference, ComfyUI workflow submission, media generation, video editing, and export are not implemented. Do not use the health-check result alone to infer generation readiness, production security, export capability, or performance. Physical Windows and phone acceptance remains required.
