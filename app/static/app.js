const els = {
  status: document.querySelector("#system-status"),
  useAI: document.querySelector("#use-ai"),
  button: document.querySelector("#analyze-button"),
  loading: document.querySelector("#loading"),
  error: document.querySelector("#error"),
  result: document.querySelector("#result"),
  severity: document.querySelector("#severity"),
  mode: document.querySelector("#mode"),
  headline: document.querySelector("#headline"),
  summary: document.querySelector("#summary"),
  stormName: document.querySelector("#storm-name"),
  sourceCount: document.querySelector("#source-count"),
  modelUsed: document.querySelector("#model-used"),
  keyChanges: document.querySelector("#key-changes"),
  affectedAreas: document.querySelector("#affected-areas"),
  recommendedActions: document.querySelector("#recommended-actions"),
  sources: document.querySelector("#sources"),
  disclaimer: document.querySelector("#disclaimer"),
};

function setList(element, items) {
  element.replaceChildren(...items.map((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    return li;
  }));
}

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${detail}`);
  }
  return response.json();
}

async function loadHealth() {
  try {
    const health = await fetchJSON("/api/health");
    els.status.textContent = health.ai_enabled
      ? `GPT-5.6 ready · ${health.configured_model}`
      : "Demo mode · deterministic fallback";
    els.useAI.checked = health.ai_enabled;
  } catch (error) {
    els.status.textContent = "System status unavailable";
  }
}

async function loadSources() {
  const updates = await fetchJSON("/api/updates");
  els.sources.replaceChildren(...updates.map((update) => {
    const article = document.createElement("article");
    article.className = "source";

    const title = document.createElement("h4");
    title.textContent = update.title;

    const meta = document.createElement("small");
    meta.textContent = `${update.source} · ${new Date(update.observed_at).toLocaleString()}`;

    const content = document.createElement("p");
    content.textContent = update.content;

    article.append(title, meta, content);
    return article;
  }));
}

function renderResult(result) {
  els.severity.textContent = result.severity.toUpperCase();
  els.severity.dataset.level = result.severity;
  els.mode.textContent = result.mode === "ai" ? "GPT-5.6 analysis" : "Deterministic analysis";
  els.headline.textContent = result.headline;
  els.summary.textContent = result.summary;
  els.stormName.textContent = result.storm_name;
  els.sourceCount.textContent = String(result.source_count);
  els.modelUsed.textContent = result.model_used;
  setList(els.keyChanges, result.key_changes);
  setList(els.affectedAreas, result.affected_areas);
  setList(els.recommendedActions, result.recommended_actions);
  els.disclaimer.textContent = result.disclaimer;
}

async function analyze() {
  els.button.disabled = true;
  els.loading.classList.remove("hidden");
  els.error.classList.add("hidden");
  els.result.classList.add("hidden");

  try {
    const result = await fetchJSON("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ updates: [], use_ai: els.useAI.checked }),
    });
    renderResult(result);
    await loadSources();
    els.result.classList.remove("hidden");
  } catch (error) {
    els.error.textContent = `Analysis failed: ${error.message}`;
    els.error.classList.remove("hidden");
  } finally {
    els.loading.classList.add("hidden");
    els.button.disabled = false;
  }
}

els.button.addEventListener("click", analyze);
loadHealth();
analyze();
