// const apiBase = "http://127.0.0.1:8000/api/tasks";
const apiBase = "https://task-analyzer-pe7x.onrender.com/api/tasks";

const tasksLocal = [];

document.getElementById("task-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const title = document.getElementById("title").value.trim();
  const due_date = document.getElementById("due_date").value || null;
  const estimated_hours = document.getElementById("estimated_hours").value ? parseFloat(document.getElementById("estimated_hours").value) : null;
  const importance = document.getElementById("importance").value ? parseFloat(document.getElementById("importance").value) : null;
  const depsRaw = document.getElementById("dependencies").value.trim();
  const dependencies = depsRaw ? depsRaw.split(",").map(s => s.trim()).filter(Boolean) : [];
  const id = `local-${Date.now()}`;
  const t = { id, title, due_date, estimated_hours, importance, dependencies };
  tasksLocal.unshift(t);
  showMessage("Task added locally.");
  document.getElementById("task-form").reset();
  renderLocal();
});

document.getElementById("analyze").addEventListener("click", async () => {
  const bulk = document.getElementById("bulk").value.trim();
  let tasks = tasksLocal.slice();
  if (bulk) {
    try {
      const parsed = JSON.parse(bulk);
      if (Array.isArray(parsed)) tasks = parsed.concat(tasks);
      else return showMessage("Bulk JSON must be an array.", true)
    } catch (e) {
      return showMessage("Invalid JSON in bulk input.", true);
    }
  }
  if (tasks.length === 0) return showMessage("No tasks to analyze.", true);
  const strategy = document.getElementById("strategy").value;
  showMessage("Analyzing...", false, true);
  try {
    const res = await fetch(`${apiBase}/analyze/`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ tasks, strategy })
    });
    const body = await res.json();
    if (!res.ok) {
      showMessage(JSON.stringify(body), true);
      return;
    }
    renderResults(body.results);
    showMessage("Analysis complete.");
  } catch (err) {
    showMessage("Network error: " + err.message, true);
  }
});

document.getElementById("suggest").addEventListener("click", async () => {
  const bulk = document.getElementById("bulk").value.trim();
  let tasks = tasksLocal.slice();
  if (bulk) {
    try {
      const parsed = JSON.parse(bulk);
      if (Array.isArray(parsed)) tasks = parsed.concat(tasks);
      else return showMessage("Bulk JSON must be an array.", true)
    } catch (e) {
      return showMessage("Invalid JSON in bulk input.", true);
    }
  }
  if (tasks.length === 0) return showMessage("No tasks to suggest.", true);
  const strategy = document.getElementById("strategy").value;
  showMessage("Fetching suggestions...", false, true);
  try {
    const res = await fetch(`${apiBase}/suggest/`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ tasks, strategy })
    });
    const body = await res.json();
    if (!res.ok) {
      showMessage(JSON.stringify(body), true);
      return;
    }
    const suggestions = body.suggestions || [];
    renderResults(suggestions.map(s => {
      return {
        id: s.id,
        title: s.title,
        score: s.score,
        raw: {},
        explanation: s.why
      };
    }), true);
    showMessage("Top 3 suggestions displayed.");
  } catch (err) {
    showMessage("Network error: " + err.message, true);
  }
});

function renderLocal(){
  const el = document.getElementById("results");
  const localHtml = tasksLocal.map(t=>`<div class="task small"><strong>${escapeHtml(t.title)}</strong> <div class="small">ID: ${escapeHtml(t.id)}</div></div>`).join("");
  el.innerHTML = `<h3>Local tasks (${tasksLocal.length})</h3>` + localHtml;
}

function renderResults(results, emphasize=false){
  const el = document.getElementById("results");
  let html = results.map(r=>{
    let label = "low";
    if (r.score >= 0.7) label = "high";
    else if (r.score >= 0.4) label = "medium";
    const due = r.raw && r.raw.due_date ? r.raw.due_date : (r.due_date || "—");
    const hours = r.raw && r.raw.estimated_hours ? r.raw.estimated_hours : (r.estimated_hours || "—");
    const importance = r.raw && r.raw.importance ? r.raw.importance : (r.importance || "—");
    return `<div class="task ${label}">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <div class="score">${escapeHtml(r.title || r.id)} <span class="small">(${escapeHtml(r.id)})</span></div>
          <div class="small">Due: ${escapeHtml(String(due))} | Hours: ${escapeHtml(String(hours))} | Importance: ${escapeHtml(String(importance))}</div>
        </div>
        <div style="text-align:right">
          <div>Score: ${escapeHtml(String(r.score))}</div>
        </div>
      </div>
      <div class="small" style="margin-top:8px">${escapeHtml(r.explanation || r.why || '')}</div>
    </div>`;
  }).join("");
  el.innerHTML = html || "<div class='small'>No results yet.</div>";
}

function showMessage(msg, isError=false, loading=false){
  console[isError ? 'error' : 'log'](msg);
  // optional: you can implement a UI toast here.
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
