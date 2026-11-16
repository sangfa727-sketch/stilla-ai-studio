# M7j — Local Runtime Laptop Acceptance

This checklist is for the user's Windows laptop. It validates the existing local services without changing their model files or runtime configuration.

## Before opening STILLA

1. Start the existing Bionic application and load the already-installed Qwen2.5 model.
2. Confirm Bionic's OpenAI-compatible local API is enabled. The expected base URL is `http://127.0.0.1:1234/v1`.
3. Start the existing ComfyUI server. The expected base URL is `http://127.0.0.1:8188`.
4. Do not move, rename, reinstall, download, or reconfigure Qwen2.5/Bionic or ComfyUI for this test.

## Launch the desktop application

From the repository root, install the documented optional dependencies if they are not already installed:

```powershell
python -m pip install -e ".[desktop,dev,image]"
python -m stilla.desktop.app
```

Open **Settings → Qwen2.5 / Bionic**.

## Qwen2.5 / Bionic

1. Keep the default endpoint `http://127.0.0.1:1234/v1` unless Bionic is configured to use another local port.
2. Select **Discover models & test**.
3. Choose the exact model ID returned by Bionic in the model-ID field. The default expected ID is `qwen2.5-7b-instruct-uncensored`, but the server's returned ID is authoritative.
4. Select **Save settings**.
5. Close and reopen STILLA, then verify the endpoint and model ID are restored.

**Expected result:** the Qwen status shows Connected and the selected model is listed by `GET /v1/models`.

This is a connectivity and model-discovery check only. It does not send a prompt or prove that text inference works.

## ComfyUI

1. Keep the default endpoint `http://127.0.0.1:8188` unless ComfyUI uses another local port.
2. Select **Test ComfyUI**.

**Expected result:** the ComfyUI status shows Connected after `GET /system_stats` returns a valid system/device response.

This check does not submit a workflow or generate an image.

## Model file path — important

When Bionic has already loaded Qwen2.5 and serves it through its local API, STILLA does **not** need the GGUF model path. Select the model ID returned by Bionic instead. Direct GGUF loading by STILLA is not implemented in M7j.

## Failure handling

- **Qwen unavailable:** confirm Bionic is running, the model is loaded, the local API is enabled, and the port is correct.
- **Model ID not found:** choose one of the IDs returned by model discovery; do not guess a model path.
- **ComfyUI unavailable:** confirm ComfyUI is running and the server port is correct.
- **Browser preview:** browser-only mode cannot test loopback services; use the PyWebView desktop application.

The health checks accept literal loopback HTTP endpoints only, bypass configured HTTP proxies, reject redirects, use a three-second timeout, and cap JSON responses at 256 KiB. They do not upload media, contact cloud services, change runtime settings, or touch model files.

## Acceptance record

- [ ] Windows desktop application opens successfully.
- [ ] Qwen2.5 model discovery succeeds.
- [ ] Correct Qwen model ID can be selected and saved.
- [ ] Qwen settings survive an application restart.
- [ ] ComfyUI health check succeeds.
- [ ] Burmese UI text is legible on the Windows display.
- [ ] No model or ComfyUI files/settings were changed.

Physical acceptance must be recorded separately from hosted CI. A passing CI run is not evidence that the user's laptop services are running.
