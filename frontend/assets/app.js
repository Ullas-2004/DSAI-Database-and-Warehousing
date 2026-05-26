function formatNumber(value, decimals) {
  return new Intl.NumberFormat("en-IN", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value);
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

function toFiniteNumber(value, fallback = 0) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : fallback;
}

function formatCount(value, format, decimals) {
  if (format === "decimal") {
    return formatNumber(value, decimals ?? 2);
  }

  return formatNumber(Math.round(value), 0);
}

function createCounterMarkup(item) {
  const decimals = toFiniteNumber(item.decimals ?? (item.format === "decimal" ? 2 : 0), 0);
  const rawPrefix = item.prefix ?? "";
  const rawSuffix = item.suffix ?? "";
  const prefix = escapeHtml(rawPrefix);
  const suffix = escapeHtml(rawSuffix);
  const label = escapeHtml(item.label);
  const note = escapeHtml(item.note);
  const value = toFiniteNumber(item.value, 0);
  const format = item.format === "decimal" ? "decimal" : "integer";

  return `
    <article class="metric-card glass-card reveal">
      <div class="metric-value" data-count-target="${value}" data-count-format="${format}" data-count-decimals="${decimals}" data-count-prefix="${escapeAttribute(rawPrefix)}" data-count-suffix="${escapeAttribute(rawSuffix)}">
        ${prefix}0${suffix}
      </div>
      <h3>${label}</h3>
      <p>${note}</p>
    </article>
  `;
}

function createFeatureMarkup(item, index) {
  return `
    <article class="feature-card glass-card reveal" style="transition-delay:${index * 0.08}s">
      <span class="kicker">Capability 0${index + 1}</span>
      <h3>${escapeHtml(item.title)}</h3>
      <p>${escapeHtml(item.body)}</p>
    </article>
  `;
}

function createLayerMarkup(layer, index) {
  return `
    <article class="layer-card glass-card reveal" style="transition-delay:${index * 0.08}s">
      <span class="kicker">${escapeHtml(layer.stat)}</span>
      <h3>${escapeHtml(layer.name)}</h3>
      <p>${escapeHtml(layer.description)}</p>
    </article>
  `;
}

function createStoryMarkup(panel, index) {
  return `
    <article class="story-card glass-card reveal" style="transition-delay:${index * 0.08}s">
      <span class="story-index">${escapeHtml(panel.page)}</span>
      <h3>${escapeHtml(panel.title)}</h3>
      <p>${escapeHtml(panel.body)}</p>
    </article>
  `;
}

function renderRegionChart(container, rows) {
  if (!container) {
    return;
  }

  const max = rows.reduce((current, item) => Math.max(current, item.totalKg), 0);
  container.innerHTML = rows
    .map((item, index) => {
      const fill = max > 0 ? `${(item.totalKg / max) * 100}%` : "0%";
      return `
        <article class="region-row glass-card reveal" style="transition-delay:${index * 0.06}s">
          <div class="region-meta">
            <span class="region-label">${escapeHtml(item.region)}</span>
            <strong>${formatNumber(toFiniteNumber(item.totalKg, 0), 2)} kgCO2e</strong>
          </div>
          <div class="region-track">
            <div class="region-fill" style="--fill:${fill}"></div>
          </div>
        </article>
      `;
    })
    .join("");

  requestAnimationFrame(() => container.classList.add("is-mounted"));
}

function renderFacilityTable(container, rows) {
  if (!container) {
    return;
  }

  const tableRows = rows
    .map(
      (item, index) => `
        <tr class="reveal" style="transition-delay:${index * 0.05}s">
          <td><span class="rank-pill">0${index + 1}</span></td>
          <td>
            <strong>${escapeHtml(item.facility)}</strong>
            <span>${escapeHtml(item.region)}</span>
          </td>
          <td>${formatNumber(toFiniteNumber(item.scope2Kg, 0), 2)}</td>
          <td>${formatNumber(toFiniteNumber(item.scope3Kg, 0), 2)}</td>
          <td>${formatNumber(toFiniteNumber(item.totalKg, 0), 2)}</td>
        </tr>
      `
    )
    .join("");

  container.innerHTML = `
    <div class="table-wrap glass-card">
      <table class="leader-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Facility</th>
            <th>Scope 2</th>
            <th>Scope 3</th>
            <th>Total kgCO2e</th>
          </tr>
        </thead>
        <tbody>${tableRows}</tbody>
      </table>
    </div>
  `;
}

function renderLoadChart(container, rows, overview = {}) {
  if (!container) {
    return;
  }

  const safeRows = Array.isArray(rows) ? rows : [];

  if (!safeRows.length) {
    container.innerHTML = `
      <div class="result-panel">
        No interval data is available for the current dashboard view.
      </div>
    `;
    return;
  }

  const max = safeRows.reduce((current, item) => Math.max(current, toFiniteNumber(item.totalKg, 0)), 0);
  const sortedRows = [...safeRows].sort(
    (left, right) => toFiniteNumber(right.totalKg, 0) - toFiniteNumber(left.totalKg, 0)
  );
  const peakRow = sortedRows[0] || safeRows[0];
  const quietRow = [...safeRows].sort(
    (left, right) => toFiniteNumber(left.totalKg, 0) - toFiniteNumber(right.totalKg, 0)
  )[0] || safeRows[0];

  const barsMarkup = safeRows
    .map((item, index) => {
      const totalKg = toFiniteNumber(item.totalKg, 0);
      const heightPx = max > 0 ? Math.max((totalKg / max) * 320, totalKg > 0 ? 30 : 0) : 0;
      const peakClass = item.slot === peakRow?.slot ? "is-peak" : "";
      return `
        <article
          class="load-bar-wrap reveal ${peakClass}"
          style="transition-delay:${index * 0.02}s; height: 380px; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; gap: 10px;"
        >
          <div
            class="load-bar"
            title="${escapeAttribute(item.slot)} - ${formatNumber(totalKg, 2)} kgCO2e"
            style="height:${heightPx}px; width: min(100%, 34px); min-height:${totalKg > 0 ? "30px" : "0"}; border-radius: 999px 999px 12px 12px; background: linear-gradient(180deg, rgba(234, 205, 152, 0.98) 0%, rgba(176, 129, 65, 0.92) 100%); box-shadow: 0 14px 30px rgba(176, 129, 65, 0.18);"
          ></div>
          <span style="font-size: 0.95rem;">${escapeHtml(item.slot)}</span>
        </article>
      `;
    })
    .join("");

  container.innerHTML = `
    <div style="display: grid; gap: 18px; min-height: 520px;">
      <div style="display: flex; flex-wrap: wrap; gap: 14px; align-items: center; justify-content: space-between; padding: 4px 2px 0;">
        <div style="font-size: 1rem; opacity: 0.82;">Each bar shows one recorded time slot from your data. Taller bars mean higher emissions activity.</div>
        <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.98rem;">
          <span><strong>Peak hour:</strong> ${escapeHtml(peakRow?.slot || "N/A")}</span>
          <span><strong>Quietest slot:</strong> ${escapeHtml(quietRow?.slot || "N/A")}</span>
        </div>
      </div>
      <div style="display: grid; grid-template-columns: repeat(${safeRows.length}, minmax(24px, 1fr)); align-items: end; gap: 12px; min-height: 440px; padding: 12px 6px 0; border-top: 1px solid rgba(255,255,255,0.08);">
        ${barsMarkup}
      </div>
    </div>
  `;

  requestAnimationFrame(() => container.classList.add("is-mounted"));
}

function renderMixCards(container, title, rows, suffix) {
  if (!container) {
    return;
  }

  container.innerHTML = `
      <div class="mix-card glass-card reveal">
      <div class="mix-header">
        <span class="kicker">Composition</span>
        <h3>${escapeHtml(title)}</h3>
      </div>
      <div class="mix-list">
        ${rows
          .map(
            (item, index) => `
              <div class="mix-row" style="transition-delay:${index * 0.05}s">
                <span>${escapeHtml(item.label)}</span>
                <strong>${escapeHtml(item.count)}${escapeHtml(suffix ?? "")}</strong>
              </div>
            `
          )
          .join("")}
      </div>
    </div>
  `;
}

function renderPhaseTimeline(container, rows) {
  if (!container) {
    return;
  }

  container.innerHTML = rows
    .map(
      (item, index) => `
        <article class="phase-card glass-card reveal" style="transition-delay:${index * 0.05}s">
          <span class="kicker">${escapeHtml(item.phase)}</span>
          <h3>${escapeHtml(item.title)}</h3>
          <p>${escapeHtml(item.body)}</p>
        </article>
      `
    )
    .join("");
}

function renderSchemaGrid(container, rows) {
  if (!container) {
    return;
  }

  container.innerHTML = rows
    .map(
      (item, index) => `
        <article class="schema-card glass-card reveal" style="transition-delay:${index * 0.05}s">
          <div class="schema-value">${escapeHtml(item.count)}</div>
          <h3>${escapeHtml(item.label)}</h3>
          <p>${escapeHtml(item.detail)}</p>
        </article>
      `
    )
    .join("");
}

function renderQueries(container, rows) {
  if (!container) {
    return;
  }

  container.innerHTML = rows
    .map(
      (item, index) => `
        <article class="query-card glass-card reveal" style="transition-delay:${index * 0.05}s">
          <div class="query-head">
            <span class="kicker">${escapeHtml(item.label)}</span>
            <h3>Analyst lens ${index + 1}</h3>
          </div>
          <pre>${escapeHtml(item.sql)}</pre>
          <p>${escapeHtml(item.result)}</p>
        </article>
      `
    )
    .join("");
}

function renderHomePage(data) {
  const heroStats = document.getElementById("hero-stats");
  const layerGrid = document.getElementById("layer-grid");
  const storyGrid = document.getElementById("story-grid");
  const featureGrid = document.getElementById("feature-grid");
  const heroPeriod = document.getElementById("hero-period");
  const heroTotal = document.getElementById("hero-total");
  const heroLine = document.getElementById("hero-line");

  if (heroStats) {
    heroStats.innerHTML = data.heroHighlights.map(createCounterMarkup).join("");
  }

  if (layerGrid) {
    layerGrid.innerHTML = data.architectureLayers.map(createLayerMarkup).join("");
  }

  if (storyGrid) {
    storyGrid.innerHTML = data.storyPanels.map(createStoryMarkup).join("");
  }

  if (featureGrid) {
    featureGrid.innerHTML = data.featureCards.map(createFeatureMarkup).join("");
  }

  if (heroPeriod) {
    heroPeriod.textContent = String(data.overview.reportingPeriod ?? "");
  }

  if (heroTotal) {
    heroTotal.textContent = `${formatNumber(toFiniteNumber(data.overview.totalKg, 0) / 1000, 2)} tCO2e`;
  }

  if (heroLine) {
    heroLine.textContent = String(data.overview.narrative ?? "");
  }
}

function renderDashboardPage(data) {
  const kpiGrid = document.getElementById("kpi-grid");
  const regionChart = document.getElementById("region-chart");
  const facilityTable = document.getElementById("facility-table");
  const loadChart = document.getElementById("load-chart");
  const vehicleMix = document.getElementById("vehicle-mix");
  const sectorMix = document.getElementById("sector-mix");
  const dashboardTotal = document.getElementById("dashboard-total");
  const dashboardScope = document.getElementById("dashboard-scope");

  if (kpiGrid) {
    kpiGrid.innerHTML = data.kpis.map(createCounterMarkup).join("");
  }

  renderRegionChart(regionChart, data.regionTotals);
  renderFacilityTable(facilityTable, data.facilityLeaders);
  renderLoadChart(loadChart, data.intervalLoad, data.overview);
  renderMixCards(vehicleMix, "Shipment vehicle mix", data.vehicleMix, "");
  renderMixCards(sectorMix, "Supplier sector mix", data.supplierSectors, "");

  if (dashboardTotal) {
    dashboardTotal.textContent = `${formatNumber(toFiniteNumber(data.overview.totalKg, 0) / 1000, 2)} tCO2e`;
  }

  if (dashboardScope) {
    const totalKg = toFiniteNumber(data.overview.totalKg, 0);
    const scope2Pct = totalKg ? (toFiniteNumber(data.overview.scope2Kg, 0) / totalKg) * 100 : 0;
    const scope3Pct = totalKg ? (toFiniteNumber(data.overview.scope3Kg, 0) / totalKg) * 100 : 0;
    dashboardScope.textContent = `${formatNumber(
      scope2Pct,
      1
    )}% scope 2 / ${formatNumber(
      scope3Pct,
      1
    )}% scope 3`;
  }
}

function renderArchitecturePage(data) {
  const layerGrid = document.getElementById("architecture-layer-grid");
  const phaseTimeline = document.getElementById("phase-timeline");
  const schemaGrid = document.getElementById("schema-grid");
  const queryGrid = document.getElementById("query-grid");
  const readiness = document.getElementById("lineage-readiness");

  if (layerGrid) {
    layerGrid.innerHTML = data.architectureLayers.map(createLayerMarkup).join("");
  }

  renderPhaseTimeline(phaseTimeline, data.phases);
  renderSchemaGrid(schemaGrid, data.schemaCounts);
  renderQueries(queryGrid, data.queries);

  if (readiness) {
    readiness.textContent =
      "The lineage edge table leaves room for future transformation playback, audit storytelling, and proof of traceability.";
  }
}

function initCounters() {
  const counters = document.querySelectorAll("[data-count-target]");

  if (!counters.length) {
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting || entry.target.dataset.countStarted === "true") {
          return;
        }

        entry.target.dataset.countStarted = "true";
        observer.unobserve(entry.target);

        const target = Number(entry.target.dataset.countTarget);
        const format = entry.target.dataset.countFormat || "integer";
        const decimals = Number(entry.target.dataset.countDecimals || 0);
        const prefix = entry.target.dataset.countPrefix || "";
        const suffix = entry.target.dataset.countSuffix || "";
        const duration = 1200;
        const start = performance.now();

        const step = (now) => {
          const progress = Math.min((now - start) / duration, 1);
          const eased = 1 - Math.pow(1 - progress, 3);
          const value = target * eased;
          entry.target.textContent = `${prefix}${formatCount(value, format, decimals)}${suffix}`;

          if (progress < 1) {
            requestAnimationFrame(step);
          }
        };

        requestAnimationFrame(step);
      });
    },
    { threshold: 0.45 }
  );

  counters.forEach((counter) => observer.observe(counter));
}

function initRevealObserver() {
  const revealTargets = document.querySelectorAll(".reveal");

  if (!revealTargets.length) {
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.2,
      rootMargin: "0px 0px -8% 0px"
    }
  );

  revealTargets.forEach((target) => observer.observe(target));
}

function bindPageTransitions() {
  const links = document.querySelectorAll("a[data-transition]");

  links.forEach((link) => {
    if (link.dataset.transitionBound === "true") {
      return;
    }

    link.dataset.transitionBound = "true";
    link.addEventListener("click", (event) => {
      if (
        event.defaultPrevented ||
        event.metaKey ||
        event.ctrlKey ||
        event.shiftKey ||
        event.altKey ||
        link.target === "_blank" ||
        !link.href ||
        link.getAttribute("href").startsWith("#")
      ) {
        return;
      }

      event.preventDefault();
      document.body.classList.add("is-transitioning");

      window.setTimeout(() => {
        window.location.href = link.href;
      }, 280);
    });
  });
}

function bindLiveStudioOverlay() {
  const overlay = document.getElementById("live-studio-overlay");

  if (!overlay || overlay.dataset.overlayBound === "true") {
    return;
  }

  overlay.dataset.overlayBound = "true";

  const openButtons = document.querySelectorAll("[data-open-live-studio]");
  const closeButtons = overlay.querySelectorAll("[data-close-live-studio]");
  const focusTarget = overlay.querySelector(".studio-close");
  let previousFocus = null;

  function openOverlay() {
    previousFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    document.body.classList.add("is-live-studio-open");
    overlay.setAttribute("aria-hidden", "false");

    window.requestAnimationFrame(() => {
      focusTarget?.focus();
    });
  }

  function closeOverlay() {
    document.body.classList.remove("is-live-studio-open");
    overlay.setAttribute("aria-hidden", "true");

    if (previousFocus && typeof previousFocus.focus === "function") {
      previousFocus.focus();
    }
  }

  openButtons.forEach((button) => {
    button.addEventListener("click", openOverlay);
  });

  closeButtons.forEach((button) => {
    button.addEventListener("click", closeOverlay);
  });

  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) {
      closeOverlay();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && document.body.classList.contains("is-live-studio-open")) {
      closeOverlay();
    }
  });
}

function markActiveNav() {
  const page = document.body.dataset.page;
  const navLinks = document.querySelectorAll("[data-nav]");

  navLinks.forEach((link) => {
    link.classList.toggle("is-active", link.dataset.nav === page);
  });
}

function setYear() {
  const yearTargets = document.querySelectorAll("[data-year]");
  const year = new Date().getFullYear();

  yearTargets.forEach((target) => {
    target.textContent = year;
  });
}

function markPageReady() {
  requestAnimationFrame(() => {
    document.body.classList.add("is-ready");
  });
}

function renderAll(data) {
  renderHomePage(data);
  renderDashboardPage(data);
  renderArchitecturePage(data);
  initRevealObserver();
  initCounters();
}

window.greenTraceApp = {
  renderAll,
  renderHomePage,
  renderDashboardPage,
  renderArchitecturePage,
  formatNumber
};

function boot() {
  markActiveNav();
  setYear();
  bindPageTransitions();
  bindLiveStudioOverlay();
  markPageReady();

  const data = window.greenTraceData;

  if (!data) {
    return;
  }

  renderAll(data);
}

window.addEventListener("DOMContentLoaded", boot);
