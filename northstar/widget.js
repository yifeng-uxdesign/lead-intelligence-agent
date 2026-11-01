import { WIDGET_CONFIG } from "./config.js";
import { createConversation } from "./engine.js";

const REDUCE_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function formatTime(ts) {
  return new Date(ts).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

function el(html) {
  const t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
}

export function mountWidget(root) {
  const conversation = createConversation({
    config: WIDGET_CONFIG,
    onTypingDelay: () => (REDUCE_MOTION ? 80 : WIDGET_CONFIG.typingDelayMs),
  });

  const launcher = el(`
    <button class="ns-launcher" type="button" aria-expanded="false" aria-controls="ns-widget-panel">
      <span class="ns-launcher__icon" aria-hidden="true">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M12 3.2 13.6 8.8 19.2 10.4 13.6 12 12 17.6 10.4 12 4.8 10.4 10.4 8.8 12 3.2Z" fill="currentColor"/>
          <circle cx="12" cy="12" r="9.2" stroke="currentColor" stroke-width="1.2" opacity=".45"/>
        </svg>
      </span>
      <span class="ns-launcher__label">Chat with Northstar</span>
    </button>
  `);

  const panel = el(`
    <section id="ns-widget-panel" class="ns-panel" role="dialog" aria-modal="true" aria-labelledby="ns-widget-title" hidden>
      <header class="ns-panel__header">
        <div class="ns-panel__identity">
          <span class="ns-panel__mark" aria-hidden="true"></span>
          <div>
            <h2 id="ns-widget-title" class="ns-panel__name">${WIDGET_CONFIG.assistantName}</h2>
            <p class="ns-panel__status"><span class="ns-panel__dot"></span>${WIDGET_CONFIG.statusLabel}</p>
          </div>
        </div>
        <div class="ns-panel__actions">
          <button type="button" class="ns-icon-btn" data-action="restart" aria-label="Restart conversation">Restart</button>
          <button type="button" class="ns-icon-btn ns-icon-btn--close" data-action="close" aria-label="Close chat">Close</button>
        </div>
      </header>
      <div class="ns-panel__thread" data-thread tabindex="0"></div>
      <div class="visually-hidden" role="status" aria-live="polite" data-announce></div>
      <form class="ns-panel__composer" data-form>
        <label class="visually-hidden" for="ns-widget-input">Message</label>
        <textarea id="ns-widget-input" name="message" rows="1" placeholder="${WIDGET_CONFIG.placeholder}" autocomplete="off"></textarea>
        <button type="submit" class="ns-send" aria-label="Send message">
          Send
        </button>
      </form>
    </section>
  `);

  root.append(launcher, panel);

  const thread = panel.querySelector("[data-thread]");
  const announcer = panel.querySelector("[data-announce]");
  let announcedCount = 0;
  const form = panel.querySelector("[data-form]");
  const input = panel.querySelector("#ns-widget-input");
  let open = false;
  let lastFocus = null;

  function setOpen(next) {
    if (next === open) return; // re-opening must not overwrite the focus-return target
    open = next;
    panel.hidden = !open;
    launcher.setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("ns-chat-open", open);
    if (open) {
      lastFocus = document.activeElement;
      panel.classList.add("ns-panel--in");
      requestAnimationFrame(() => input.focus());
      scrollThread();
    } else {
      panel.classList.remove("ns-panel--in");
      if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
    }
  }

  function scrollThread() {
    thread.scrollTop = thread.scrollHeight;
  }

  // The thread is rebuilt on every render, so it cannot be a live region (it would
  // re-read the whole history). New assistant messages are announced separately.
  function announce(messages) {
    if (messages.length <= announcedCount) {
      announcedCount = messages.length; // restart or no change
      return;
    }
    const fresh = messages.slice(announcedCount).filter((m) => m.role === "assistant");
    announcedCount = messages.length;
    if (open && fresh.length) {
      announcer.textContent = "";
      announcer.textContent = fresh.map((m) => m.text).join(" ");
    }
  }

  function render(snapshot) {
    thread.replaceChildren();

    for (const msg of snapshot.messages) {
      const row = document.createElement("article");
      row.className = `ns-msg ns-msg--${msg.role}${msg.tone === "cue" ? " ns-msg--cue" : ""}`;
      row.innerHTML = `
        <p class="ns-msg__meta">${msg.role === "assistant" ? WIDGET_CONFIG.assistantName : "You"} · ${formatTime(msg.at)}</p>
        <p class="ns-msg__text"></p>
      `;
      row.querySelector(".ns-msg__text").textContent = msg.text;
      thread.append(row);
    }

    if (snapshot.typing) {
      const typing = document.createElement("div");
      typing.className = "ns-typing";
      typing.setAttribute("aria-label", "Assistant is typing");
      typing.innerHTML = `<span></span><span></span><span></span>`;
      thread.append(typing);
    }

    if (snapshot.startersVisible) {
      const wrap = document.createElement("div");
      wrap.className = "ns-starters";
      wrap.setAttribute("role", "group");
      wrap.setAttribute("aria-label", "Suggested messages");
      for (const starter of WIDGET_CONFIG.starters) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "ns-chip";
        btn.textContent = starter.label;
        btn.addEventListener("click", () => conversation.startFrom(starter.scenarioId));
        wrap.append(btn);
      }
      thread.append(wrap);
    } else if (!snapshot.typing) {
      const nodeChoices = snapshot.choices.filter((c) => c.next !== "__restart__");
      const restartChoice = snapshot.choices.find((c) => c.next === "__restart__");
      if (nodeChoices.length) {
        const wrap = document.createElement("div");
        wrap.className = "ns-starters";
        wrap.setAttribute("role", "group");
        wrap.setAttribute("aria-label", "Suggested replies");
        for (const choice of nodeChoices) {
          const btn = document.createElement("button");
          btn.type = "button";
          btn.className = "ns-chip";
          btn.textContent = choice.label;
          btn.addEventListener("click", () => conversation.choose(choice.id));
          wrap.append(btn);
        }
        if (restartChoice) {
          const btn = document.createElement("button");
          btn.type = "button";
          btn.className = "ns-chip ns-chip--quiet";
          btn.textContent = restartChoice.label;
          btn.addEventListener("click", () => conversation.restart());
          wrap.append(btn);
        }
        thread.append(wrap);
      }
    }

    input.disabled = snapshot.typing;
    scrollThread();
    announce(snapshot.messages);

    // The nodes that held focus (a chip, or the input while disabled) are gone or inert.
    // Keep focus inside the dialog instead of dropping to <body>.
    if (open) {
      const active = document.activeElement;
      const lost =
        active === document.body ||
        !panel.contains(active) ||
        active === thread ||
        (active === input && input.disabled);
      if (lost) {
        if (!input.disabled) input.focus();
        else thread.focus({ preventScroll: true });
      }
    }
  }

  conversation.subscribe(render);

  launcher.addEventListener("click", () => setOpen(!open));

  panel.querySelector('[data-action="close"]').addEventListener("click", () => setOpen(false));
  panel.querySelector('[data-action="restart"]').addEventListener("click", () => {
    conversation.restart();
    input.focus();
  });

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const value = input.value.trim();
    if (!value) return;
    input.value = "";
    resizeInput();
    conversation.send(value);
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });

  input.addEventListener("input", resizeInput);
  function resizeInput() {
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 120)}px`;
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && open) {
      e.preventDefault();
      setOpen(false);
    }
    if (!open || e.key !== "Tab") return;
    const focusable = panel.querySelectorAll(
      'button:not([disabled]), textarea:not([disabled]), [href], [tabindex]:not([tabindex="-1"])'
    );
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (!panel.contains(document.activeElement)) {
      e.preventDefault();
      first.focus();
      return;
    }
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  });

  return {
    open: () => setOpen(true),
    close: () => setOpen(false),
    toggle: () => setOpen(!open),
  };
}
