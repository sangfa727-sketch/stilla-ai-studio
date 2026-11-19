(() => {
  "use strict";

  const translate = (value) => window.STILLAI18N?.translate?.(value) ?? value;
  const allowedStatuses = new Set(["available", "partial", "unsupported"]);
  const labels = Object.freeze({ ipadapter: "IPAdapter", instantid: "InstantID" });

  function appendText(parent, tag, className, value) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    element.textContent = String(value);
    parent.appendChild(element);
    return element;
  }

  function validRequiredInputTypes(node) {
    if (
      !Array.isArray(node.required_input_types) ||
      node.required_input_types.length > 128 ||
      node.required_input_types.length !== node.required_inputs.length
    ) {
      return false;
    }
    const seen = new Set();
    for (const item of node.required_input_types) {
      if (
        !item ||
        typeof item.name !== "string" ||
        !node.required_inputs.includes(item.name) ||
        seen.has(item.name) ||
        (item.input_type !== null && (
          typeof item.input_type !== "string" ||
          item.input_type.length < 1 ||
          item.input_type.length > 128
        )) ||
        (item.choice_count !== null && (
          !Number.isInteger(item.choice_count) ||
          item.choice_count < 1 ||
          item.choice_count > 512
        )) ||
        (item.input_type === "COMBO" && item.choice_count === null) ||
        (item.input_type !== "COMBO" && item.choice_count !== null)
      ) {
        return false;
      }
      seen.add(item.name);
    }
    return seen.size === node.required_inputs.length;
  }

  function validateReport(report) {
    if (
      !report ||
      report.generation_ready !== false ||
      !allowedStatuses.has(report.status) ||
      !Number.isInteger(report.node_count) ||
      report.node_count < 0 ||
      report.node_count > 20000 ||
      !Array.isArray(report.capabilities) ||
      report.capabilities.length !== 2
    ) {
      throw new Error(translate("Capability report is invalid; generation remains disabled."));
    }
    if (report.comfyui_version !== null && (
      typeof report.comfyui_version !== "string" || report.comfyui_version.length > 64
    )) {
      throw new Error(translate("Capability report is invalid; generation remains disabled."));
    }
    const seen = new Set();
    for (const capability of report.capabilities) {
      if (
        !capability ||
        !Object.prototype.hasOwnProperty.call(labels, capability.capability) ||
        seen.has(capability.capability) ||
        !allowedStatuses.has(capability.status) ||
        !Array.isArray(capability.nodes) ||
        capability.nodes.length > 3 ||
        !Array.isArray(capability.missing_nodes) ||
        capability.missing_nodes.length > 3 ||
        capability.missing_nodes.some((name) => typeof name !== "string" || name.length > 200)
      ) {
        throw new Error(translate("Capability report is invalid; generation remains disabled."));
      }
      seen.add(capability.capability);
      for (const node of capability.nodes) {
        if (
          !node ||
          typeof node.class_name !== "string" ||
          node.class_name.length > 128 ||
          typeof node.schema_valid !== "boolean" ||
          !Array.isArray(node.required_inputs) ||
          node.required_inputs.length > 128 ||
          node.required_inputs.some((name) => typeof name !== "string" || name.length > 128) ||
          (node.required_input_types !== undefined && !validRequiredInputTypes(node))
        ) {
          throw new Error(translate("Capability report is invalid; generation remains disabled."));
        }
      }
    }
    if (seen.size !== 2) {
      throw new Error(translate("Capability report is invalid; generation remains disabled."));
    }
  }

  function render(root, report) {
    if (!root || typeof root.replaceChildren !== "function") {
      throw new TypeError("A report container is required.");
    }
    validateReport(report);
    root.replaceChildren();

    appendText(root, "h3", "", translate("Installed ComfyUI conditioning capabilities"));
    const version = report.comfyui_version || translate("Not reported");
    appendText(
      root,
      "p",
      "notice warn",
      translate("ComfyUI version") + ": " + version +
        " · " + translate("Node classes") + ": " + report.node_count +
        " · " + translate("Generation ready") + ": " + translate("No — discovery only")
    );

    for (const capability of report.capabilities) {
      const section = document.createElement("section");
      section.className = "card";
      const header = document.createElement("div");
      header.className = "row between";
      appendText(header, "strong", "", translate(labels[capability.capability]));
      appendText(
        header,
        "span",
        "pill " + (capability.status === "available" ? "good" : "warn"),
        translate(capability.status)
      );
      section.appendChild(header);

      for (const node of capability.nodes) {
        const item = document.createElement("div");
        item.className = "list-item";
        const meta = document.createElement("div");
        meta.className = "meta";
        appendText(meta, "strong", "", node.class_name);
        appendText(
          meta,
          "span",
          "small muted",
          translate("Required sockets") + ": " +
            (node.required_inputs.length
              ? node.required_inputs.map((name) => {
                  const detail = (node.required_input_types || []).find((item) => item.name === name);
                  if (!detail || !detail.input_type) {
                    return name + " [" + translate("Type unavailable") + "]";
                  }
                  if (detail.input_type === "COMBO") {
                    return name + " [COMBO · " + detail.choice_count + " " + translate("choices") + "]";
                  }
                  return name + " [" + detail.input_type + "]";
                }).join(", ")
              : translate("None"))
        );
        item.appendChild(meta);
        appendText(
          item,
          "span",
          "pill " + (node.schema_valid ? "good" : "warn"),
          translate(node.schema_valid ? "Schema structure valid" : "Schema mismatch")
        );
        section.appendChild(item);
      }

      if (capability.missing_nodes.length) {
        appendText(
          section,
          "p",
          "small muted",
          translate("Missing nodes") + ": " + capability.missing_nodes.join(", ")
        );
      }
      root.appendChild(section);
    }
    return root;
  }

  window.STILLAComfyUICapabilityUI = Object.freeze({ render });
})();
