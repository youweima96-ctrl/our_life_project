const API_BASE = "/api";
const USER_ID = "demo-user";

const state = {
  scenario: "",
  draft: null
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `请求失败：${response.status}`);
  }

  return response.json();
}

function toast(message) {
  const node = $("#toast");
  node.textContent = message;
  node.classList.remove("hidden");
  window.setTimeout(() => node.classList.add("hidden"), 2600);
}

function switchView(viewId) {
  $$(".view").forEach((view) => view.classList.toggle("active", view.id === viewId));
  $$(".nav-item").forEach((button) => button.classList.toggle("active", button.dataset.view === viewId));

  if (viewId === "timeline") loadEvents();
  if (viewId === "rooms") loadRooms();
}

function setScenario(scenario) {
  state.scenario = scenario;
  $$("#scenarioRow button").forEach((button) => {
    button.classList.toggle("active", button.dataset.scenario === scenario);
  });
  $("#selectedScenario").textContent = scenario ? `已选择：${scenario}` : "未选择场景";
}

function renderExtraction(draft) {
  state.draft = draft;
  const output = draft.extraction.output_json;
  $("#confirmTitle").value = output.title;
  $("#confirmSummary").value = output.summary;
  $("#confirmType").value = output.event_type;
  $("#confirmVisibility").value = output.suggested_visibility;

  const tags = [...output.topic_tags, ...output.emotion_tags, ...output.need_tags];
  $("#tags").innerHTML = tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("");
  $("#questions").innerHTML = output.follow_up_questions
    .map((question) => `<div class="question">${escapeHtml(question)}</div>`)
    .join("");
  $("#confirmPanel").classList.remove("hidden");
}

async function extractRecord() {
  const raw = $("#rawContent").value.trim();
  if (!raw) {
    toast("先输入一段记录");
    return;
  }

  $("#extractButton").disabled = true;
  $("#extractButton").textContent = "整理中...";
  try {
    const draft = await api("/events/draft", {
      method: "POST",
      body: JSON.stringify({
        user_id: USER_ID,
        raw_content: raw,
        scenario: state.scenario || null
      })
    });
    renderExtraction(draft);
    toast("AI 整理完成");
  } catch (error) {
    toast(error.message);
  } finally {
    $("#extractButton").disabled = false;
    $("#extractButton").textContent = "AI 整理记录";
  }
}

async function confirmRecord() {
  if (!state.draft) {
    toast("没有待确认记录");
    return;
  }

  const payload = {
    title: $("#confirmTitle").value.trim(),
    summary: $("#confirmSummary").value.trim(),
    event_type: $("#confirmType").value.trim(),
    topic_tags: state.draft.extraction.output_json.topic_tags,
    emotion_tags: state.draft.extraction.output_json.emotion_tags,
    need_tags: state.draft.extraction.output_json.need_tags,
    visibility: $("#confirmVisibility").value.trim()
  };

  try {
    await api(`/events/${state.draft.event.id}/confirm`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
    $("#rawContent").value = "";
    $("#confirmPanel").classList.add("hidden");
    state.draft = null;
    toast("已保存到时间线");
    switchView("timeline");
  } catch (error) {
    toast(error.message);
  }
}

async function discardRecord() {
  if (!state.draft) return;
  await api(`/events/${state.draft.event.id}/discard`, { method: "POST" }).catch(() => {});
  state.draft = null;
  $("#confirmPanel").classList.add("hidden");
  toast("已丢弃");
}

async function loadEvents() {
  try {
    const events = await api(`/events?user_id=${encodeURIComponent(USER_ID)}`);
    $("#eventList").innerHTML = events.length
      ? events.map(renderEvent).join("")
      : '<div class="card"><div class="card-body">暂无已确认记录</div></div>';
  } catch (error) {
    toast(error.message);
  }
}

function renderEvent(event) {
  return `
    <article class="card">
      <div class="card-title">${escapeHtml(event.title)}</div>
      <div class="card-body">${escapeHtml(event.summary)}</div>
      <div class="card-meta">${escapeHtml(event.event_type)} · ${escapeHtml(event.visibility)} · ${new Date(event.event_time).toLocaleString()}</div>
    </article>
  `;
}

async function createRoom() {
  const name = $("#roomName").value.trim();
  if (!name) {
    toast("请输入房间名称");
    return;
  }

  try {
    await api("/rooms", {
      method: "POST",
      body: JSON.stringify({
        owner_user_id: USER_ID,
        name,
        room_type: "couple"
      })
    });
    $("#roomName").value = "";
    toast("房间已创建");
    loadRooms();
  } catch (error) {
    toast(error.message);
  }
}

async function loadRooms() {
  try {
    const rooms = await api(`/rooms?user_id=${encodeURIComponent(USER_ID)}`);
    $("#roomList").innerHTML = rooms.length
      ? rooms.map(renderRoom).join("")
      : '<div class="card"><div class="card-body">暂无房间</div></div>';
  } catch (error) {
    toast(error.message);
  }
}

function renderRoom(room) {
  return `
    <article class="card">
      <div class="card-title">${escapeHtml(room.name)}</div>
      <div class="card-body">邀请码：${escapeHtml(room.invite_code)}</div>
      <div class="card-meta">${escapeHtml(room.room_type)} · ${room.member_ids.length} 人</div>
    </article>
  `;
}

async function generateReport() {
  $("#generateReportButton").disabled = true;
  $("#generateReportButton").textContent = "生成中...";
  try {
    const report = await api("/reports/personal-weekly", {
      method: "POST",
      body: JSON.stringify({ user_id: USER_ID })
    });
    $("#reportPanel").textContent = report.content_markdown;
    toast("周报已生成");
  } catch (error) {
    toast(error.message);
  } finally {
    $("#generateReportButton").disabled = false;
    $("#generateReportButton").textContent = "生成个人周报";
  }
}

async function checkApi() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("bad status");
    $("#apiStatusDot").className = "dot ok";
    $("#apiStatus").textContent = "后端已连接";
  } catch (error) {
    $("#apiStatusDot").className = "dot bad";
    $("#apiStatus").textContent = "后端未连接";
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function bindEvents() {
  $$(".nav-item").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
  });
  $$("#scenarioRow button").forEach((button) => {
    button.addEventListener("click", () => setScenario(button.dataset.scenario));
  });
  $("#extractButton").addEventListener("click", extractRecord);
  $("#confirmButton").addEventListener("click", confirmRecord);
  $("#discardButton").addEventListener("click", discardRecord);
  $("#refreshEvents").addEventListener("click", loadEvents);
  $("#createRoomButton").addEventListener("click", createRoom);
  $("#generateReportButton").addEventListener("click", generateReport);
}

bindEvents();
checkApi();
loadEvents();
loadRooms();
