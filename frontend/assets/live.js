(function () {
  const state = {
    autoRefresh: true,
    lastSignature: "",
    lastSource: "",
    writeToken: "",
    eventSource: null,
    fallbackTimer: null,
    facilityRows: []
  };

  function byId(id) {
    return document.getElementById(id);
  }

  function setText(id, value) {
    const node = byId(id);
    if (node) {
      node.textContent = value;
    }
  }

  function setHtml(id, value) {
    const node = byId(id);
    if (node) {
      node.innerHTML = value;
    }
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function escapeAttribute(value) {
    return escapeHtml(value).replaceAll("`", "&#96;");
  }

  function escapeSqlLiteral(value) {
    return String(value ?? "").replaceAll("\\", "\\\\").replaceAll("'", "''");
  }

  async function ensureWriteToken() {
    if (state.writeToken) {
      return state.writeToken;
    }

    const response = await fetch("/api/security/bootstrap", {
      cache: "no-store",
      credentials: "same-origin",
      headers: {
        "X-Requested-With": "fetch"
      }
    });

    const payload = await response.json().catch(() => ({}));
    if (!response.ok || payload.ok === false || !payload.writeToken) {
      throw new Error(payload.error || "Unable to initialize secure write access.");
    }

    state.writeToken = payload.writeToken;
    return state.writeToken;
  }

  function pulseNode(node, className = "is-updated", duration = 1400) {
    if (!node) {
      return;
    }

    node.classList.remove(className);
    // Force the browser to restart the animation when the same class is reused.
    void node.offsetWidth;
    node.classList.add(className);

    window.setTimeout(() => {
      node.classList.remove(className);
    }, duration);
  }

  function pulseSelector(selector, className = "is-updated", duration = 1400) {
    document.querySelectorAll(selector).forEach((node, index) => {
      window.setTimeout(() => pulseNode(node, className, duration), index * 40);
    });
  }

  function setNote(id, message, tone = "info") {
    const node = byId(id);
    if (!node) {
      return;
    }

    node.textContent = message;
    node.classList.remove("is-error", "is-success", "is-info");
    node.classList.add(`is-${tone}`);
    pulseNode(node, "is-updated", 1200);
  }

  function formatTimestamp(value) {
    if (!value) {
      return "Not synced yet";
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return new Intl.DateTimeFormat("en-IN", {
      dateStyle: "medium",
      timeStyle: "medium"
    }).format(date);
  }

  function payloadSignature(data) {
    return JSON.stringify({
      source: data.meta?.source,
      totalKg: data.overview?.totalKg,
      scope2Kg: data.overview?.scope2Kg,
      scope3Kg: data.overview?.scope3Kg,
      facilities: data.overview?.facilities,
      topFacility: data.facilityLeaders?.[0],
      topRegion: data.regionTotals?.[0]
    });
  }

  async function fetchJson(url, options, allowRetry = true) {
    const method = String(options?.method || "GET").toUpperCase();
    const headers = {
      "Content-Type": "application/json",
      "X-Requested-With": "fetch",
      ...(options?.headers || {})
    };

    if (method !== "GET" && method !== "HEAD") {
      headers["X-GreenTrace-Write-Token"] = await ensureWriteToken();
    }

    const response = await fetch(url, {
      cache: "no-store",
      credentials: "same-origin",
      headers,
      ...options
    });

    const payload = await response.json().catch(() => ({}));
    if (
      response.status === 403 &&
      method !== "GET" &&
      method !== "HEAD" &&
      allowRetry &&
      String(payload.error || "").toLowerCase().includes("token")
    ) {
      state.writeToken = "";
      return fetchJson(url, options, false);
    }

    if (!response.ok || payload.ok === false) {
      throw new Error(payload.error || `Request failed: ${response.status}`);
    }

    return payload;
  }

  function setBadge(meta) {
    const badge = byId("live-badge");
    if (!badge) {
      return;
    }

    const isDatabase = meta?.source === "database";
    badge.textContent = isDatabase ? "Live DB" : "Snapshot";
    badge.classList.toggle("is-live", isDatabase);
    badge.classList.toggle("is-snapshot", !isDatabase);
    if (state.lastSource && state.lastSource !== meta?.source) {
      pulseNode(badge, "is-pulse", 1500);
    }
  }

  function updateStatus(meta, overview) {
    setBadge(meta);
    setText("live-source-text", meta?.source === "database" ? "Connected to MySQL and reading the latest warehouse state." : "Live warehouse unavailable, showing the latest exported snapshot.");
    setText("live-last-sync", formatTimestamp(meta?.lastUpdated));
    setText("live-reporting-period", overview?.reportingPeriod || "N/A");
    setText("live-capture-window", overview?.captureWindow || "N/A");
    setText("live-error-text", meta?.error ? meta.error : "No connection errors reported.");
  }

  function setRefreshButtonState(isLoading) {
    const button = byId("live-refresh-button");
    if (!button) {
      return;
    }

    button.classList.toggle("is-loading", isLoading);
    button.textContent = isLoading ? "Refreshing..." : "Refresh now";
  }

  function animateLiveRefresh(didRender) {
    pulseSelector(".live-monitor, .live-editor, .sql-console", "is-updated", 1400);
    pulseSelector("#live-last-sync, #live-reporting-period, #live-capture-window, #dashboard-total, #dashboard-scope", "is-fresh", 1200);

    if (didRender) {
      pulseSelector(".metric-card, .region-row, .leader-table tbody tr, .load-bar-wrap, .mix-row", "is-fresh", 1200);
    }
  }

  function applyPayload(data, forceRender) {
    const signature = payloadSignature(data);
    const shouldRender = forceRender || signature !== state.lastSignature;

    window.greenTraceData = data;
    updateStatus(data.meta, data.overview);

    if (shouldRender && window.greenTraceApp?.renderAll) {
      window.greenTraceApp.renderAll(data);
      state.lastSignature = signature;
    }

    animateLiveRefresh(shouldRender);
    state.lastSource = data.meta?.source || "";
  }

  async function refreshLiveData(forceRender) {
    const payload = await fetchJson("/api/live-data");
    applyPayload(payload.data, forceRender);
  }

  function populateFacilityForm(selectedId) {
    const select = byId("facility-select");
    if (!select || !state.facilityRows.length) {
      return;
    }

    const fallbackId = selectedId || select.value || state.facilityRows[0].hkFacility;
    select.innerHTML = state.facilityRows
      .map(
        (row) =>
          `<option value="${escapeAttribute(row.hkFacility)}">${escapeHtml(row.facilityName)}</option>`
      )
      .join("");
    select.value = fallbackId;

    const active = state.facilityRows.find((row) => row.hkFacility === select.value) || state.facilityRows[0];
    if (!active) {
      return;
    }

    if (byId("facility-name-input")) {
      byId("facility-name-input").value = active.facilityName || "";
    }
    if (byId("facility-country-input")) {
      byId("facility-country-input").value = active.country || "";
    }
    if (byId("facility-region-input")) {
      byId("facility-region-input").value = active.gridRegion || "";
    }

    const readOnly = Boolean(active.readOnly);
    ["facility-name-input", "facility-country-input", "facility-region-input", "facility-save-button"].forEach((id) => {
      const node = byId(id);
      if (node) {
        node.disabled = readOnly;
      }
    });

    setNote(
      "editor-feedback",
      readOnly
        ? "Facility editing becomes available as soon as the live warehouse connection is restored."
        : "Publishing a facility creates a fresh satellite version, preserving history while the latest state becomes visible.",
      readOnly ? "info" : "info"
    );

    ensureFacilityExamplesUi();
  }

  async function refreshFacilityRows() {
    const select = byId("facility-select");
    if (!select) {
      return;
    }

    const payload = await fetchJson("/api/editor/facilities");
    state.facilityRows = payload.rows || [];
    populateFacilityForm(select.value);
  }

  async function handleFacilitySave(event) {
    event.preventDefault();

    const hkFacility = byId("facility-select")?.value;
    if (!hkFacility) {
      setText("editor-feedback", "Select a facility before publishing a change.");
      return;
    }

    try {
      const payload = await fetchJson(`/api/editor/facilities/${encodeURIComponent(hkFacility)}`, {
        method: "PATCH",
        body: JSON.stringify({
          facilityName: byId("facility-name-input")?.value || "",
          country: byId("facility-country-input")?.value || "",
          gridRegion: byId("facility-region-input")?.value || ""
        })
      });

      setNote("editor-feedback", payload.message || "Facility version published.", "success");
      pulseSelector(".live-editor", "is-updated", 1600);
      await refreshFacilityRows();
      await refreshLiveData(true);
    } catch (error) {
      setNote("editor-feedback", error.message, "error");
    }
  }

  function buildFacilityExamples() {
    const activeFacility =
      state.facilityRows.find((row) => row.hkFacility === byId("facility-select")?.value) ||
      state.facilityRows[0] ||
      {};

    const currentName = String(activeFacility.facilityName || "Demo Facility").trim();
    const cleanName = currentName.replace(/\s+LIVE DEMO$/i, "").trim();

    return [
      {
        label: "Demo rename",
        description: "Adds a visible demo suffix so you can publish and instantly show the changed facility name.",
        values: {
          facilityName: `${cleanName} LIVE DEMO`,
          country: String(activeFacility.country || "IN").toUpperCase(),
          gridRegion: String(activeFacility.gridRegion || "DEMO REGION").toUpperCase()
        }
      },
      {
        label: "Region shift",
        description: "Keeps the same facility and country, but changes the grid region for a quick presentation edit.",
        values: {
          facilityName: currentName,
          country: String(activeFacility.country || "IN").toUpperCase(),
          gridRegion: "DEMO REGION"
        }
      },
      {
        label: "Presentation sample",
        description: "Loads a polished sample change you can publish directly during the demo.",
        values: {
          facilityName: `${cleanName} Sustainability Hub`,
          country: "IN",
          gridRegion: "WEST GRID"
        }
      },
      {
        label: "Reset form",
        description: "Restores the form to the currently selected facility values.",
        values: {
          facilityName: String(activeFacility.facilityName || ""),
          country: String(activeFacility.country || "").toUpperCase(),
          gridRegion: String(activeFacility.gridRegion || "").toUpperCase()
        }
      }
    ];
  }

  function ensureFacilityExamplesUi() {
    const form = byId("facility-editor-form");
    const nameInput = byId("facility-name-input");
    const countryInput = byId("facility-country-input");
    const regionInput = byId("facility-region-input");
    const saveButton = byId("facility-save-button");
    if (!form || !nameInput || !countryInput || !regionInput) {
      return;
    }

    let wrapper = byId("facility-example-panel");
    if (!wrapper) {
      wrapper = document.createElement("div");
      wrapper.id = "facility-example-panel";
      wrapper.className = "result-panel";
      wrapper.style.marginBottom = "16px";
      wrapper.innerHTML = `
        <div class="result-summary">Publish facility examples</div>
        <p id="facility-example-note" style="margin: 8px 0 12px; opacity: 0.85;">
          Load a sample edit, then publish it to create a new facility satellite version live.
        </p>
        <div id="facility-example-buttons" style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;"></div>
        <div id="facility-example-description" style="font-size: 0.95rem; opacity: 0.8;"></div>
      `;
      form.insertBefore(wrapper, form.firstChild);
    }

    const buttonsHost = byId("facility-example-buttons");
    const descriptionHost = byId("facility-example-description");
    if (!buttonsHost || !descriptionHost) {
      return;
    }

    const disabled = Boolean(saveButton?.disabled);
    const examples = buildFacilityExamples();
    buttonsHost.innerHTML = "";
    descriptionHost.textContent = disabled
      ? "Examples are visible, but publishing will stay disabled until the live warehouse reconnects."
      : "Pick a sample, tweak the values if needed, and publish to show the update instantly.";

    examples.forEach((example, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = example.label;
      button.disabled = disabled;
      button.style.padding = "8px 12px";
      button.style.borderRadius = "999px";
      button.style.border = "1px solid rgba(255,255,255,0.18)";
      button.style.background = index === 0 ? "rgba(72, 187, 120, 0.18)" : "rgba(255,255,255,0.06)";
      button.style.color = "inherit";
      button.style.cursor = disabled ? "not-allowed" : "pointer";
      button.style.opacity = disabled ? "0.55" : "1";
      button.addEventListener("click", () => {
        nameInput.value = example.values.facilityName;
        countryInput.value = example.values.country;
        regionInput.value = example.values.gridRegion;
        descriptionHost.textContent = example.description;
        setNote(
          "editor-feedback",
          `${example.label} loaded. You can edit the values before publishing.`,
          "info"
        );
      });
      buttonsHost.appendChild(button);
    });
  }

  function renderSqlResults(payload) {
    const target = byId("sql-results");
    if (!target) {
      return;
    }

    if (payload.mode === "select") {
      if (!payload.rows?.length) {
        target.innerHTML = '<div class="result-panel">The statement ran successfully, but returned 0 rows.</div>';
        return;
      }

      const head = payload.columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("");
      const rows = payload.rows
        .map(
          (row) =>
            `<tr>${payload.columns
              .map((column) => `<td>${escapeHtml(row[column] ?? "")}</td>`)
              .join("")}</tr>`
        )
        .join("");

      target.innerHTML = `
        <div class="result-panel is-updated">
          <div class="result-summary">Returned ${payload.rowCount} row(s).</div>
          <div class="table-scroll">
            <table class="result-table">
              <thead><tr>${head}</tr></thead>
              <tbody>${rows}</tbody>
            </table>
          </div>
        </div>
      `;
      return;
    }

    target.innerHTML = `
        <div class="result-panel is-updated">
          <div class="result-summary">${payload.message || "Statement executed successfully."}</div>
          <p>${payload.rowsAffected ?? 0} row(s) affected.</p>
        </div>
      `;
  }

  async function handleSqlSubmit(event) {
    event.preventDefault();

    const sql = byId("sql-input")?.value || "";
    if (!sql.trim()) {
      setText("sql-feedback", "Enter a statement before running the console.");
      return;
    }

    try {
      const payload = await fetchJson("/api/sql/execute", {
        method: "POST",
        body: JSON.stringify({ sql })
      });
      setNote("sql-feedback", payload.message || "Statement executed successfully.", "success");
      renderSqlResults(payload);
      pulseSelector(".sql-console", "is-updated", 1600);
      await refreshLiveData(true);
      await refreshFacilityRows();
    } catch (error) {
      setNote("sql-feedback", error.message, "error");
      setHtml("sql-results", `<div class="result-panel is-error">${escapeHtml(error.message)}</div>`);
    }
  }

  function buildSqlExamples() {
    const activeFacility =
      state.facilityRows.find((row) => row.hkFacility === byId("facility-select")?.value) ||
      state.facilityRows[0] ||
      {};

    const facilityId = escapeSqlLiteral(activeFacility.hkFacility || "");
    const facilityName = escapeSqlLiteral(activeFacility.facilityName || "");

    return [
      {
        label: "Latest facilities",
        description: "Fast SELECT demo for the latest facility satellite rows.",
        sql:
          "SELECT facility_name, country, grid_region, load_dts\n" +
          "FROM sat_facility_attr\n" +
          "ORDER BY load_dts DESC\n" +
          "LIMIT 8;"
      },
      {
        label: "Selected facility",
        description: "Shows the currently selected facility so you can edit the filter live.",
        sql:
          "SELECT facility_name, country, grid_region, load_dts\n" +
          "FROM sat_facility_attr\n" +
          `WHERE hk_facility = '${facilityId}'\n` +
          "ORDER BY load_dts DESC\n" +
          "LIMIT 5;"
      },
      {
        label: "Emission ranking",
        description: "Good presentation query for live dashboard-style ranking output.",
        sql:
          "SELECT latest.facility_name,\n" +
          "       latest.grid_region,\n" +
          "       COALESCE(s2.total_scope2, 0) AS scope2_kg,\n" +
          "       COALESCE(s3.total_scope3, 0) AS scope3_kg,\n" +
          "       COALESCE(s2.total_scope2, 0) + COALESCE(s3.total_scope3, 0) AS total_kg\n" +
          "FROM (\n" +
          "    SELECT fa.hk_facility, fa.facility_name, fa.grid_region\n" +
          "    FROM sat_facility_attr fa\n" +
          "    JOIN (\n" +
          "        SELECT hk_facility, MAX(load_dts) AS max_load_dts\n" +
          "        FROM sat_facility_attr\n" +
          "        GROUP BY hk_facility\n" +
          "    ) latest_fa\n" +
          "      ON latest_fa.hk_facility = fa.hk_facility\n" +
          "     AND latest_fa.max_load_dts = fa.load_dts\n" +
          ") latest\n" +
          "LEFT JOIN (\n" +
          "    SELECT hk_facility, SUM(scope2_kgco2e) AS total_scope2\n" +
          "    FROM bv_scope2_emission_event\n" +
          "    GROUP BY hk_facility\n" +
          ") s2\n" +
          "  ON s2.hk_facility = latest.hk_facility\n" +
          "LEFT JOIN (\n" +
          "    SELECT hk_facility, SUM(scope3_kgco2e) AS total_scope3\n" +
          "    FROM bv_scope3_emission_event\n" +
          "    GROUP BY hk_facility\n" +
          ") s3\n" +
          "  ON s3.hk_facility = latest.hk_facility\n" +
          "ORDER BY total_kg DESC, latest.facility_name ASC\n" +
          "LIMIT 5;"
      },
      {
        label: "Update template",
        description: "Editable UPDATE demo. Change the values, then run it and refresh to show live impact.",
        sql:
          "UPDATE sat_facility_attr\n" +
          `SET facility_name = '${facilityName || "Demo Facility"} LIVE',\n` +
          "    grid_region = 'DEMO REGION'\n" +
          `WHERE hk_facility = '${facilityId}'\n` +
          "ORDER BY load_dts DESC\n" +
          "LIMIT 1;"
      }
    ];
  }

  function ensureSqlExamplesUi() {
    const form = byId("sql-form");
    const sqlInput = byId("sql-input");
    if (!form || !sqlInput) {
      return;
    }

    let wrapper = byId("sql-example-panel");
    if (!wrapper) {
      wrapper = document.createElement("div");
      wrapper.id = "sql-example-panel";
      wrapper.className = "result-panel";
      wrapper.style.marginBottom = "16px";
      wrapper.innerHTML = `
        <div class="result-summary">Live SQL examples</div>
        <p id="sql-example-note" style="margin: 8px 0 12px; opacity: 0.85;">
          Pick an example, edit the SQL, and run it to show live backend results.
        </p>
        <div id="sql-example-buttons" style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;"></div>
        <div id="sql-example-description" style="font-size: 0.95rem; opacity: 0.8;"></div>
      `;
      form.insertBefore(wrapper, sqlInput.parentElement || form.firstChild);
    }

    const buttonsHost = byId("sql-example-buttons");
    const descriptionHost = byId("sql-example-description");
    if (!buttonsHost || !descriptionHost) {
      return;
    }

    const examples = buildSqlExamples();
    buttonsHost.innerHTML = "";
    descriptionHost.textContent =
      "Use the selected facility example to show dynamic filtering, or the update template to demonstrate a live edit.";

    examples.forEach((example, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = example.label;
      button.style.padding = "8px 12px";
      button.style.borderRadius = "999px";
      button.style.border = "1px solid rgba(255,255,255,0.18)";
      button.style.background = index === 0 ? "rgba(72, 187, 120, 0.18)" : "rgba(255,255,255,0.06)";
      button.style.color = "inherit";
      button.style.cursor = "pointer";
      button.addEventListener("click", () => {
        sqlInput.value = example.sql;
        descriptionHost.textContent = example.description;
        setNote(
          "sql-feedback",
          `${example.label} loaded. You can edit the SQL before running it.`,
          "info"
        );
      });
      buttonsHost.appendChild(button);
    });
  }

  function bindControls() {
    const refreshButton = byId("live-refresh-button");
    if (refreshButton && refreshButton.dataset.bound !== "true") {
      refreshButton.dataset.bound = "true";
      refreshButton.addEventListener("click", async () => {
        setText("live-source-text", "Refreshing the live warehouse view...");
        setRefreshButtonState(true);
        pulseSelector(".live-monitor", "is-updated", 1200);
        try {
          await refreshLiveData(true);
          await refreshFacilityRows();
        } catch (error) {
          setText("live-source-text", error.message);
        } finally {
          setRefreshButtonState(false);
        }
      });
    }

    const autoRefreshToggle = byId("auto-refresh-toggle");
    if (autoRefreshToggle && autoRefreshToggle.dataset.bound !== "true") {
      autoRefreshToggle.dataset.bound = "true";
      autoRefreshToggle.checked = state.autoRefresh;
      autoRefreshToggle.addEventListener("change", () => {
        state.autoRefresh = autoRefreshToggle.checked;
      });
    }

    const select = byId("facility-select");
    if (select && select.dataset.bound !== "true") {
      select.dataset.bound = "true";
      select.addEventListener("change", () => {
        populateFacilityForm(select.value);
        ensureFacilityExamplesUi();
        ensureSqlExamplesUi();
      });
    }

    const facilityForm = byId("facility-editor-form");
    if (facilityForm && facilityForm.dataset.bound !== "true") {
      facilityForm.dataset.bound = "true";
      facilityForm.addEventListener("submit", handleFacilitySave);
    }

    const sqlForm = byId("sql-form");
    if (sqlForm && sqlForm.dataset.bound !== "true") {
      sqlForm.dataset.bound = "true";
      sqlForm.addEventListener("submit", handleSqlSubmit);
    }
  }

  function connectLiveStream() {
    if (!("EventSource" in window)) {
      state.fallbackTimer = window.setInterval(() => {
        if (state.autoRefresh) {
          refreshLiveData(false).catch(() => {});
        }
      }, 12000);
      return;
    }

    state.eventSource = new EventSource("/api/live-events");
    state.eventSource.onmessage = () => {
      if (state.autoRefresh) {
        refreshLiveData(false).catch(() => {});
      }
    };
    state.eventSource.onerror = () => {
      if (!state.fallbackTimer) {
        state.fallbackTimer = window.setInterval(() => {
          if (state.autoRefresh) {
            refreshLiveData(false).catch(() => {});
          }
        }, 12000);
      }
    };
  }

  async function boot() {
    bindControls();
    connectLiveStream();
    ensureFacilityExamplesUi();
    ensureSqlExamplesUi();

    try {
      await refreshLiveData(true);
      await refreshFacilityRows();
      ensureSqlExamplesUi();
    } catch (error) {
      updateStatus(
        {
          source: "snapshot",
          lastUpdated: new Date().toISOString(),
          error: error.message
        },
        window.greenTraceData?.overview
      );
      setNote("editor-feedback", error.message, "error");
      setNote("sql-feedback", error.message, "error");
    }
  }

  window.addEventListener("DOMContentLoaded", boot);
})();
