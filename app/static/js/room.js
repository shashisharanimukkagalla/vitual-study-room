const workspace = document.querySelector(".study-layout");

if (workspace) {
  const roomId = workspace.dataset.roomId;
  const username = workspace.dataset.user;
  const socket = io();
  const messages = document.querySelector("#messages");
  const chatForm = document.querySelector("#chat-form");
  const chatInput = document.querySelector("#chat-input");
  const timerDisplay = document.querySelector("#timer-display");
  const csrfToken = document.querySelector("#csrf-token")?.value || "";
  let remaining = 25 * 60;
  let defaultSeconds = remaining;
  let timerHandle = null;
  let sessionRecorded = false;

  function appendMessage({ user, content, time, system = false }) {
    const item = document.createElement("p");
    if (system) {
      item.className = "system";
      item.textContent = content;
    } else {
      const name = document.createElement("strong");
      const stamp = document.createElement("span");
      const lineBreak = document.createElement("br");
      name.textContent = user;
      stamp.textContent = ` ${time}`;
      item.append(name, stamp, lineBreak, document.createTextNode(content));
    }
    messages.appendChild(item);
    messages.scrollTop = messages.scrollHeight;
  }

  function renderTimer() {
    const minutes = Math.floor(remaining / 60).toString().padStart(2, "0");
    const seconds = (remaining % 60).toString().padStart(2, "0");
    timerDisplay.textContent = `${minutes}:${seconds}`;
  }

  function broadcastTimer(state) {
    socket.emit("timer_update", { room_id: roomId, state, remaining, defaultSeconds });
  }

  function startTimer(shouldBroadcast = true) {
    if (timerHandle) return;
    sessionRecorded = false;
    timerHandle = setInterval(() => {
      remaining = Math.max(remaining - 1, 0);
      renderTimer();
      if (remaining === 0) {
        clearInterval(timerHandle);
        timerHandle = null;
        recordSession(Math.max(1, Math.round(defaultSeconds / 60)));
      }
    }, 1000);
    if (shouldBroadcast) broadcastTimer("start");
  }

  function pauseTimer(shouldBroadcast = true) {
    clearInterval(timerHandle);
    timerHandle = null;
    if (shouldBroadcast) broadcastTimer("pause");
  }

  function resetTimer(shouldBroadcast = true) {
    pauseTimer(false);
    remaining = defaultSeconds;
    sessionRecorded = false;
    renderTimer();
    if (shouldBroadcast) broadcastTimer("reset");
  }

  function recordSession(durationMinutes) {
    if (sessionRecorded) return;
    sessionRecorded = true;
    const body = new URLSearchParams();
    body.set("csrf_token", csrfToken);
    body.set("duration_minutes", durationMinutes.toString());
    fetch(`/rooms/${roomId}/session`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": csrfToken },
      body,
    }).catch(() => {
      sessionRecorded = false;
    });
  }

  socket.emit("join_room_channel", { room_id: roomId });

  socket.on("system_message", (data) => {
    appendMessage({ content: data.content, system: true });
  });

  socket.on("receive_message", (data) => {
    appendMessage(data);
  });

  socket.on("timer_update", (data) => {
    remaining = Number(data.remaining);
    defaultSeconds = Number(data.defaultSeconds);
    renderTimer();
    if (data.state === "start") startTimer(false);
    if (data.state === "pause") pauseTimer(false);
    if (data.state === "reset") resetTimer(false);
  });

  chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const content = chatInput.value.trim();
    if (!content) return;
    socket.emit("send_message", { room_id: roomId, content });
    chatInput.value = "";
  });

  document.querySelectorAll("[data-minutes]").forEach((button) => {
    button.addEventListener("click", () => {
      defaultSeconds = Number(button.dataset.minutes) * 60;
      remaining = defaultSeconds;
      renderTimer();
      broadcastTimer("reset");
    });
  });

  document.querySelector("#timer-start").addEventListener("click", () => startTimer());
  document.querySelector("#timer-pause").addEventListener("click", () => pauseTimer());
  document.querySelector("#timer-reset").addEventListener("click", () => resetTimer());

  if (window.JitsiMeetExternalAPI) {
    new JitsiMeetExternalAPI("meet.jit.si", {
      roomName: workspace.dataset.jitsiName,
      parentNode: document.querySelector("#jitsi-meet"),
      userInfo: { displayName: username },
      configOverwrite: {
        prejoinPageEnabled: false,
      },
      interfaceConfigOverwrite: {
        SHOW_JITSI_WATERMARK: false,
      },
    });
  }
}
