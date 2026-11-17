# M7k — Windows Desktop Packaging and Laptop Acceptance

## Scope

M7k introduces an optional Windows one-folder package for the existing PyWebView desktop host. It does not replace the browser prototype or alter local AI runtimes.

## Build from source

Use Python 3.11+ in a project virtual environment:

```powershell
python -m pip install -e ".[desktop,dev,image,packaging]"
python -m PyInstaller --noconfirm packaging/stilla.spec
```

Expected executable:

```text
dist/STILLA-AI-Studio/STILLA-AI-Studio.exe
```

Keep the entire `dist/STILLA-AI-Studio` directory together. This is an onedir package, not a standalone single-file executable.

## Windows prerequisites

- Windows 10/11 x64.
- Microsoft Edge WebView2 Evergreen Runtime. STILLA does not download or install it.
- The package includes the PyWebView Python application and prototype UI resources, but not Python, WebView2 Runtime, Bionic, Qwen weights, ComfyUI, FFmpeg, user workspaces, or generated media.
- If WebView2 is missing, install/repair the Evergreen Runtime using Microsoft's official distribution. Do not download installers from third-party sites.

## First launch acceptance

- [ ] Extract the complete package to a writable local folder.
- [ ] Launch `STILLA-AI-Studio.exe`.
- [ ] Confirm the UI opens without a missing-resource error. The desktop host serves bundled UI, CSS, and JavaScript through pywebview’s loopback HTTP server instead of direct `file://` navigation.
- [ ] Switch UI language between English and Myanmar.
- [ ] Create a disposable test project and verify it appears after restart.
- [ ] Import a test reference image using the native file picker.
- [ ] Verify the reference preview loads and the original file remains unchanged.
- [ ] Verify the application can close and reopen cleanly.
- [ ] Confirm no model files, Bionic settings, ComfyUI settings, or existing user projects were changed.

## Local AI runtime acceptance

Start the existing Bionic application with the existing Qwen2.5 model loaded, and start the existing ComfyUI server before testing:

- Qwen base URL: `http://127.0.0.1:1234/v1`
- ComfyUI base URL: `http://127.0.0.1:8188`

In Settings, discover the model list and select the exact model ID returned by Bionic. Save, close, reopen, and verify settings persistence. Test ComfyUI health.

These are metadata/health checks only. M7k does not send prompts, run Qwen inference, submit ComfyUI workflows, or generate images. Do not enter a GGUF path; Bionic remains responsible for loading the existing model.

## CI versus physical acceptance

Windows CI verifies that PyInstaller can assemble the onedir package and that the executable and prototype resource file exist in the output. It does not launch the GUI, validate WebView2 on the user's machine, check Burmese font rendering, or test local GPU/model inference.

Record the checklist above only after a real laptop run. Do not mark physical acceptance complete based on CI alone.

## Rollback

The package is optional. If it fails to launch, close it and continue using the documented source launcher:

```powershell
python -m stilla.desktop.app
```

Do not remove or reinstall Bionic, Qwen2.5, ComfyUI, or their model files as a packaging troubleshooting step.
