/* ============================================================
   CareerAI — script.js
   Vanilla JavaScript · No libraries · 60 FPS · API-integrated
   ------------------------------------------------------------
   MODULES
   01. Utilities
   02. Loader
   03. Scroll Progress
   04. Navbar (hide/show, scrolled state, mobile menu)
   05. Particle Background
   06. Cursor Spotlight
   07. Typing Animation
   08. Scroll Reveal (with stagger)
   09. Animated Counters
   10. Progress Bars & Bar Chart
   11. Line Chart Draw-in
   12. 3D Tilt Cards
   13. Magnetic Buttons
   14. Card Mouse Glow
   15. Ripple Effect
   16. Marquee
   17. FAQ Accordion Animation
   18. Contact Form
   19. Back to Top
   20. API Client & Auth State
   21. Modal System (shared)
   22. Auth Modal (login / register)
   23. Resume Analysis Modal (upload -> skills -> recommendations)
   24. Auth-aware Navbar & CTA wiring
   ============================================================ */

(() => {
  "use strict";

  /* ============ CONFIG ============ */

  const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:5000/api"
    : "/api";
  const TOKEN_KEY = "careerai_token";
  const USER_KEY = "careerai_user";

  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  const isTouchDevice = window.matchMedia("(hover: none)").matches;

  /* ============ 01. UTILITIES ============ */

  const $ = (selector, scope = document) => scope.querySelector(selector);
  const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];

  const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

  const lerp = (start, end, factor) => start + (end - start) * factor;

  const escapeHtml = (text) =>
    String(text).replace(/[&<>"]/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
    })[char]);

  function initLoader() {
    const loader = $("#loader");
    if (!loader) return;

    const hide = () => {
      loader.classList.add("loader--done");
      document.body.style.overflow = "";
    };

    document.body.style.overflow = "hidden";

    if (document.readyState === "complete") {
      setTimeout(hide, 400);
    } else {
      window.addEventListener("load", () => setTimeout(hide, 400));
      setTimeout(hide, 3500);
    }
  }

  function initScrollProgress() {
    const bar = $("#scrollProgress");
    if (!bar) return;

    let ticking = false;

    const update = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = docHeight > 0 ? scrollTop / docHeight : 0;
      bar.style.transform = `scaleX(${progress})`;
      ticking = false;
    };

    window.addEventListener(
      "scroll",
      () => {
        if (!ticking) {
          requestAnimationFrame(update);
          ticking = true;
        }
      },
      { passive: true }
    );

    update();
  }

  function initNavbar() {
    const navbar = $("#navbar");
    const toggle = $("#navToggle");
    const links = $("#navLinks");
    if (!navbar) return;

    let lastScrollY = window.scrollY;
    let ticking = false;

    const update = () => {
      const currentY = window.scrollY;
      navbar.classList.toggle("navbar--scrolled", currentY > 24);

      const menuOpen = links && links.classList.contains("open");
      if (!menuOpen) {
        if (currentY > lastScrollY && currentY > 300) {
          navbar.classList.add("navbar--hidden");
        } else {
          navbar.classList.remove("navbar--hidden");
        }
      }

      lastScrollY = currentY;
      ticking = false;
    };

    window.addEventListener(
      "scroll",
      () => {
        if (!ticking) {
          requestAnimationFrame(update);
          ticking = true;
        }
      },
      { passive: true }
    );

    if (toggle && links) {
      toggle.addEventListener("click", () => {
        const isOpen = links.classList.toggle("open");
        toggle.setAttribute("aria-expanded", String(isOpen));
      });

      links.addEventListener("click", (event) => {
        if (event.target.closest(".nav-link")) {
          links.classList.remove("open");
          toggle.setAttribute("aria-expanded", "false");
        }
      });
    }

    update();
  }

  /* ============ 06. CURSOR SPOTLIGHT ============ */

  function initCursorSpotlight() {
    const spotlight = $("#cursorSpotlight");
    if (!spotlight || prefersReducedMotion || isTouchDevice) return;

    let targetX = window.innerWidth / 2;
    let targetY = window.innerHeight / 2;
    let currentX = targetX;
    let currentY = targetY;

    window.addEventListener(
      "mousemove",
      (event) => {
        targetX = event.clientX;
        targetY = event.clientY;
      },
      { passive: true }
    );

    const follow = () => {
      currentX = lerp(currentX, targetX, 0.08);
      currentY = lerp(currentY, targetY, 0.08);
      spotlight.style.transform = `translate(${currentX - spotlight.offsetWidth / 2}px, ${currentY - spotlight.offsetHeight / 2}px)`;
      requestAnimationFrame(follow);
    };

    follow();
  }

  /* ============ 07. TYPING ANIMATION ============ */

  function initTyping() {
    const element = $("#typingText");
    if (!element) return;

    let phrases;
    try {
      phrases = JSON.parse(element.dataset.typing || "[]");
    } catch {
      phrases = [];
    }
    if (!phrases.length) return;

    if (prefersReducedMotion) {
      element.textContent = phrases[0];
      return;
    }

    let phraseIndex = 0;
    let charIndex = 0;
    let deleting = false;

    const TYPE_SPEED = 65;
    const DELETE_SPEED = 32;
    const HOLD_DELAY = 1800;

    const tick = () => {
      const phrase = phrases[phraseIndex];

      if (!deleting) {
        charIndex += 1;
        element.textContent = phrase.slice(0, charIndex);

        if (charIndex === phrase.length) {
          deleting = true;
          setTimeout(tick, HOLD_DELAY);
          return;
        }
        setTimeout(tick, TYPE_SPEED);
      } else {
        charIndex -= 1;
        element.textContent = phrase.slice(0, charIndex);

        if (charIndex === 0) {
          deleting = false;
          phraseIndex = (phraseIndex + 1) % phrases.length;
        }
        setTimeout(tick, DELETE_SPEED);
      }
    };

    setTimeout(tick, 800);
  }

  /* ============ 08. SCROLL REVEAL ============ */

  function initReveal() {
    const elements = $$("[data-reveal]");
    if (!elements.length) return;

    if (prefersReducedMotion) {
      elements.forEach((el) => el.classList.add("revealed"));
      return;
    }

    const groups = new Map();
    for (const el of elements) {
      const parent = el.parentElement;
      if (!groups.has(parent)) groups.set(parent, []);
      groups.get(parent).push(el);
    }
    for (const siblings of groups.values()) {
      siblings.forEach((el, index) => {
        el.style.setProperty("--reveal-delay", `${index * 0.09}s`);
      });
    }

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add("revealed");
            observer.unobserve(entry.target);
          }
        }
      },
      { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
    );

    elements.forEach((el) => observer.observe(el));
  }

  /* ============ 09. ANIMATED COUNTERS ============ */

  function initCounters() {
    const counters = $$("[data-counter]");
    if (!counters.length) return;

    const animate = (el) => {
      const target = parseInt(el.dataset.counter, 10) || 0;

      if (prefersReducedMotion) {
        el.textContent = target.toLocaleString();
        return;
      }

      const duration = 1800;
      const start = performance.now();

      const step = (now) => {
        const progress = clamp((now - start) / duration, 0, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(target * eased).toLocaleString();
        if (progress < 1) requestAnimationFrame(step);
      };

      requestAnimationFrame(step);
    };

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            animate(entry.target);
            observer.unobserve(entry.target);
          }
        }
      },
      { threshold: 0.6 }
    );

    counters.forEach((el) => observer.observe(el));
  }

  /* ============ 10. PROGRESS BARS & BAR CHART ============ */

  function initProgressBars() {
    const fills = $$("[data-progress]");
    const bars = $$("[data-bar]");
    if (!fills.length && !bars.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          const el = entry.target;

          if (el.dataset.progress !== undefined) {
            el.style.width = `${clamp(parseInt(el.dataset.progress, 10) || 0, 0, 100)}%`;
          }
          if (el.dataset.bar !== undefined) {
            el.style.setProperty(
              "--bar-h",
              `${clamp(parseInt(el.dataset.bar, 10) || 0, 0, 100)}%`
            );
          }
          observer.unobserve(el);
        }
      },
      { threshold: 0.4 }
    );

    [...fills, ...bars].forEach((el) => observer.observe(el));
  }

  /* ============ 11. LINE CHART DRAW-IN ============ */

  function initLineChart() {
    const chart = $(".analytics-visual");
    if (!chart) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add("in-view");
            observer.unobserve(entry.target);
          }
        }
      },
      { threshold: 0.4 }
    );

    observer.observe(chart);
  }

  /* ============ 14. CARD MOUSE GLOW ============ */

  function initCardGlow() {
    if (isTouchDevice) return;

    $$(".feature-card").forEach((card) => {
      card.addEventListener("mousemove", (event) => {
        const rect = card.getBoundingClientRect();
        card.style.setProperty("--mx", `${event.clientX - rect.left}px`);
        card.style.setProperty("--my", `${event.clientY - rect.top}px`);
      });
    });
  }

  /* ============ 15. RIPPLE EFFECT ============ */

  function initRipple() {
    if (prefersReducedMotion) return;

    document.addEventListener("click", (event) => {
      const button = event.target.closest(".btn-primary, .btn-glass");
      if (!button) return;

      const rect = button.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const ripple = document.createElement("span");

      ripple.className = "ripple";
      ripple.style.width = ripple.style.height = `${size}px`;
      ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
      ripple.style.top = `${event.clientY - rect.top - size / 2}px`;

      button.appendChild(ripple);
      ripple.addEventListener("animationend", () => ripple.remove());
    });
  }

  /* ============ 16. MARQUEE ============ */

  function initMarquee() {
    const track = $("#marqueeTrack");
    if (!track) return;

    track.innerHTML += track.innerHTML;
  }

  /* ============ 17. FAQ ACCORDION ANIMATION ============ */

  function initFaq() {
    const items = $$(".faq-item");
    if (!items.length) return;

    items.forEach((item) => {
      const summary = $(".faq-question", item);
      const answer = $(".faq-answer", item);
      if (!summary || !answer) return;

      summary.addEventListener("click", (event) => {
        if (prefersReducedMotion) return;
        event.preventDefault();

        if (item.open) {
          const closeAnim = answer.animate(
            [
              { height: `${answer.scrollHeight}px`, opacity: 1 },
              { height: "0px", opacity: 0 },
            ],
            { duration: 300, easing: "cubic-bezier(0.22, 1, 0.36, 1)" }
          );
          closeAnim.addEventListener("finish", () => {
            item.open = false;
          });
        } else {
          items.forEach((other) => {
            if (other !== item && other.open) other.open = false;
          });

          item.open = true;
          answer.animate(
            [
              { height: "0px", opacity: 0 },
              { height: `${answer.scrollHeight}px`, opacity: 1 },
            ],
            { duration: 350, easing: "cubic-bezier(0.22, 1, 0.36, 1)" }
          );
        }
      });
    });
  }

  /* ============ 18. CONTACT FORM ============ */

  function initContactForm() {
    const form = $("#contactForm");
    const status = $("#formStatus");
    if (!form || !status) return;

    const setStatus = (message, type) => {
      status.textContent = message;
      status.className = `form-status ${type}`;
    };

    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const name = form.name.value.trim();
      const email = form.email.value.trim();
      const message = form.message.value.trim();

      if (name.length < 2) {
        setStatus("Please enter your full name.", "error");
        form.name.focus();
        return;
      }

      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
      if (!emailPattern.test(email)) {
        setStatus("Please enter a valid email address.", "error");
        form.email.focus();
        return;
      }

      if (message.length < 10) {
        setStatus("Tell us a little more about your goal (10+ characters).", "error");
        form.message.focus();
        return;
      }

      const submitButton = form.querySelector('button[type="submit"]');
      setBtnLoading(submitButton, true, "Sending...");

      try {
        const response = await api("/contact/submit", {
          method: "POST",
          body: { name, email, message, website },
        });

        form.reset();
        setStatus(response.message || `Thanks, ${name.split(" ")[0]}! Your message was sent.`, "success");
      } catch (error) {
        setStatus(error.message, "error");
      } finally {
        setBtnLoading(submitButton, false);
      }
    });
  }

  /* ============ 19. BACK TO TOP ============ */

  function initBackToTop() {
    const button = $("#backToTop");
    if (!button) return;

    let ticking = false;

    window.addEventListener(
      "scroll",
      () => {
        if (!ticking) {
          requestAnimationFrame(() => {
            button.classList.toggle("visible", window.scrollY > 600);
            ticking = false;
          });
          ticking = true;
        }
      },
      { passive: true }
    );

    button.addEventListener("click", () => {
      window.scrollTo({
        top: 0,
        behavior: prefersReducedMotion ? "auto" : "smooth",
      });
    });
  }

  /* ============ 20. API CLIENT & AUTH STATE ============ */

  const auth = {
    get token() {
      return localStorage.getItem(TOKEN_KEY);
    },
    get user() {
      try {
        return JSON.parse(localStorage.getItem(USER_KEY));
      } catch {
        return null;
      }
    },
    save(token, user) {
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    },
    clear() {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    },
    get isLoggedIn() {
      return Boolean(this.token);
    },
  };

  const learningState = {
    roadmap: null,
  };

  /**
   * Fetch wrapper: attaches JWT, parses JSON, throws Error(message) on
   * failure, and auto-logs-out on expired sessions.
   * In-flight GET requests are deduplicated to prevent redundant calls.
   */
  const _inflight = new Map();
  async function api(path, { method = "GET", body = null, isForm = false } = {}) {
    const headers = {};
    if (auth.token) headers.Authorization = `Bearer ${auth.token}`;
    if (body && !isForm) headers["Content-Type"] = "application/json";

    // Deduplicate concurrent identical GET requests
    const isGet = method === "GET" && !body;
    if (isGet && _inflight.has(path)) return _inflight.get(path);

    const p = fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body ? (isForm ? body : JSON.stringify(body)) : null,
    })
      .catch(() => {
        throw new Error("Cannot reach the server. Is the backend running on port 5000?");
      })
      .then(async (response) => {
        let data = {};
        try { data = await response.json(); } catch { /* non-JSON */ }
        if (!response.ok) {
          if (response.status === 401 && auth.isLoggedIn) {
            auth.clear();
            updateNavbarAuthState();
          }
          throw new Error(data.error || data.detail || `Request failed (${response.status}).`);
        }
        return data;
      })
      .finally(() => { if (isGet) _inflight.delete(path); });

    if (isGet) _inflight.set(path, p);
    return p;
  }

  /* ============ 21. MODAL SYSTEM (shared) ============ */

  function injectModalStyles() {
    // Minimal positioning styles only — all visual styling reuses the
    // existing design system classes from styles.css.
    const style = document.createElement("style");
    style.textContent = [
      ".modal-overlay{position:fixed;inset:0;z-index:300;display:grid;place-items:center;padding:1.5rem;background:rgba(2,6,23,0.75);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);opacity:0;transition:opacity .3s ease;overflow-y:auto}",
      ".modal-overlay.open{opacity:1}",
      ".modal-box{width:min(100%,480px);max-height:90vh;overflow-y:auto;padding:2rem;position:relative;transform:translateY(16px) scale(.97);transition:transform .35s cubic-bezier(.22,1,.36,1)}",
      ".modal-overlay.open .modal-box{transform:translateY(0) scale(1)}",
      ".modal-close{position:absolute;top:1rem;right:1rem;width:36px;height:36px;display:grid;place-content:center;border-radius:50%;border:1px solid var(--border);background:var(--card);color:var(--muted);font-size:1.1rem;line-height:1}",
      ".modal-close:hover{color:var(--text)}",
      ".auth-tabs{display:grid;grid-template-columns:1fr 1fr;gap:.5rem;margin-bottom:1.5rem}",
      ".auth-tab{padding:.7rem;border-radius:var(--radius-full);border:1px solid var(--border);background:transparent;color:var(--muted);font-weight:600;font-size:var(--fs-sm)}",
      ".auth-tab.active{background:var(--gradient-cta);color:#fff;border-color:transparent}",
      ".modal-title{font-size:1.4rem;font-weight:800;margin-bottom:.35rem}",
      ".modal-subtitle{font-size:var(--fs-sm);color:var(--muted);margin-bottom:1.25rem}",
      ".result-block{margin-top:1.25rem;display:grid;gap:1rem}",
      ".file-note{font-size:var(--fs-xs);color:var(--muted);margin-top:.35rem}",
      ".course-modal .modal-box{width:min(100%,760px)}",
      ".course-content{display:grid;gap:1.1rem}",
      ".course-video{aspect-ratio:16/9;width:100%;border:1px solid var(--border);border-radius:var(--radius-md);overflow:hidden;background:rgba(255,255,255,.04)}",
      ".course-video iframe{width:100%;height:100%;border:0}",
      ".course-links{display:grid;gap:.7rem}",
      ".course-search-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:.7rem}",
      ".course-link{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.85rem 1rem;border:1px solid var(--border);border-radius:var(--radius-md);background:rgba(255,255,255,.05);font-size:var(--fs-sm);transition:border-color .25s,background-color .25s}",
      ".course-link:hover{border-color:rgba(6,182,212,.45);background:rgba(255,255,255,.08)}",
      ".course-link span:last-child{color:var(--muted);font-size:var(--fs-xs);white-space:nowrap}",
      ".course-note{font-size:var(--fs-xs);color:var(--muted);line-height:1.6}",
      ".quiz-list{display:grid;gap:.9rem}",
      ".quiz-section{margin-bottom:.5rem}",
      ".quiz-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;padding-bottom:.75rem;border-bottom:1px solid var(--border)}",
      ".quiz-title{font-size:var(--fs-base);font-weight:700;color:var(--text);margin:0}",
      ".quiz-progress-badge{font-size:var(--fs-xs);font-weight:600;padding:.3rem .7rem;border-radius:999px;background:rgba(99,102,241,.12);color:#a5b4fc;transition:all .2s ease}",
      ".quiz-progress-badge.quiz-progress-complete{background:rgba(34,197,94,.15);color:#4ade80}",
      ".quiz-card{padding:1rem;border:1px solid var(--border);border-radius:var(--radius-md);background:rgba(255,255,255,.04);transition:border-color .2s ease,background .2s ease}",
      ".quiz-card:has(input:checked){border-color:rgba(99,102,241,.4);background:rgba(99,102,241,.06)}",
      ".quiz-q{font-size:var(--fs-sm);font-weight:600;margin-bottom:.7rem}",
      ".quiz-options{display:grid;gap:.55rem}",
      ".quiz-option{display:flex;gap:.6rem;align-items:flex-start;font-size:var(--fs-sm);color:var(--muted);cursor:pointer;padding:.45rem .6rem;border-radius:var(--radius-sm);transition:background .15s ease}",
      ".quiz-option:hover{background:rgba(255,255,255,.06)}",
      ".quiz-option input[type=radio]{accent-color:#6366f1;margin-top:.15rem}",
      ".roadmap-card.is-locked{opacity:.7;border-color:rgba(255,255,255,.08)}",
      ".roadmap-card.is-locked:hover{transform:none;box-shadow:var(--shadow-card)}",
      ".course-actions{display:grid;grid-template-columns:1fr 1fr;gap:.75rem}",
      ".course-status-row{display:flex;align-items:center;justify-content:space-between;gap:1rem;font-size:var(--fs-sm)}",
      ".roadmap-card{cursor:pointer}",
    ].join("\n");
    document.head.appendChild(style);
  }

  function createModal(id, innerHtml) {
    let overlay = document.getElementById(id);
    if (overlay) return overlay;

    overlay = document.createElement("div");
    overlay.className = "modal-overlay";
    overlay.id = id;
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.innerHTML = `
      <div class="modal-box glass-card">
        <button type="button" class="modal-close" aria-label="Close dialog">✕</button>
        ${innerHtml}
      </div>`;
    document.body.appendChild(overlay);

    const close = () => closeModal(overlay);
    $(".modal-close", overlay).addEventListener("click", close);
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) close();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && overlay.classList.contains("open")) close();
    });

    return overlay;
  }

  function openModal(overlay) {
    overlay.style.display = "grid";
    requestAnimationFrame(() => overlay.classList.add("open"));
    document.body.style.overflow = "hidden";
  }

  function closeModal(overlay) {
    overlay.classList.remove("open");
    document.body.style.overflow = "";
    setTimeout(() => {
      overlay.style.display = "none";
    }, 300);
  }

  function setBtnLoading(button, loading, loadingText) {
    if (loading) {
      button.dataset.originalText = button.textContent;
      button.textContent = loadingText;
      button.disabled = true;
      button.style.opacity = "0.7";
    } else {
      button.textContent = button.dataset.originalText || button.textContent;
      button.disabled = false;
      button.style.opacity = "";
    }
  }

  /* ============ 22. AUTH MODAL ============ */

  function buildAuthModal() {
    const overlay = createModal(
      "authModal",
      `
      <h3 class="modal-title">Welcome to CareerAI</h3>
      <p class="modal-subtitle">Sign in or create a free account to analyze your resume.</p>
      <div class="auth-tabs">
        <button type="button" class="auth-tab" data-mode="login">Sign in</button>
        <button type="button" class="auth-tab" data-mode="register">Create account</button>
      </div>
      <form id="authForm" novalidate>
        <div class="form-field" id="authNameField" style="margin-bottom:1rem">
          <label for="authName">Full name</label>
          <input type="text" id="authName" name="name" placeholder="Alex Fernando" autocomplete="name" />
        </div>
        <div class="form-field" style="margin-bottom:1rem">
          <label for="authEmail">Email address</label>
          <input type="email" id="authEmail" name="email" placeholder="alex@university.edu" required autocomplete="email" />
        </div>
        <div class="form-field" style="margin-bottom:1.25rem">
          <label for="authPassword">Password</label>
          <input type="password" id="authPassword" name="password" placeholder="At least 6 characters" required autocomplete="current-password" />
        </div>
        <button type="submit" class="btn btn-primary btn-block" id="authSubmit">Sign in</button>
        <p class="form-status" id="authStatus" role="status" aria-live="polite"></p>
      </form>`
    );

    const form = $("#authForm", overlay);
    const tabs = $$(".auth-tab", overlay);
    const nameField = $("#authNameField", overlay);
    const submit = $("#authSubmit", overlay);
    const status = $("#authStatus", overlay);

    const setStatus = (message, type) => {
      status.textContent = message;
      status.className = `form-status ${type}`;
    };

    const setMode = (mode) => {
      overlay.dataset.mode = mode;
      tabs.forEach((tab) =>
        tab.classList.toggle("active", tab.dataset.mode === mode)
      );
      nameField.style.display = mode === "register" ? "" : "none";
      submit.textContent = mode === "register" ? "Create account" : "Sign in";
      setStatus("", "");
    };

    tabs.forEach((tab) =>
      tab.addEventListener("click", () => setMode(tab.dataset.mode))
    );

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      setStatus("", "");

      const mode = overlay.dataset.mode || "login";
      const name = form.name.value.trim();
      const email = form.email.value.trim().toLowerCase();
      const password = form.password.value;

      if (mode === "register" && name.length < 2) {
        setStatus("Please enter your full name.", "error");
        return;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
        setStatus("Please enter a valid email address.", "error");
        return;
      }
      if (password.length < 6) {
        setStatus("Password must be at least 6 characters.", "error");
        return;
      }

      setBtnLoading(submit, true, mode === "register" ? "Creating account…" : "Signing in…");

      try {
        const path = mode === "register" ? "/auth/register" : "/auth/login";
        const body =
          mode === "register" ? { name, email, password } : { email, password };
        const data = await api(path, { method: "POST", body });

        auth.save(data.access_token, data.user);
        updateNavbarAuthState();
        hydrateLearningState();
        setStatus(data.message, "success");

        setTimeout(() => {
          closeModal(overlay);
          form.reset();
          openResumeModal();
        }, 700);
      } catch (error) {
        setStatus(error.message, "error");
      } finally {
        setBtnLoading(submit, false);
      }
    });

    overlay.dataset.built = "true";
    setMode("login");
    return overlay;
  }

  function openAuthModal(mode = "login", prefill = {}) {
    const overlay = buildAuthModal();
    const tabs = $$(".auth-tab", overlay);
    const target = tabs.find((tab) => tab.dataset.mode === mode);
    if (target) target.click();

    if (prefill.name) $("#authName", overlay).value = prefill.name;
    if (prefill.email) $("#authEmail", overlay).value = prefill.email;

    openModal(overlay);
  }

  /* ============ 23. RESUME ANALYSIS MODAL ============ */

  function buildResumeModal() {
    const overlay = createModal(
      "resumeModal",
      `
      <div id="resumeChoiceScreen">
        <h3 class="modal-title">How would you like to get started?</h3>
        <p class="modal-subtitle">Choose one option — both paths lead to the same powerful career analysis.</p>
        <div class="choice-grid">
          <button class="choice-card" id="choiceUpload" type="button">
            <div class="choice-icon choice-icon--upload">
              <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            </div>
            <h4 class="choice-title">Upload Resume</h4>
            <p class="choice-desc">Upload a PDF resume — our AI extracts your skills automatically.</p>
          </button>
          <button class="choice-card" id="choiceFillForm" type="button">
            <div class="choice-icon choice-icon--form">
              <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            </div>
            <h4 class="choice-title">Fill a Form</h4>
            <p class="choice-desc">Enter your details manually — skills, education, and career goals.</p>
          </button>
        </div>
      </div>

      <div id="resumeUploadScreen" style="display:none">
        <h3 class="modal-title">Analyze your resume</h3>
        <p class="modal-subtitle">Upload your PDF resume — our AI extracts your skills and matches you to careers.</p>
        <form id="resumeForm" action="javascript:void(0)" novalidate>
          <div class="form-field" style="margin-bottom:1.25rem">
            <label for="resumeFile">Resume (PDF, max 5 MB)</label>
            <input type="file" id="resumeFile" name="resume" accept="application/pdf" required />
            <p class="file-note">Your resume is only used to generate your analysis.</p>
          </div>
          <div class="form-field" id="resumeRoleStep" style="display:none;margin-bottom:1.25rem">
            <label for="resumeTargetRole">Which role are you aiming for?</label>
            <select id="resumeTargetRole" name="target_career" required>
              <option value="">Select a role</option>
            </select>
            <p class="file-note">Choose the role you want, then analyze to see the skill gaps and courses.</p>
          </div>
          <button type="submit" class="btn btn-primary btn-block" id="resumeSubmit">Upload resume</button>
          <p class="form-status" id="resumeStatus" role="status" aria-live="polite"></p>
        </form>
        <div class="result-block" id="resumeResults"></div>
        <button class="btn btn-ghost back-to-choice-btn" id="backToChoice1" type="button">&larr; Back to options</button>
      </div>

      <div id="resumeFormScreen" style="display:none">
        <h3 class="modal-title">Tell us about yourself</h3>
        <p class="modal-subtitle">Fill in your details — we'll use this to generate your career analysis.</p>
        <form id="manualProfileForm" action="javascript:void(0)" novalidate>
          <div class="form-field" style="margin-bottom:1.25rem">
            <label for="formSkills">Your Skills *</label>
            <div class="skills-input-wrap">
              <input type="text" id="formSkillInput" placeholder="Type a skill and press Enter…" autocomplete="off" />
              <div class="skill-tags" id="formSkillTags"></div>
            </div>
            <p class="file-note">e.g. Python, React, Machine Learning, Docker…</p>
          </div>

          <div class="form-field" style="margin-bottom:1.25rem">
            <label for="formEducation">Education</label>
            <input type="text" id="formEducation" name="education" placeholder="e.g. B.Tech in Computer Science" autocomplete="off" />
          </div>

          <div class="form-field" style="margin-bottom:1.25rem">
            <label for="formExperience">Years of Experience</label>
            <input type="number" id="formExperience" name="experience_years" min="0" max="50" step="0.5" placeholder="e.g. 2" />
          </div>

          <div class="form-field" id="formRoleStep" style="margin-bottom:1.25rem">
            <label for="formTargetRole">Which role are you aiming for? *</label>
            <select id="formTargetRole" name="target_career" required>
              <option value="">Select a role</option>
            </select>
            <p class="file-note">Choose the career you want to pursue.</p>
          </div>

          <div class="form-field" style="margin-bottom:1.25rem">
            <label for="formInterests">Interests (optional)</label>
            <input type="text" id="formInterests" name="interests" placeholder="e.g. AI, Cloud Computing, Web Dev" />
            <p class="file-note">Comma-separated interests to refine recommendations.</p>
          </div>

          <button type="submit" class="btn btn-primary btn-block" id="formSubmit">Analyze my profile</button>
          <p class="form-status" id="formStatus" role="status" aria-live="polite"></p>
        </form>
        <button class="btn btn-ghost back-to-choice-btn" id="backToChoice2" type="button">&larr; Back to options</button>
      </div>`
    );

    /* ---------- Shared elements ---------- */
    const choiceScreen  = $("#resumeChoiceScreen", overlay);
    const uploadScreen  = $("#resumeUploadScreen", overlay);
    const formScreen    = $("#resumeFormScreen", overlay);
    const choiceUpload  = $("#choiceUpload", overlay);
    const choiceFill    = $("#choiceFillForm", overlay);
    const backToChoice1 = $("#backToChoice1", overlay);
    const backToChoice2 = $("#backToChoice2", overlay);

    const showScreen = (which) => {
      choiceScreen.style.display = which === "choice" ? "" : "none";
      uploadScreen.style.display = which === "upload" ? "" : "none";
      formScreen.style.display   = which === "form"   ? "" : "none";
    };

    choiceUpload.addEventListener("click", () => showScreen("upload"));
    choiceFill.addEventListener("click", () => showScreen("form"));
    backToChoice1.addEventListener("click", () => showScreen("choice"));
    backToChoice2.addEventListener("click", () => showScreen("choice"));

    /* ================================================================
       UPLOAD PATH (existing flow)
       ================================================================ */
    const form       = $("#resumeForm", overlay);
    const fileInput  = $("#resumeFile", overlay);
    const roleStep   = $("#resumeRoleStep", overlay);
    const roleSelect = $("#resumeTargetRole", overlay);
    const submit     = $("#resumeSubmit", overlay);
    const status     = $("#resumeStatus", overlay);
    const results    = $("#resumeResults", overlay);
    let flowStage    = "upload";
    let roleOptionsLoaded = false;
    let uploadedResume = null;

    const setStatus = (message, type) => {
      status.textContent = message;
      status.className = `form-status ${type}`;
    };

    const loadRoleOptions = async (selectEl) => {
      if (roleOptionsLoaded) return;
      const data = await api("/career/list");
      const roles = data.careers || [];
      const optionsHtml = `<option value="">Select a role</option>` + roles
        .map((c) => `<option value="${escapeHtml(c.title)}">${escapeHtml(c.title)} — ${escapeHtml(c.category)}</option>`)
        .join("");
      selectEl.innerHTML = optionsHtml;
      roleOptionsLoaded = true;
    };

    const loadAllRoleOptions = async () => {
      if (roleOptionsLoaded) return;
      const data = await api("/career/list");
      const roles = data.careers || [];
      const optionsHtml = `<option value="">Select a role</option>` + roles
        .map((c) => `<option value="${escapeHtml(c.title)}">${escapeHtml(c.title)} — ${escapeHtml(c.category)}</option>`)
        .join("");
      roleSelect.innerHTML = optionsHtml;
      formTargetRole.innerHTML = optionsHtml;
      roleOptionsLoaded = true;
    };

    const resetToUpload = () => {
      flowStage = "upload";
      roleStep.style.display = "none";
      roleSelect.value = "";
      submit.textContent = "Upload resume";
    };

    resetToUpload();

    fileInput.addEventListener("change", () => {
      if (flowStage === "analyze") {
        resetToUpload();
        results.innerHTML = "";
      }
    });

    const runUploadAnalysis = async () => {
      setStatus("", "");
      results.innerHTML = "";
      if (flowStage === "upload") {
        const file = fileInput?.files?.[0];
        if (!file) {
          setStatus("Please choose a PDF file.", "error");
          return;
        }
        if (file.type !== "application/pdf") {
          setStatus("Only PDF files are accepted.", "error");
          return;
        }
        if (file.size > 5 * 1024 * 1024) {
          setStatus("File is too large. Maximum size is 5 MB.", "error");
          return;
        }

        if (!auth.isLoggedIn) {
          setStatus("Sign in to upload and analyze your resume.", "error");
          openAuthModal("login");
          return;
        }

        const formData = new FormData();
        formData.append("resume", file);

        setBtnLoading(submit, true, "Uploading resume…");

        try {
          const upload = await api("/resume/upload", {
            method: "POST",
            body: formData,
            isForm: true,
          });

          uploadedResume = { file_name: file.name, parsed: upload.parsed };

          renderSkills(results, upload.parsed.skills_found);
          await loadAllRoleOptions();
          roleStep.style.display = "block";
          flowStage = "analyze";
          submit.textContent = "Analyze resume";
          setStatus("Upload complete. Choose the role you are aiming for, then click Analyze.", "success");
        } catch (error) {
          setStatus(error.message, "error");
        } finally {
          setBtnLoading(submit, false);
        }
        return;
      }

      const targetCareer = roleSelect.value.trim();
      if (!targetCareer) {
        setStatus("Choose the role you are aiming for.", "error");
        return;
      }

      setBtnLoading(submit, true, "Analyzing role fit…");

      try {
        const analysis = await api("/career/analyze", {
          method: "POST",
          body: { career: targetCareer },
        });
        renderTargetRoleAnalysisOnPage(uploadedResume || { file_name: "resume.pdf", parsed: {} }, analysis.analysis);
        setStatus("Analysis complete — reflected on the page.", "success");
        setTimeout(() => {
          closeModal(overlay);
          const target = $("#demo") || $("#hero") || $("#roadmap");
          target?.scrollIntoView({ behavior: "smooth", block: "start" });
        }, 500);
      } catch (error) {
        setStatus(error.message, "error");
      } finally {
        setBtnLoading(submit, false);
      }
    };

    form.addEventListener("submit", (e) => { e.preventDefault(); runUploadAnalysis(); });
    submit.addEventListener("click", (e) => { e.preventDefault(); e.stopPropagation(); if (e.detail === 0) return; runUploadAnalysis(); });

    /* ================================================================
       FORM PATH (manual entry)
       ================================================================ */
    const manualForm     = $("#manualProfileForm", overlay);
    const skillInput     = $("#formSkillInput", overlay);
    const skillTagsWrap  = $("#formSkillTags", overlay);
    const formEducation  = $("#formEducation", overlay);
    const formExperience = $("#formExperience", overlay);
    const formTargetRole = $("#formTargetRole", overlay);
    const formInterests  = $("#formInterests", overlay);
    const formSubmit     = $("#formSubmit", overlay);
    const formStatus     = $("#formStatus", overlay);

    let manualSkills = [];

    const setFormStatus = (message, type) => {
      formStatus.textContent = message;
      formStatus.className = `form-status ${type}`;
    };

    const renderSkillTags = () => {
      skillTagsWrap.innerHTML = manualSkills
        .map((s, i) => `<span class="skill-tag">${escapeHtml(s)} <button type="button" class="skill-tag-remove" data-idx="${i}" aria-label="Remove ${escapeHtml(s)}">&times;</button></span>`)
        .join("");
    };

    skillTagsWrap.addEventListener("click", (e) => {
      const btn = e.target.closest(".skill-tag-remove");
      if (!btn) return;
      manualSkills.splice(Number(btn.dataset.idx), 1);
      renderSkillTags();
    });

    skillInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const val = skillInput.value.trim();
        if (val && !manualSkills.includes(val) && manualSkills.length < 30) {
          manualSkills.push(val);
          renderSkillTags();
        }
        skillInput.value = "";
      }
    });

    // Load role options when form screen becomes visible
    choiceFill.addEventListener("click", () => loadAllRoleOptions());

    manualForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      setFormStatus("", "");

      if (!manualSkills.length) {
        setFormStatus("Please add at least one skill.", "error");
        return;
      }

      const targetCareer = formTargetValue(formTargetRole);

      if (!auth.isLoggedIn) {
        setFormStatus("Sign in to analyze your profile.", "error");
        openAuthModal("login");
        return;
      }

      setFormLoading(formSubmit, true, "Saving profile…");

      try {
        const interests = formInterests.value.split(",").map((s) => s.trim()).filter(Boolean);

        const payload = {
          skills: manualSkills,
          education: formEducation.value.trim(),
          experience_years: formExperience.value ? Number(formExperience.value) : null,
          target_career: targetCareer,
          interests,
        };

        const resp = await api("/resume/submit-form", {
          method: "POST",
          body: payload,
        });

        // Now run career analysis (same as upload path)
        setFormStatus("Profile saved. Running analysis…", "success");

        const analysis = await api("/career/analyze", {
          method: "POST",
          body: { career: targetCareer },
        });

        renderTargetRoleAnalysisOnPage(
          { file_name: "manual-form", parsed: resp.parsed },
          analysis.analysis,
        );

        setFormStatus("Analysis complete — reflected on the page.", "success");
        setTimeout(() => {
          closeModal(overlay);
          const target = $("#demo") || $("#hero") || $("#roadmap");
          target?.scrollIntoView({ behavior: "smooth", block: "start" });
        }, 500);
      } catch (error) {
        setFormStatus(error.message, "error");
      } finally {
        setFormLoading(formSubmit, false);
      }
    });

    formSubmit.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (e.detail === 0) return;
      manualForm.requestSubmit();
    });

    function formTargetValue(select) { return (select?.value || "").trim(); }
    function setFormLoading(btn, loading, label) {
      btn.disabled = loading;
      if (loading) { btn.dataset.origText = btn.textContent; btn.textContent = label || "Working…"; }
      else { btn.textContent = btn.dataset.origText || "Analyze my profile"; }
    }

    return overlay;
  }

  function renderSkills(container, skills) {
    const section = document.createElement("div");
    if (!skills.length) {
      section.innerHTML = `<p class="modal-subtitle">No known skills detected — try adding more detail to your resume.</p>`;
    } else {
      section.innerHTML = `
        <p class="demo-title" style="margin-bottom:.6rem">Skills extracted (${skills.length})</p>
        <div class="skill-chips" style="border:none;padding:0">
          ${skills.map((skill) => `<span class="chip">${escapeHtml(skill)}</span>`).join("")}
        </div>`;
    }
    container.appendChild(section);
  }

  const encodeQuery = (text) => encodeURIComponent(String(text).trim());

  const youtubeWatchUrl = (video) =>
    video?.youtube_id ? `https://www.youtube.com/watch?v=${encodeURIComponent(video.youtube_id)}` : "";

  const youtubeSearchUrl = (query) =>
    `https://www.youtube.com/results?search_query=${encodeQuery(query)}`;

  const youtubeEmbedUrl = (video) => {
    if (!video?.youtube_id) return "";
    return `https://www.youtube-nocookie.com/embed/${encodeURIComponent(video.youtube_id)}`;
  };

  const moduleProgress = (module) => {
    if (module.status === "completed") return 100;
    return clamp(Number(module.progress_percent || 0), 0, 100);
  };

  const isModuleUnlocked = (module, roadmap = learningState.roadmap) => {
    if (!roadmap?.modules?.length) return true;
    if (module.order <= 1) return true;
    const previousModule = roadmap.modules.find((item) => item.order === module.order - 1);
    return previousModule?.status === "completed";
  };

  const moduleStatusLabel = (module, roadmap = learningState.roadmap) => {
    if (!isModuleUnlocked(module, roadmap)) return "Locked - pass previous quiz";
    const progress = moduleProgress(module);
    if (module.status === "completed" || progress >= 100) return "Completed";
    if (progress > 0 || module.status === "in_progress") return `In progress - ${progress}%`;
    return "Ready to start";
  };

  const moduleStatusClass = (module, roadmap = learningState.roadmap) => {
    if (!isModuleUnlocked(module, roadmap)) return "status-locked";
    const progress = moduleProgress(module);
    if (module.status === "completed" || progress >= 100) return "status-done";
    if (progress > 0 || module.status === "in_progress") return "status-active";
    return "status-locked";
  };

  function renderRoadmapOnPage(roadmap) {
    const roadmapGrid = $("#roadmap .roadmap-grid");
    if (!roadmapGrid || !roadmap?.modules?.length) return;

    learningState.roadmap = roadmap;
    roadmapGrid.innerHTML = roadmap.modules
      .map(
        (module, index) => `
        <article class="roadmap-card glass-card ${isModuleUnlocked(module, roadmap) ? "" : "is-locked"}" data-reveal data-module-order="${module.order}" tabindex="0" role="button" aria-label="Open ${escapeHtml(module.skill)} courses">
          <div class="roadmap-week">Weeks ${module.start_week}–${module.end_week}</div>
          <h3 class="roadmap-title">${escapeHtml(module.skill)}</h3>
          <p class="roadmap-text">Gap-focused course plan for ${escapeHtml(roadmap.career)}. ${module.priority === "core" ? "Core skill" : "Bonus skill"} first.</p>
          <div class="roadmap-meta">
            <span class="chip">${module.resources.length} resources</span>
            <span class="chip">${module.videos.length} embed + playlists</span>
            <span class="chip chip-success">Quiz</span>
          </div>
          <div class="progress-track"><div class="progress-fill ${module.priority === "core" ? "fill-primary" : "fill-secondary"}" style="width:${Math.round(moduleProgress(module))}%"></div></div>
          <span class="roadmap-status ${moduleStatusClass(module, roadmap)}">${moduleStatusLabel(module, roadmap)}</span>
        </article>`
      )
      .join("");

    $$("#roadmap .roadmap-card", roadmapGrid).forEach((card, index) => {
      card.classList.remove("revealed");
      setTimeout(() => card.classList.add("revealed"), index * 70);
    });

    bindRoadmapCards();
    updateDashboardFromRoadmap(roadmap);
  }

  function findRoadmapModule(order) {
    return learningState.roadmap?.modules?.find((module) => module.order === order);
  }

  function syncModuleProgress(moduleUpdate) {
    const module = findRoadmapModule(moduleUpdate.order);
    if (!module) return;
    module.status = moduleUpdate.status;
    module.progress_percent = moduleUpdate.progress_percent;
    renderRoadmapOnPage(learningState.roadmap);
  }

  async function refreshRoadmap() {
    if (!auth.isLoggedIn) return;
    const data = await api("/roadmap");
    renderRoadmapOnPage(data.roadmap);
  }

  async function startModule(module) {
    if (!auth.isLoggedIn) {
      openAuthModal("login");
      return;
    }

    await api(`/roadmap/module/${module.order}/start`, {
      method: "PUT",
    });
    await refreshRoadmap();
    await refreshDashboardSummary();
  }

  async function recordCourseProgress(module, progressPercent, resourceType, resourceTitle) {
    if (!auth.isLoggedIn) {
      openAuthModal("login");
      return;
    }

    const data = await api(`/roadmap/module/${module.order}/progress`, {
      method: "PUT",
      body: {
        progress_percent: progressPercent,
        resource_type: resourceType,
        resource_title: resourceTitle,
      },
    });

    syncModuleProgress(data.module);
    await refreshDashboardSummary();
  }

  async function submitModuleQuiz(module, answers) {
    if (!auth.isLoggedIn) {
      openAuthModal("login");
      return;
    }

    const data = await api(`/roadmap/module/${module.order}/quiz`, {
      method: "POST",
      body: { answers },
    });
    await refreshRoadmap();
    await refreshDashboardSummary();
    return data;
  }

  function youtubeConceptLinks(module) {
    const skill = module.skill;
    return [
      {
        label: "YouTube playlists",
        detail: "Playlist search",
        query: `${skill} complete playlist free course`,
      },
      {
        label: "Full course",
        detail: "Long-form videos",
        query: `${skill} full course for beginners`,
      },
      {
        label: "Project tutorials",
        detail: "Build along",
        query: `${skill} project tutorial hands on`,
      },
      {
        label: "Concept revision",
        detail: "Key concepts",
        query: `${skill} important concepts tutorial`,
      },
    ];
  }

  function buildCourseModal(module) {
    const unlocked = isModuleUnlocked(module);
    const video = module.videos?.[0];
    const videoMarkup = video
      ? `<div class="course-video"><iframe src="${youtubeEmbedUrl(video)}" title="${escapeHtml(video.title)}" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>`
      : `<p class="modal-subtitle">No embedded video is available for this skill yet. Use the free resources below.</p>`;

    const youtubeMarkup = youtubeConceptLinks(module)
      .map(
        (item) => `
        <a class="course-link" href="${youtubeSearchUrl(item.query)}" target="_blank" rel="noopener" data-resource-title="${escapeHtml(item.label)}">
          <span>${escapeHtml(item.label)}</span>
          <span>${escapeHtml(item.detail)}</span>
        </a>`
      )
      .join("");

    const videoLinksMarkup = (module.videos || [])
      .map(
        (item, index) => `
        <a class="course-link" href="${youtubeWatchUrl(item)}" target="_blank" rel="noopener" data-resource-title="${escapeHtml(item.title)}">
          <span>${index === 0 ? "Open embedded video on YouTube" : escapeHtml(item.title)}</span>
          <span>${index === 0 ? "Fallback" : "Video"}</span>
        </a>`
      )
      .join("");

    const resourceMarkup = module.resources?.length
      ? module.resources
          .map(
            (resource) => `
            <a class="course-link" href="${escapeHtml(resource.url)}" target="_blank" rel="noopener" data-resource-title="${escapeHtml(resource.name)}">
              <span>${escapeHtml(resource.name)}</span>
              <span>${escapeHtml(resource.platform || "Open resource")}</span>
            </a>`
          )
          .join("")
      : `<p class="modal-subtitle">No external resources were found for this module.</p>`;

    const totalQuestions = module.quiz?.length || 0;
    const quizMarkup = totalQuestions
      ? `
      <div class="quiz-section">
        <div class="quiz-header">
          <h4 class="quiz-title">Quiz</h4>
          <span class="quiz-progress-badge" id="quizProgressBadge">0 / ${totalQuestions} answered</span>
        </div>
        <div class="quiz-list">
          ${module.quiz
            .map(
              (question, questionIndex) => `
              <fieldset class="quiz-card" data-question-index="${questionIndex}">
                <legend class="quiz-q">${questionIndex + 1}. ${escapeHtml(question.q)}</legend>
                <div class="quiz-options">
                  ${question.options
                    .map(
                      (option, optionIndex) => `
                      <label class="quiz-option">
                        <input type="radio" name="quiz_${questionIndex}" value="${optionIndex}" />
                        <span>${escapeHtml(option)}</span>
                      </label>`
                    )
                    .join("")}
                </div>
              </fieldset>`
            )
            .join("")}
        </div>
      </div>`
      : `<p class="course-note">This module has no quiz configured, so finishing it will complete the module directly.</p>`;

    const overlay = createModal(
      "courseModal",
      `<div class="course-content" id="courseContent"></div>`
    );
    overlay.classList.add("course-modal");
    $("#courseContent", overlay).innerHTML = `
      <h3 class="modal-title">${escapeHtml(module.skill)}</h3>
      <p class="modal-subtitle">Free courses and videos selected for this skill gap.</p>
      <div class="course-status-row">
        <span>${moduleStatusLabel(module)}</span>
        <span class="match-score">${Math.round(moduleProgress(module))}%</span>
      </div>
      <div class="progress-track"><div class="progress-fill fill-secondary" style="width:${Math.round(moduleProgress(module))}%"></div></div>
      ${unlocked ? "" : `<p class="form-status error">Pass the previous module quiz to unlock this course.</p>`}
      ${videoMarkup}
      <div class="course-actions">
        <button type="button" class="btn btn-glass" id="courseStart" ${unlocked ? "" : "disabled"}>Start learning</button>
        <button type="button" class="btn btn-primary" id="courseQuizSubmit" ${unlocked ? "" : "disabled"}>${module.quiz?.length ? `Submit quiz (${module.quiz.length} questions)` : "Finish module"}</button>
      </div>
      ${videoLinksMarkup}
      <p class="course-note">If YouTube blocks an embed, use the fallback or playlist search. Progress still updates when you open these links.</p>
      <div class="course-search-grid">${youtubeMarkup}</div>
      <div class="course-links">${resourceMarkup}</div>
      ${quizMarkup}
      <p class="form-status" id="courseStatus" role="status" aria-live="polite"></p>`;

    const status = $("#courseStatus", overlay);
    const setStatus = (message, type) => {
      status.textContent = message;
      status.className = `form-status ${type}`;
    };

    /* Live quiz progress tracking */
    const progressBadge = overlay.querySelector("#quizProgressBadge");
    if (progressBadge && module.quiz?.length) {
      const totalQ = module.quiz.length;
      overlay.querySelectorAll("input[type=radio]").forEach((radio) => {
        radio.addEventListener("change", () => {
          let answered = 0;
          for (let i = 0; i < totalQ; i++) {
            if (overlay.querySelector(`input[name="quiz_${i}"]:checked`)) answered++;
          }
          progressBadge.textContent = `${answered} / ${totalQ} answered`;
          progressBadge.classList.toggle("quiz-progress-complete", answered === totalQ);
        });
      });
    }

    $("#courseStart", overlay)?.addEventListener("click", async () => {
      try {
        await startModule(module);
        await recordCourseProgress(module, Math.max(moduleProgress(module), 25), "course", "Started learning");
        setStatus("Module started. Finish the quiz to unlock the next one.", "success");
      } catch (error) {
        setStatus(error.message, "error");
      }
    });

    $("#courseQuizSubmit", overlay)?.addEventListener("click", async () => {
      try {
        const answers = module.quiz?.length
          ? module.quiz.map((_, questionIndex) => {
              const selected = $(`input[name="quiz_${questionIndex}"]:checked`, overlay);
              return selected ? Number(selected.value) : null;
            })
          : [];
        if (module.quiz?.length && answers.some((a) => a === null)) {
          const unanswered = answers.filter((a) => a === null).length;
          if (!confirm(`You have ${unanswered} unanswered question${unanswered > 1 ? "s" : ""}. Submit anyway?`)) return;
        }
        const result = await submitModuleQuiz(module, answers);
        const percentage = result?.result?.percentage;
        if (result?.result?.passed) {
          setStatus(`${result.message} Next module unlocked.`, "success");
        } else if (typeof percentage === "number") {
          setStatus(`Quiz submitted. Score: ${percentage}%. Review and try again.`, "error");
        } else {
          setStatus(result?.message || "Module completed.", "success");
        }
      } catch (error) {
        setStatus(error.message, "error");
      }
    });

    $$(".course-link", overlay).forEach((link) => {
      link.addEventListener("click", () => {
        if (!unlocked) return;
        recordCourseProgress(module, Math.max(moduleProgress(module), 50), "resource", link.dataset.resourceTitle).catch(() => {});
      });
    });

    return overlay;
  }

  function openCourseModal(module) {
    openModal(buildCourseModal(module));
    if (isModuleUnlocked(module)) {
      recordCourseProgress(module, Math.max(moduleProgress(module), 10), "course", "Course opened").catch(() => {});
    }
  }

  function bindRoadmapCards() {
    $$("#roadmap .roadmap-card").forEach((card) => {
      const open = () => {
        const order = Number(card.dataset.moduleOrder);
        const module = findRoadmapModule(order);
        if (module) openCourseModal(module);
      };
      card.addEventListener("click", open);
      card.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          open();
        }
      });
    });
  }

  function setDashboardValue(label, value, suffix = "") {
    const stat = $$(".dash-stat").find((item) =>
      $(".dash-stat-label", item)?.textContent.trim() === label
    );
    const span = $(".dash-stat-value span", stat);
    if (!span) return;
    span.dataset.counter = String(value);
    span.textContent = String(value);
    const valueEl = $(".dash-stat-value", stat);
    if (valueEl && suffix && !valueEl.textContent.trim().endsWith(suffix)) {
      valueEl.lastChild.textContent = suffix;
    }
  }

  function updateDashboardBars(labels = [], values = []) {
    const bars = $$(".bar-chart .bar");
    const max = Math.max(...values, 1);
    bars.forEach((bar, index) => {
      const value = values[index] || 0;
      const percent = value ? Math.max(18, Math.round((value / max) * 100)) : 6;
      bar.dataset.bar = String(percent);
      bar.style.setProperty("--bar-h", `${percent}%`);
      const label = $(".bar-label", bar);
      if (label && labels[index]) label.textContent = labels[index];
    });
  }

  function updateDashboardFromRoadmap(roadmap) {
    const modules = roadmap?.modules || [];
    if (!modules.length) return;
    const completed = modules.filter((module) => moduleProgress(module) >= 100).length;
    const averageProgress = Math.round(
      modules.reduce((sum, module) => sum + moduleProgress(module), 0) / modules.length
    );

    setDashboardValue("Skills mastered", completed);
    setDashboardValue("Roadmap progress", averageProgress, "%");
  }

  async function refreshDashboardSummary() {
    if (!auth.isLoggedIn) return;
    try {
      const summary = await api("/analytics/summary");
      setDashboardValue("Skills mastered", summary.roadmap?.completed_modules || 0);
      setDashboardValue("Roadmap progress", Math.round(summary.roadmap?.completion_percentage || 0), "%");
      setDashboardValue("Avg quiz score", Math.round(summary.quizzes?.average_percentage || 0), "%");
      updateDashboardBars(summary.weekly_activity?.labels || [], summary.weekly_activity?.values || []);
    } catch {
      /* Dashboard remains in demo state until the user has profile data. */
    }
  }

  async function hydrateLearningState() {
    if (!auth.isLoggedIn) return;
    await refreshDashboardSummary();
    try {
      const data = await api("/roadmap");
      renderRoadmapOnPage(data.roadmap);
    } catch {
      /* A user may be signed in before generating their first roadmap. */
    }
  }

  function renderTargetRoleAnalysisOnPage(upload, analysis) {
    const heroCard = $(".hero-card");
    const demoCard = $(".demo-visual");
    const skills = upload.parsed?.skills_found || [];
    const gap = analysis.gap || {};
    const recommendations = analysis.recommendations || [];

    if (heroCard) {
      const fileName = $(".analysis-name", heroCard);
      const meta = $(".analysis-meta", heroCard);
      const statusChip = $(".analysis-row .chip", heroCard);
      const matchBlocks = $$(".match-block", heroCard);
      const chips = $(".skill-chips", heroCard);
      const topThree = [
        {
          title: gap.title || analysis.target_career,
          match_score: gap.readiness ?? 0,
          matched_skills: gap.matched_skills || [],
          missing_core_skills: gap.missing_core_skills || [],
          missing_bonus_skills: gap.missing_bonus_skills || [],
        },
        ...recommendations.slice(0, 2),
      ];

      if (fileName) fileName.textContent = upload.file_name || "resume.pdf";
      if (meta) {
        const skillCount = upload.parsed?.skills_count ?? skills.length;
        const experienceYears = upload.parsed?.experience_years ?? 0;
        meta.textContent = `Parsed · ${skillCount} skills extracted · ${experienceYears} yrs experience · Targeting ${analysis.target_career}`;
      }
      if (statusChip) statusChip.textContent = "Targeted";

      matchBlocks.forEach((block, index) => {
        const match = topThree[index];
        if (!match) {
          block.style.display = index === 0 ? "grid" : "none";
          return;
        }

        block.style.display = "grid";
        const title = $(".match-head span:first-child", block);
        const score = $(".match-score", block);
        const fill = $(".progress-fill", block);
        const roundedScore = Math.round(clamp(match.match_score, 0, 100));
        if (title) title.textContent = match.title;
        if (score) score.textContent = `${roundedScore}%`;
        if (fill) {
          fill.removeAttribute("data-progress");
          fill.style.transition = "none";
          fill.style.width = `${roundedScore}%`;
          void fill.offsetWidth;
          fill.style.transition = "";
        }
      });

      if (chips) {
        const matched = gap.matched_skills || [];
        const missing = gap.missing_core_skills || [];
        const bonus = gap.missing_bonus_skills || [];
        const chipMarkup = [
          ...matched.slice(0, 3).map((skill) => `<span class="chip">${escapeHtml(skill)}</span>`),
          ...missing.slice(0, 2).map((skill) => `<span class="chip chip-gap">+ ${escapeHtml(skill)}</span>`),
          ...bonus.slice(0, 1).map((skill) => `<span class="chip chip-gap">+ ${escapeHtml(skill)}</span>`),
        ];

        chips.innerHTML = chipMarkup.length
          ? chipMarkup.join("")
          : `<span class="chip chip-gap">No skills detected</span>`;
      }
    }

    if (demoCard && gap.title) {
      const demoTitle = $(".demo-header .demo-title", demoCard);
      const demoSkills = $$(".demo-skill", demoCard);
      const demoFooter = $(".demo-footer .demo-verdict", demoCard);
      const breakdown = [
        ...[...(gap.matched_skills || [])].slice(0, 3).map((skill) => ({ label: skill, score: 100, fillClass: "fill-success" })),
        ...[...(gap.missing_core_skills || [])].slice(0, 2).map((skill) => ({ label: skill, score: 35, fillClass: "fill-warning" })),
      ].slice(0, demoSkills.length);

      if (demoTitle) demoTitle.textContent = `Skill Gap Analysis — ${gap.title}`;

      demoSkills.forEach((row, index) => {
        const data = breakdown[index];
        if (!data) {
          row.style.display = "none";
          return;
        }

        row.style.display = "grid";
        const label = $(".demo-skill-head span:first-child", row);
        const value = $(".demo-skill-head span:last-child", row);
        const fill = $(".progress-fill", row);
        const roundedScore = Math.round(clamp(data.score, 0, 100));
        if (label) label.textContent = data.label;
        if (value) value.textContent = `${roundedScore}%`;
        if (fill) {
          fill.className = `progress-fill ${data.fillClass}`;
          fill.removeAttribute("data-bar");
          fill.style.transition = "none";
          fill.style.width = `${roundedScore}%`;
          void fill.offsetWidth;
          fill.style.transition = "";
        }
      });

      if (demoFooter) {
        const missingCount = gap.missing_core_skills?.length || 0;
        const weeks = gap.estimated_weeks || Math.max(1, missingCount * 2 + (gap.missing_bonus_skills?.length || 0));
        demoFooter.innerHTML = `Verdict: <strong>${missingCount} critical gaps</strong> — est. ${weeks} weeks to close`;
      }
    }

    renderRoadmapOnPage(analysis.roadmap);
    refreshDashboardSummary();
  }

  function openResumeModal() {
    openModal(buildResumeModal());
  }

  /* ============ 24. AUTH-AWARE NAVBAR & CTA WIRING ============ */

  function updateNavbarAuthState() {
    const signInBtn = $(".nav-actions .btn-ghost");
    const primaryBtn = $(".nav-actions .btn-primary");
    if (!signInBtn || !primaryBtn) return;

    if (auth.isLoggedIn && auth.user) {
      signInBtn.textContent = `Hi, ${auth.user.name.split(" ")[0]}`;
      primaryBtn.childNodes[0].textContent = "Log out ";
      primaryBtn.dataset.authAction = "logout";
    } else {
      signInBtn.textContent = "Sign in";
      primaryBtn.childNodes[0].textContent = "Get started ";
      primaryBtn.dataset.authAction = "register";
    }
  }

  function initAuthWiring() {
    injectModalStyles();

    const signInBtn = $(".nav-actions .btn-ghost");
    const primaryBtn = $(".nav-actions .btn-primary");
    const heroAnalyzeBtn = $(".hero-cta .btn-primary");

    if (signInBtn) {
      signInBtn.addEventListener("click", (event) => {
        event.preventDefault();
        if (auth.isLoggedIn) {
          openResumeModal();
        } else {
          openAuthModal("login");
        }
      });
    }

    if (primaryBtn) {
      primaryBtn.addEventListener("click", (event) => {
        event.preventDefault();
        if (primaryBtn.dataset.authAction === "logout") {
          auth.clear();
          updateNavbarAuthState();
        } else {
          openAuthModal("register");
        }
      });
    }

    if (heroAnalyzeBtn) {
      heroAnalyzeBtn.addEventListener("click", (event) => {
        event.preventDefault();
        openResumeModal();
      });
    }

    // Validate a stored session on load; clear it if the token expired.
    if (auth.isLoggedIn) {
      api("/auth/me")
        .then(() => hydrateLearningState())
        .catch(() => {
          auth.clear();
          updateNavbarAuthState();
        });
    }

    updateNavbarAuthState();
  }

  /* ============ STREAK TRACKING ============ */

  function initStreak() {
    const today = new Date();
    const todayStr = today.toISOString().split("T")[0];
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayStr = yesterday.toISOString().split("T")[0];

    let streakData = JSON.parse(localStorage.getItem("careerai_streak") || "null");
    let streak = 0;
    let message = "";

    if (!streakData) {
      streak = 1;
      message = "Day 1 — start your streak!";
      streakData = { count: 1, lastVisit: todayStr };
    } else {
      const lastVisit = streakData.lastVisit;

      if (lastVisit === todayStr) {
        streak = streakData.count;
        message = streak > 1 ? `Keeping it alive for ${streak} days!` : "Day 1 — keep going!";
      } else if (lastVisit === yesterdayStr) {
        streak = streakData.count + 1;
        streakData.count = streak;
        streakData.lastVisit = todayStr;
        message = streak >= 7 ? `${streak} days — on fire! 🔥` : `${streak} days strong!`;
      } else {
        const missed = Math.floor((today - new Date(lastVisit)) / (1000 * 60 * 60 * 24));
        message = `Streak lost! Missed ${missed} day${missed > 1 ? "s" : ""}. New streak starts today!`;
        streak = 1;
        streakData = { count: 1, lastVisit: todayStr };
      }
    }

    localStorage.setItem("careerai_streak", JSON.stringify(streakData));

    const streakFloat = document.getElementById("streakFloatValue");
    const streakMsg = document.getElementById("streakMsg");
    const dashStreakCounter = document.getElementById("dashStreakCounter");

    if (streakFloat) {
      streakFloat.textContent = streak > 0 ? `${streak} day${streak > 1 ? "s" : ""} 🔥` : "0 days 🔥";
    }

    if (streakMsg) {
      if (streakData.count >= 2) {
        streakMsg.style.display = "block";
        streakMsg.textContent = message;
      } else if (message.includes("lost")) {
        streakMsg.style.display = "block";
        streakMsg.textContent = message;
      }
    }

    if (dashStreakCounter) {
      dashStreakCounter.setAttribute("data-counter", streak);
      dashStreakCounter.textContent = streak;
    }
  }

  /* ============ BOOT ============ */

  document.addEventListener("DOMContentLoaded", () => {
    /* Critical-path: run immediately */
    initLoader();
    initScrollProgress();
    initNavbar();
    initCursorSpotlight();
    initTyping();
    initReveal();
    initAuthWiring();
    initThemeToggle();

    /* Non-critical / below-fold: defer until idle */
    const _idle = (fn) =>
      typeof requestIdleCallback === "function"
        ? requestIdleCallback(fn, { timeout: 2000 })
        : setTimeout(fn, 0);
    _idle(() => {
      initCounters();
      initStreak();
      initProgressBars();
      initLineChart();
      initCardGlow();
      initRipple();
      initMarquee();
      initFaq();
      initContactForm();
      initBackToTop();
      initDemandBadges();
      initCompareCareers();
      initRadarChart();
      initDownloadReport();
      initTransitionAdvisor();
      initLearningPace();
      initSkillMarket();
    });
  });

  /* ============ THEME TOGGLE ============ */
  function initThemeToggle() {
    const btn = $("#themeToggle");
    if (!btn) return;
    const saved = localStorage.getItem("careerai_theme");
    if (saved === "light") document.body.classList.add("light-mode");
    btn.addEventListener("click", () => {
      document.body.classList.toggle("light-mode");
      localStorage.setItem(
        "careerai_theme",
        document.body.classList.contains("light-mode") ? "light" : "dark"
      );
    });
  }

  /* ============ DYNAMIC DEMAND BADGES ============ */
  const DEMAND_MAP = {
    python: "hot", javascript: "hot", typescript: "hot", react: "hot",
    nodejs: "growing", docker: "hot", kubernetes: "growing", "machine learning": "hot",
    "deep learning": "hot", tensorflow: "growing", pytorch: "growing",
    sql: "stable", java: "stable", cplusplus: "stable", go: "growing",
    rust: "growing", aws: "hot", azure: "growing", gcp: "growing",
    "data analysis": "growing", pandas: "growing", numpy: "growing",
    git: "stable", linux: "stable", rest: "stable", graphql: "growing",
    figma: "growing", ux: "stable", "power bi": "growing", tableau: "stable",
  };
  const DEMAND_LABELS = { hot: "🔥 Hot", growing: "📈 Growing", stable: "⚖️ Stable" };
  const DEMAND_TEXT = {
    hot: "High demand — most job postings require this skill",
    growing: "Growing demand — increasingly sought by employers",
    stable: "Stable demand — consistently valued across roles",
  };

  function initDemandBadges() {
    $$(".chip-match, .chip[data-skill]").forEach((chip) => {
      const skill = (chip.dataset.skill || chip.textContent.replace(/["+)/].*/g, "").trim()).toLowerCase();
      const level = DEMAND_MAP[skill] || "stable";
      const badge = document.createElement("span");
      badge.className = `badge-demand ${level}`;
      badge.textContent = DEMAND_LABELS[level];
      badge.title = DEMAND_TEXT[level];
      chip.appendChild(badge);
    });
  }

  const CAREER_CATALOG_DETAILS = {
    "Frontend Developer": {
      core_skills: ["HTML", "CSS", "JavaScript", "React", "Git"],
      bonus_skills: ["TypeScript", "Tailwind CSS", "Redux", "Next.js"],
      market: "High frontend hiring velocity",
      salary_inr: { min: 400000, max: 1200000, avg: 700000, exp: "0-3 yrs" },
    },
    "Backend Developer": {
      core_skills: ["Python", "Flask", "SQL", "REST API", "Git"],
      bonus_skills: ["Docker", "MongoDB", "Node.js", "Redis"],
      market: "Strong API and platform demand",
      salary_inr: { min: 450000, max: 1400000, avg: 800000, exp: "0-3 yrs" },
    },
    "Full-Stack Developer": {
      core_skills: ["HTML", "CSS", "JavaScript", "React", "Node.js", "SQL"],
      bonus_skills: ["MongoDB", "Docker", "TypeScript", "Git"],
      market: "Broad product-team demand",
      salary_inr: { min: 500000, max: 1600000, avg: 900000, exp: "0-4 yrs" },
    },
    "Data Scientist": {
      core_skills: ["Python", "Statistics", "Pandas", "Machine Learning", "Data Visualization"],
      bonus_skills: ["SQL", "Deep Learning", "NumPy", "Tableau"],
      market: "High analytics and AI demand",
      salary_inr: { min: 600000, max: 2000000, avg: 1100000, exp: "0-3 yrs" },
    },
    "Machine Learning Engineer": {
      core_skills: ["Python", "Machine Learning", "Deep Learning", "Scikit-learn", "TensorFlow"],
      bonus_skills: ["MLOps", "Docker", "NumPy", "Natural Language Processing"],
      market: "Premium AI engineering demand",
      salary_inr: { min: 700000, max: 2500000, avg: 1300000, exp: "1-4 yrs" },
    },
    "Data Analyst": {
      core_skills: ["Excel", "SQL", "Data Analysis", "Data Visualization", "Statistics"],
      bonus_skills: ["Python", "Power BI", "Tableau", "Pandas"],
      market: "Consistent business intelligence demand",
      salary_inr: { min: 350000, max: 900000, avg: 550000, exp: "0-2 yrs" },
    },
    "DevOps Engineer": {
      core_skills: ["Linux", "Docker", "CI/CD", "Git", "Bash"],
      bonus_skills: ["Kubernetes", "AWS", "Terraform", "Jenkins"],
      market: "Strong cloud automation demand",
      salary_inr: { min: 500000, max: 1800000, avg: 950000, exp: "0-3 yrs" },
    },
    "UI/UX Designer": {
      core_skills: ["UI/UX Design", "Figma", "Wireframing", "Prototyping"],
      bonus_skills: ["HTML", "CSS", "Adobe XD", "Communication"],
      market: "Growing product design demand",
      salary_inr: { min: 350000, max: 1000000, avg: 600000, exp: "0-3 yrs" },
    },
  };

  const DEMO_MARKET_SKILLS = [
    { skill: "Python", demand: 95, salary_range: [90000, 140000], trend: "hot", related_roles: ["Data Scientist", "ML Engineer"], market_value: "strong" },
    { skill: "React", demand: 90, salary_range: [90000, 150000], trend: "hot", related_roles: ["Frontend Developer", "Full-Stack Developer"], market_value: "premium" },
    { skill: "Docker", demand: 85, salary_range: [95000, 155000], trend: "hot", related_roles: ["DevOps Engineer", "Backend Developer"], market_value: "premium" },
    { skill: "SQL", demand: 85, salary_range: [75000, 125000], trend: "stable", related_roles: ["Data Analyst", "Backend Developer"], market_value: "strong" },
    { skill: "Figma", demand: 78, salary_range: [70000, 120000], trend: "hot", related_roles: ["UI/UX Designer"], market_value: "strong" },
  ];

  function skillChips(skills, limit = 4) {
    const visible = (skills || []).slice(0, limit);
    const extra = Math.max(0, (skills || []).length - visible.length);
    return visible.map((skill) => `<span class="chip">${escapeHtml(skill)}</span>`).join("") +
      (extra ? `<span class="chip">+${extra} more</span>` : "");
  }

  function progressPill(value) {
    const score = clamp(Number(value) || 0, 0, 100);
    return `<span class="metric-pill">${score}%</span><div class="mini-progress"><span style="width:${score}%"></span></div>`;
  }

  /* ============ COMPARE CAREERS ============ */
  function initCompareCareers() {
    const selectA = $("#compareA");
    const selectB = $("#compareB");
    const result = $("#compareResult");
    if (!selectA || !selectB || !result) return;

    let catalog = [];

    async function load() {
      try {
        const res = await api("/career/list");
        catalog = res.careers || [];
        catalog.forEach((c) => {
          selectA.add(new Option(`${c.title} — ${c.category}`, c.title));
          selectB.add(new Option(`${c.title} — ${c.category}`, c.title));
        });
        if (catalog.length >= 2) {
          selectA.selectedIndex = 1;
          selectB.selectedIndex = 2;
          runCompare();
        }
      } catch (_) {}
    }

    async function runCompare() {
      const titleA = selectA.value;
      const titleB = selectB.value;
      if (!titleA || !titleB || titleA === titleB) {
        result.style.display = "none";
        return;
      }

      const token = auth.token;
      if (token) {
        // Logged-in: use real gap analysis
        try {
          const [resA, resB] = await Promise.all([
            api("/career/gap", { method: "POST", body: { career: titleA } }),
            api("/career/gap", { method: "POST", body: { career: titleB } }),
          ]);
          fillCompare(resA.gap || {}, resB.gap || {});
          result.style.display = "";
          return;
        } catch (_) {}
      }

      // Fallback: catalog-based comparison (no auth)
      const a = catalog.find((c) => c.title === titleA) || {};
      const b = catalog.find((c) => c.title === titleB) || {};
      fillCompareCatalog(a, b);
      result.style.display = "";
    }

    function setCompareRow(idA, idB, valueA, valueB) {
      const aCell = $(idA);
      const bCell = $(idB);
      if (aCell) aCell.innerHTML = valueA;
      if (bCell) bCell.innerHTML = valueB;
    }

    function fillCompare(a, b) {
      const aCore = (a.matched_skills || []).length + (a.missing_core_skills || []).length;
      const bCore = (b.matched_skills || []).length + (b.missing_core_skills || []).length;
      $("#cmpAName").textContent = a.title || "Career A";
      $("#cmpBName").textContent = b.title || "Career B";
      setCompareRow("#cmpAMatch", "#cmpBMatch", progressPill(a.readiness), progressPill(b.readiness));
      setCompareRow("#cmpACore", "#cmpBCore", `${aCore} core`, `${bCore} core`);
      setCompareRow("#cmpAMatched", "#cmpBMatched", skillChips(a.matched_skills), skillChips(b.matched_skills));
      setCompareRow(
        "#cmpAGaps",
        "#cmpBGaps",
        skillChips([...(a.missing_core_skills || []), ...(a.missing_bonus_skills || [])], 5),
        skillChips([...(b.missing_core_skills || []), ...(b.missing_bonus_skills || [])], 5)
      );
      setCompareRow(
        "#cmpAWeeks",
        "#cmpBWeeks",
        a.estimated_weeks != null ? `${a.estimated_weeks} weeks` : "Run analysis",
        b.estimated_weeks != null ? `${b.estimated_weeks} weeks` : "Run analysis"
      );
      return;
      $("#cmpAName").textContent = a.title || "—";
      $("#cmpBName").textContent = b.title || "—";
      $("#cmpAMatch").textContent = a.readiness != null ? a.readiness + "%" : "—";
      $("#cmpBMatch").textContent = b.readiness != null ? b.readiness + "%" : "—";
      $("#cmpACore").textContent = aCore;
      $("#cmpBCore").textContent = bCore;
      $("#cmpAMatched").textContent = (a.matched_skills || []).length;
      $("#cmpBMatched").textContent = (b.matched_skills || []).length;
      $("#cmpAGaps").textContent = (a.missing_core_skills || []).length + (a.missing_bonus_skills || []).length;
      $("#cmpBGaps").textContent = (b.missing_core_skills || []).length + (b.missing_bonus_skills || []).length;
      $("#cmpAWeeks").textContent = a.estimated_weeks != null ? a.estimated_weeks + "w" : "—";
      $("#cmpBWeeks").textContent = b.estimated_weeks != null ? b.estimated_weeks + "w" : "—";
    }

    function fillCompareCatalog(a, b) {
      const detailA = CAREER_CATALOG_DETAILS[a.title] || {};
      const detailB = CAREER_CATALOG_DETAILS[b.title] || {};
      const weeksA = Math.max(4, ((detailA.core_skills || []).length * 2) + (detailA.bonus_skills || []).length);
      const weeksB = Math.max(4, ((detailB.core_skills || []).length * 2) + (detailB.bonus_skills || []).length);
      $("#cmpAName").textContent = a.title || "Career A";
      $("#cmpBName").textContent = b.title || "Career B";
      setCompareRow("#cmpAMatch", "#cmpBMatch", escapeHtml(detailA.market || "Sign in for readiness"), escapeHtml(detailB.market || "Sign in for readiness"));
      setCompareRow("#cmpACore", "#cmpBCore", `${(detailA.core_skills || []).length} core`, `${(detailB.core_skills || []).length} core`);
      setCompareRow("#cmpAMatched", "#cmpBMatched", skillChips(detailA.core_skills), skillChips(detailB.core_skills));
      setCompareRow("#cmpAGaps", "#cmpBGaps", skillChips(detailA.bonus_skills), skillChips(detailB.bonus_skills));
      setCompareRow("#cmpAWeeks", "#cmpBWeeks", `${weeksA} weeks full path`, `${weeksB} weeks full path`);
      return;
      $("#cmpAName").textContent = a.title || "—";
      $("#cmpBName").textContent = b.title || "—";
      $("#cmpAMatch").textContent = "Sign in to compare";
      $("#cmpBMatch").textContent = "Sign in to compare";
      $("#cmpACore").textContent = "—";
      $("#cmpBCore").textContent = "—";
      $("#cmpAMatched").textContent = "—";
      $("#cmpBMatched").textContent = "—";
      $("#cmpAGaps").textContent = "—";
      $("#cmpBGaps").textContent = "—";
      $("#cmpAWeeks").textContent = "—";
      $("#cmpBWeeks").textContent = "—";
    }

    selectA.addEventListener("change", runCompare);
    selectB.addEventListener("change", runCompare);
    load();
  }

  /* ============ RADAR CHART ============ */
  function initRadarChart() {
    const canvas = $("#radarChart");
    const wrap = $("#radarWrap");
    if (!canvas || !wrap) return;
    const ctx = canvas.getContext("2d");

    /* Skill-to-dimension mapping: each label lists skills that contribute to it.
       Score = (matched intersect dimSkills) / dimSkills.length, blended with readiness. */
    const DIM_MAP = {
      'Frontend Developer': [
        { label: 'JS Core', skills: ['JavaScript','TypeScript','ES6','DOM'] },
        { label: 'React/SPA', skills: ['React','Next.js','Vue','Angular'] },
        { label: 'CSS/UI', skills: ['CSS','Tailwind CSS','HTML','Sass'] },
        { label: 'Responsive', skills: ['Responsive Design','CSS','HTML','Media Queries'] },
        { label: 'Performance', skills: ['Webpack','Lighthouse','Vite','Lazy Loading'] },
        { label: 'Accessibility', skills: ['A11y','ARIA','Semantic HTML'] },
        { label: 'Testing', skills: ['Jest','Cypress','React Testing Library'] },
        { label: 'Tooling', skills: ['Git','npm','CI/CD','Docker'] },
      ],
      'Backend Developer': [
        { label: 'Language', skills: ['Python','Java','Go','Node.js'] },
        { label: 'Database', skills: ['SQL','PostgreSQL','MongoDB','Redis'] },
        { label: 'APIs', skills: ['REST API','GraphQL','Flask','Django'] },
        { label: 'Security', skills: ['Authentication','JWT','OAuth','CORS'] },
        { label: 'Caching', skills: ['Redis','Memcached','CDN'] },
        { label: 'Containers', skills: ['Docker','Kubernetes','Podman'] },
        { label: 'Testing', skills: ['Pytest','Unit Testing','Integration Testing'] },
        { label: 'Version Ctrl', skills: ['Git','GitHub','CI/CD'] },
      ],
      'Data Scientist': [
        { label: 'Statistics', skills: ['Statistics','Probability','A/B Testing'] },
        { label: 'Programming', skills: ['Python','R','SQL','Pandas'] },
        { label: 'ML', skills: ['Machine Learning','Scikit-learn','XGBoost'] },
        { label: 'Visualization', skills: ['Data Visualization','Tableau','Matplotlib'] },
        { label: 'Data Wrangling', skills: ['SQL','Pandas','NumPy','ETL'] },
        { label: 'NLP', skills: ['NLP','spaCy','NLTK'] },
        { label: 'Deep Learning', skills: ['Deep Learning','TensorFlow','PyTorch'] },
        { label: 'Communication', skills: ['Data Storytelling','Presentation','Communication'] },
      ],
      'Full-Stack Developer': [
        { label: 'Frontend', skills: ['React','JavaScript','HTML','CSS'] },
        { label: 'Backend', skills: ['Node.js','Python','Flask','Express'] },
        { label: 'Database', skills: ['SQL','MongoDB','PostgreSQL'] },
        { label: 'DevOps', skills: ['Docker','CI/CD','AWS','Git'] },
        { label: 'APIs', skills: ['REST API','GraphQL','WebSockets'] },
        { label: 'Testing', skills: ['Jest','Cypress','Unit Testing'] },
        { label: 'Security', skills: ['JWT','Authentication','HTTPS'] },
        { label: 'Tooling', skills: ['Git','npm','Webpack'] },
      ],
      'Machine Learning Engineer': [
        { label: 'ML Theory', skills: ['Machine Learning','Statistics','Linear Algebra'] },
        { label: 'Programming', skills: ['Python','C++','SQL'] },
        { label: 'Deep Learning', skills: ['Deep Learning','TensorFlow','PyTorch'] },
        { label: 'MLOps', skills: ['MLOps','MLflow','Kubeflow'] },
        { label: 'Data Pipeline', skills: ['SQL','Pandas','Spark','ETL'] },
        { label: 'Infrastructure', skills: ['Docker','Kubernetes','AWS'] },
        { label: 'NLP/CV', skills: ['NLP','Computer Vision','OpenCV'] },
        { label: 'Feature Eng', skills: ['Feature Engineering','Pandas','NumPy'] },
      ],
      'Data Analyst': [
        { label: 'SQL', skills: ['SQL','MySQL','PostgreSQL'] },
        { label: 'Spreadsheets', skills: ['Excel','Google Sheets','Pivot Tables'] },
        { label: 'Visualization', skills: ['Tableau','Power BI','Data Visualization'] },
        { label: 'Statistics', skills: ['Statistics','Regression','Hypothesis Testing'] },
        { label: 'Programming', skills: ['Python','R','Pandas'] },
        { label: 'Storytelling', skills: ['Data Storytelling','Communication'] },
        { label: 'Domain', skills: ['Business Analysis','Domain Knowledge'] },
        { label: 'ETL', skills: ['ETL','Data Cleaning','Data Wrangling'] },
      ],
      'DevOps Engineer': [
        { label: 'Linux', skills: ['Linux','Bash','Shell Scripting'] },
        { label: 'CI/CD', skills: ['CI/CD','Jenkins','GitHub Actions'] },
        { label: 'Containers', skills: ['Docker','Kubernetes','Helm'] },
        { label: 'IaC', skills: ['Terraform','Ansible','CloudFormation'] },
        { label: 'Monitoring', skills: ['Prometheus','Grafana','ELK Stack'] },
        { label: 'Security', skills: ['DevSecOps','SSO','Secrets Management'] },
        { label: 'Scripting', skills: ['Python','Bash','Go'] },
        { label: 'Cloud', skills: ['AWS','Azure','GCP'] },
      ],
      '_default': [
        { label: 'Programming', skills: ['Python','JavaScript','Java','Programming'] },
        { label: 'Data Skills', skills: ['SQL','Excel','Data Analysis'] },
        { label: 'Communication', skills: ['Communication','Presentation','Writing'] },
        { label: 'Problem Solving', skills: ['Problem Solving','Critical Thinking'] },
        { label: 'Version Control', skills: ['Git','GitHub'] },
        { label: 'Testing', skills: ['Unit Testing','QA'] },
        { label: 'Documentation', skills: ['Technical Writing','Documentation'] },
        { label: 'Soft Skills', skills: ['Teamwork','Leadership','Agile'] },
      ],
    };

    function dimScore(matched, dimSkills) {
      const ms = new Set((matched || []).map(s => s.toLowerCase()));
      let hits = 0;
      for (const ds of dimSkills) if (ms.has(ds.toLowerCase())) hits++;
      return hits / (dimSkills.length || 1);
    }

    async function draw() {
      /* Demo defaults — 8 equal low bars */
      let labels = DIM_MAP['_default'].map(d => d.label);
      let values = labels.map(() => 15);
      let readiness = 0;

      try {
        const token = auth.token;
        if (token) {
          const res = await api("/career/analysis");
          const recs = (res.analysis || {}).recommendations || [];
          const gap = (res.analysis || {}).gap || {};
          readiness = recs.length > 0 ? Math.round(recs[0].match_score || 0) : 0;
          if (recs.length > 0) {
            const career = recs[0].career_path || 'General Tech';
            const dims = DIM_MAP[career] || DIM_MAP['_default'];
            const matched = gap.matched_skills || [];
            labels = dims.map(d => d.label);
            values = dims.map(d => {
              let raw = dimScore(matched, d.skills) * 100;
              /* Blend with overall match so chart isn't too extreme */
              raw = raw * 0.7 + readiness * 0.3;
              return Math.round(Math.min(100, Math.max(5, raw)));
            });
          }
        }
      } catch (_) {}

      wrap.style.display = "";
      drawRadarShape(ctx, canvas.width / 2, canvas.height / 2, 130, labels, values);
    }

    draw();
  }

  function drawRadarShape(ctx, cx, cy, r, labels, values) {
    const n = labels.length;
    const angleStep = (Math.PI * 2) / n;
    const startAngle = -Math.PI / 2;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);

    ctx.canvas.width = 340 * dpr;
    ctx.canvas.height = 340 * dpr;
    ctx.canvas.style.width = "340px";
    ctx.canvas.style.height = "340px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, 340, 340);

    // Grid rings
    for (let ring = 1; ring <= 5; ring++) {
      const rr = (r / 5) * ring;
      ctx.beginPath();
      for (let i = 0; i <= n; i++) {
        const angle = startAngle + angleStep * i;
        const x = cx + rr * Math.cos(angle);
        const y = cy + rr * Math.sin(angle);
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.strokeStyle = "rgba(99,102,241,0.15)";
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Axes
    for (let i = 0; i < n; i++) {
      const angle = startAngle + angleStep * i;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + r * Math.cos(angle), cy + r * Math.sin(angle));
      ctx.strokeStyle = "rgba(99,102,241,0.2)";
      ctx.stroke();
    }

    // Data polygon
    ctx.beginPath();
    values.forEach((v, i) => {
      const angle = startAngle + angleStep * i;
      const vr = (Math.min(v, 100) / 100) * r;
      const x = cx + vr * Math.cos(angle);
      const y = cy + vr * Math.sin(angle);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.fillStyle = "rgba(99,102,241,0.2)";
    ctx.fill();
    ctx.strokeStyle = "rgba(99,102,241,0.8)";
    ctx.lineWidth = 2;
    ctx.stroke();

    // Dots + labels
    values.forEach((v, i) => {
      const angle = startAngle + angleStep * i;
      const vr = (Math.min(v, 100) / 100) * r;
      const x = cx + vr * Math.cos(angle);
      const y = cy + vr * Math.sin(angle);

      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(99,102,241,1)";
      ctx.fill();

      const lx = cx + (r + 22) * Math.cos(angle);
      const ly = cy + (r + 22) * Math.sin(angle);
      ctx.fillStyle = "rgba(128,128,128,0.9)";
      ctx.font = "11px Inter, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(labels[i], lx, ly);
    });
  }

  /* ============ DOWNLOAD PDF REPORT ============ */
  function initDownloadReport() {
    const btn = $("#downloadReportBtn");
    const card = $("#downloadReportCard");
    if (!btn || !card) return;

    async function showButton() {
      try {
        const token = auth.token;
        if (token) {
          const res = await api("/career/analysis");
          if (res.analysis) card.style.display = "";
        }
      } catch (_) {}
    }

    btn.addEventListener("click", async () => {
      btn.disabled = true;
      btn.textContent = "Generating…";
      try {
        const res = await api("/career/analysis");
        const a = res.analysis || {};
        buildPDF(a);
      } catch (_) {
        alert("Run a career analysis first, then download your report.");
      } finally {
        btn.disabled = false;
        btn.textContent = "Download PDF Report";
      }
    });

    showButton();
  }

  function buildPDF(analysis) {
    const { jsPDF } = window.jspdf || {};
    if (!jsPDF) {
      alert("PDF library not loaded. Check your connection.");
      return;
    }

    const doc = new jsPDF();
    const gap = analysis.gap || {};
    const recs = analysis.recommendations || [];
    let y = 20;

    const addLine = (text, size = 11, bold = false) => {
      if (y > 270) { doc.addPage(); y = 20; }
      doc.setFontSize(size);
      doc.setFont("helvetica", bold ? "bold" : "normal");
      doc.text(text, 20, y);
      y += size * 0.5;
    };

    const addSpacing = (h = 6) => { y += h; };

    // Title
    doc.setFillColor(99, 102, 241);
    doc.rect(0, 0, 210, 40, "F");
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(22);
    doc.setFont("helvetica", "bold");
    doc.text("CareerAI — Career Analysis Report", 20, 18);
    doc.setFontSize(10);
    doc.text(`Generated: ${new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}`, 20, 28);
    doc.setFontSize(9);
    doc.text("AI-Driven Personalized Career Guidance System", 20, 35);
    doc.setTextColor(0, 0, 0);
    y = 52;

    // Target Career
    if (gap.title) {
      doc.setFillColor(240, 240, 255);
      doc.roundedRect(15, y - 6, 180, 32, 3, 3, "F");
      addLine("TARGET CAREER", 14, true);
      addLine(`Career:     ${gap.title}`, 11);
      addLine(`Category:   ${gap.category || "—"}`, 11);
      addLine(`Readiness:  ${gap.readiness != null ? gap.readiness + "%" : "—"}`, 11);
      addLine(`Est. Weeks: ${gap.estimated_weeks != null ? gap.estimated_weeks : "—"}`, 11);
      addSpacing(6);
    }

    // Skills you have
    if (gap.matched_skills && gap.matched_skills.length) {
      addLine(`SKILLS YOU HAVE (${gap.matched_skills.length})`, 12, true);
      gap.matched_skills.forEach((s) => addLine(`  ✓ ${s}`, 10));
      addSpacing(4);
    }

    // Missing core
    if (gap.missing_core_skills && gap.missing_core_skills.length) {
      addLine(`MISSING CORE SKILLS (${gap.missing_core_skills.length})`, 12, true);
      gap.missing_core_skills.forEach((s) => addLine(`  ✗ ${s}`, 10));
      addSpacing(4);
    }

    // Missing bonus
    if (gap.missing_bonus_skills && gap.missing_bonus_skills.length) {
      addLine(`MISSING BONUS SKILLS (${gap.missing_bonus_skills.length})`, 12, true);
      gap.missing_bonus_skills.forEach((s) => addLine(`  ○ ${s}`, 10));
      addSpacing(4);
    }

    // Top matches
    if (recs.length) {
      addLine("TOP CAREER MATCHES", 12, true);
      recs.forEach((r, i) => {
        const bar = "█".repeat(Math.round(r.match_score / 10)) + "░".repeat(10 - Math.round(r.match_score / 10));
        addLine(`  ${i + 1}. ${r.title}  ${bar}  ${r.match_score}%`, 10);
      });
      addSpacing(4);
    }

    // Footer
    addSpacing(8);
    doc.setFontSize(8);
    doc.setTextColor(150, 150, 150);
    doc.text("Generated by CareerAI — AI-Driven Personalized Career Guidance System", 20, y);

    doc.save(`CareerAI_Report_${(gap.title || "Analysis").replace(/\s+/g, "_")}.pdf`);
  }

  /* ============ TRANSITION ADVISOR ============ */
  function initTransitionAdvisor() {
    const select = $("#transitionCareer");
    const btn = $("#runAdvisorBtn");
    const resultDiv = $("#advisorResult");
    if (!select || !btn || !resultDiv) return;

    async function loadCareers() {
      try {
        const res = await api("/career/list");
        (res.careers || []).forEach((c) => {
          select.add(new Option(`${c.title} — ${c.category}`, c.title));
        });
      } catch (_) {}
    }

    btn.addEventListener("click", async () => {
      const career = select.value;
      if (!career) { alert("Select a target career first."); return; }
      btn.disabled = true;
      btn.textContent = "Analyzing\u2026";
      try {
        if (!auth.token) {
          renderAdvisor(buildDemoAdvisor(career));
          resultDiv.style.display = "";
          return;
        }
        const res = await api("/intelligence/transition-advisor", {
          method: "POST",
          body: { career },
        });
        renderAdvisor(res);
        resultDiv.style.display = "";
      } catch (e) {
        alert(e.message || "Failed. Make sure you have a profile with skills.");
      } finally {
        btn.disabled = false;
        btn.textContent = "Analyze";
      }
    });

    loadCareers();
  }

  function buildDemoAdvisor(career) {
    const detail = CAREER_CATALOG_DETAILS[career] || {};
    const core = detail.core_skills || [];
    const bonus = detail.bonus_skills || [];
    /* dynamic readiness from user's actual resume skills */
    const userSkills = new Set((lastAnalysis?.matched_skills || []).map(s => s.toLowerCase()));
    const coreHas = core.filter(s => userSkills.has(s.toLowerCase()));
    const coreMissing = core.filter(s => !userSkills.has(s.toLowerCase()));
    const bonusHas = bonus.filter(s => userSkills.has(s.toLowerCase()));
    const bonusMissing = bonus.filter(s => !userSkills.has(s.toLowerCase()));
    const totalWeight = core.length * 2 + bonus.length;
    const haveWeight = coreHas.length * 2 + bonusHas.length;
    const readiness = totalWeight > 0 ? Math.round((haveWeight / totalWeight) * 100) : 0;
    const difficulty = readiness >= 70 ? 'easy' : readiness >= 40 ? 'moderate' : 'hard';
    const weeksNeeded = coreMissing.length * 2 + bonusMissing.length;
    const estMonths = Math.max(1, Math.ceil(weeksNeeded / 3.5));

    /* phases built from actual gaps */
    const phases = [];
    if (coreHas.length) phases.push({ name: 'Leverage What You Have', description: 'You have ' + coreHas.length + ' core skill(s). Build proof-of-work.', items: coreHas.map(skill => ({ skill, action: 'Build a project showcasing this skill', weeks: 1 })) });
    if (coreMissing.length) phases.push({ name: 'Build Core Gaps', description: 'Fill ' + coreMissing.length + ' core gap(s) recruiters filter for.', items: coreMissing.map(skill => ({ skill, action: 'Complete practice and add to portfolio', weeks: 2 })) });
    if (bonusMissing.length) phases.push({ name: 'Differentiate', description: 'Add ' + bonusMissing.length + ' bonus skill(s) to stand out.', items: bonusMissing.slice(0, 4).map(skill => ({ skill, action: 'Create one applied mini project', weeks: 1 })) });
    if (!phases.length) phases.push({ name: 'Already Strong', description: 'Your skills cover this role well. Focus on projects.', items: [] });
    const milestones = [{ week: 1, milestone: 'Map your skills to ' + career + ' requirements' }];
    if (coreMissing.length) milestones.push({ week: Math.min(3, weeksNeeded), milestone: 'Complete first core skill: ' + coreMissing[0] });
    if (weeksNeeded > 2) milestones.push({ week: Math.round(weeksNeeded * 0.6), milestone: 'Build portfolio project demonstrating gap skills' });
    milestones.push({ week: Math.max(weeksNeeded, 1), milestone: 'Start applying with role-specific keywords' });

    return {
      career,
      readiness,
      difficulty_level: difficulty,
      salary_inr: sal,
      matched_core: coreHas,
      missing_core: coreMissing,
      matched_bonus: bonusHas,
      missing_bonus: bonusMissing,
      estimated_months: estMonths,
      phases: phases,
      milestones: milestones,
      resume_keywords: [...coreMissing.slice(0, 4), ...bonusMissing.slice(0, 2)],
    };
  }

  function renderAdvisor(data) {
    var diffColor = { easy: "#22C55E", moderate: "#F59E0B", hard: "#EF4444" };
    var diffEmoji = { easy: "\uD83D\uDFE2", moderate: "\uD83D\uDFE1", hard: "\uD83D\uDD34" };
    var diff = data.difficulty_level || "moderate";

    $("#advisorSummary").innerHTML =
      '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px">' +
      '<div style="text-align:center;padding:16px;background:var(--card);border-radius:12px;border:1px solid var(--border)">' +
        '<div style="font-size:2rem;font-weight:800;color:var(--primary)">' + (data.readiness || 0) + '%</div>' +
        '<div style="font-size:0.8rem;color:var(--muted)">Current Readiness</div></div>' +
      '<div style="text-align:center;padding:16px;background:var(--card);border-radius:12px;border:1px solid var(--border)">' +
        '<div style="font-size:2rem;font-weight:800;color:' + (diffColor[diff] || 'var(--primary)') + '">' +
        (diffEmoji[diff] || '') + ' ' + diff.charAt(0).toUpperCase() + diff.slice(1) + '</div>' +
        '<div style="font-size:0.8rem;color:var(--muted)">Difficulty</div></div>' +
      '<div style="text-align:center;padding:16px;background:var(--card);border-radius:12px;border:1px solid var(--border)">' +
        '<div style="font-size:2rem;font-weight:800;color:var(--accent)">' + (data.estimated_months || 0) + ' mo</div>' +
        '<div style="font-size:0.8rem;color:var(--muted)">Est. Timeline</div></div></div>';

    var phasesHtml = "";
    (data.phases || []).forEach(function(phase, pi) {
      var items = (phase.items || []).map(function(item) {
        var salary = item.salary_impact ? '<span style="color:#22C55E;font-weight:700;margin-left:8px">' + item.salary_impact + '</span>' : "";
        return '<li style="padding:6px 0;border-bottom:1px solid var(--border)">' +
          '<strong>' + item.skill + '</strong>' +
          '<span style="color:var(--muted);font-size:0.85rem;margin-left:8px">' + item.action + '</span>' + salary + '</li>';
      }).join("");
      phasesHtml += '<div style="margin-bottom:16px"><h4 style="margin-bottom:8px;color:var(--primary)">Phase ' + (pi + 1) + ': ' + phase.name + '</h4>' +
        '<p style="font-size:0.85rem;color:var(--muted);margin-bottom:8px">' + phase.description + '</p>' +
        '<ul style="list-style:none;padding:0">' + items + '</ul></div>';
    });
    $("#advisorPhases").innerHTML = phasesHtml;

    var milestones = (data.milestones || []).map(function(m) {
      return '<li style="display:flex;gap:12px;align-items:flex-start;padding:6px 0">' +
        '<span style="background:var(--primary);color:#fff;border-radius:999px;padding:2px 10px;font-size:0.75rem;font-weight:700;white-space:nowrap">Wk ' + m.week + '</span>' +
        '<span style="font-size:0.9rem">' + m.milestone + '</span></li>';
    }).join("");
    $("#advisorTimeline").innerHTML = milestones
      ? '<h4 style="margin-bottom:8px;color:var(--accent)">Milestones</h4><ul style="list-style:none;padding:0">' + milestones + '</ul>'
      : "";

    var kws = (data.resume_keywords || []).map(function(k) {
      return '<span style="display:inline-block;padding:4px 12px;margin:4px;border-radius:999px;font-size:0.8rem;font-weight:600;background:rgba(99,102,241,0.1);color:var(--primary);border:1px solid rgba(99,102,241,0.2)">' + k + '</span>';
    }).join("");
    $("#advisorKeywords").innerHTML = kws
      ? '<h4 style="margin-bottom:8px;color:var(--accent)">Add to Resume</h4>' + kws
      : "";
  }

  /* ============ LEARNING PACE ============ */
  function initLearningPace() {
    var container = $("#paceResult");
    if (!container) return;

    async function load() {
      try {
        if (!auth.token) {
          renderPace({
            career_target: "Machine Learning Engineer",
            quiz_stats: { total_quizzes: 4, average_score: 82, pass_rate: 75 },
            progress: { total_modules: 8, completed: 3, in_progress: 1, remaining: 5, active_days: 12 },
            recommendation: {
              hours_per_week: 7,
              sessions_per_week: 4,
              minutes_per_session: 105,
              best_days: ["Mon", "Wed", "Sat"],
              pace_label: "Steady",
              pace_description: "A balanced plan that keeps momentum high without overloading your week.",
            },
            projected_weeks_to_complete: 8,
            projected_completion_date: "After sign-in, this uses your roadmap activity.",
          }, container);
          return;
        }
        var res = await api("/intelligence/learning-pace");
        renderPace(res, container);
      } catch (_) {
        renderPace({
          recommendation: {
            hours_per_week: 5,
            minutes_per_session: 75,
            best_days: ["Mon", "Wed", "Fri"],
            pace_label: "Foundation",
            pace_description: "Connect your roadmap to calculate a personal pace from quiz scores and progress.",
          },
          quiz_stats: { total_quizzes: 0, average_score: 0, pass_rate: 0 },
          progress: { remaining: 0 },
          projected_weeks_to_complete: "Connect profile",
        }, container);
      }
    }
    load();
  }

  function renderPace(data, container) {
    var rec = data.recommendation || {};
    var quiz = data.quiz_stats || {};
    var prog = data.progress || {};
    var target = data.career_target || "Demo roadmap";
    var completion = data.projected_completion_date || "";

    container.innerHTML =
      '<div class="intel-kicker"><span>' + escapeHtml(target) + '</span><span>' + escapeHtml(String(completion)) + '</span></div>' +
      '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:20px">' +
        '<div style="text-align:center;padding:16px;background:var(--card);border-radius:12px;border:1px solid var(--border)">' +
          '<div style="font-size:2rem;font-weight:800;color:var(--primary)">' + (rec.hours_per_week || 0) + 'h</div>' +
          '<div style="font-size:0.8rem;color:var(--muted)">Hours / Week</div></div>' +
        '<div style="text-align:center;padding:16px;background:var(--card);border-radius:12px;border:1px solid var(--border)">' +
          '<div style="font-size:2rem;font-weight:800;color:var(--accent)">' + (rec.minutes_per_session || 0) + 'm</div>' +
          '<div style="font-size:0.8rem;color:var(--muted)">Per Session</div></div>' +
        '<div style="text-align:center;padding:16px;background:var(--card);border-radius:12px;border:1px solid var(--border)">' +
          '<div style="font-size:2rem;font-weight:800;color:var(--muted)">' + (quiz.average_score || 0) + '%</div>' +
          '<div style="font-size:0.8rem;color:var(--muted)">Avg Quiz Score</div></div>' +
        '<div style="text-align:center;padding:16px;background:var(--card);border-radius:12px;border:1px solid var(--border)">' +
          '<div style="font-size:2rem;font-weight:800;color:var(--accent)">' + (prog.remaining || 0) + '</div>' +
          '<div style="font-size:0.8rem;color:var(--muted)">Modules Left</div></div></div>' +
      '<div style="padding:16px;background:rgba(99,102,241,0.08);border-radius:12px;border:1px solid rgba(99,102,241,0.15);margin-bottom:16px">' +
        '<div style="font-weight:700;color:var(--primary);margin-bottom:4px">' + (rec.pace_label || "\u2014") + ' Pace</div>' +
        '<div style="font-size:0.9rem;color:var(--muted)">' + (rec.pace_description || "") + '</div></div>' +
      '<div style="display:flex;gap:12px;flex-wrap:wrap">' +
        '<div style="flex:1;min-width:180px;padding:14px;background:var(--card);border-radius:12px;border:1px solid var(--border)">' +
          '<div style="font-weight:600;margin-bottom:4px">Best Study Days</div>' +
          '<div style="font-size:0.9rem;color:var(--muted)">' + (rec.best_days || []).join(", ") + '</div></div>' +
        '<div style="flex:1;min-width:180px;padding:14px;background:var(--card);border-radius:12px;border:1px solid var(--border)">' +
          '<div style="font-weight:600;margin-bottom:4px">Quizzes Taken</div>' +
          '<div style="font-size:0.9rem;color:var(--muted)">' + (quiz.total_quizzes || 0) + ' (' + (quiz.pass_rate || 0) + '% pass)</div></div>' +
        '<div style="flex:1;min-width:180px;padding:14px;background:var(--card);border-radius:12px;border:1px solid var(--border)">' +
          '<div style="font-weight:600;margin-bottom:4px">Projected Completion</div>' +
          '<div style="font-size:0.9rem;color:var(--muted)">' + (data.projected_weeks_to_complete || "\u2014") + ' weeks</div></div></div>';
    container.style.display = "";
  }

  /* ============ SKILL MARKET INTELLIGENCE ============ */
  function initSkillMarket() {
    var container = $("#marketResult");
    if (!container) return;

    async function load() {
      try {
        if (!auth.token) {
          renderMarket({
            skills: DEMO_MARKET_SKILLS,
            portfolio_summary: {
              average_demand: 86.6,
              highest_potential_salary: 155000,
              hot_skills_count: 4,
              total_skills: DEMO_MARKET_SKILLS.length,
              portfolio_strength: "Strong demo",
            },
          }, container);
          return;
        }
        var res = await api("/intelligence/skill-market", { method: "POST", body: {} });
        renderMarket(res, container);
      } catch (_) {
        renderMarket({
          skills: DEMO_MARKET_SKILLS,
          portfolio_summary: {
            average_demand: 86.6,
            highest_potential_salary: 155000,
            hot_skills_count: 4,
            total_skills: DEMO_MARKET_SKILLS.length,
            portfolio_strength: "Strong demo",
          },
        }, container);
      }
    }
    load();
  }

  function renderMarket(data, container) {
    var skills = data.skills || [];
    var summary = data.portfolio_summary || {};
    var trendColors = { hot: "#EF4444", growing: "#22C55E", stable: "#F59E0B", unknown: "#6B7280" };
    var trendIcons = { hot: "\uD83D\uDD25", growing: "\uD83D\uDCC8", stable: "\u2696\uFE0F", unknown: "?" };
    var valueColors = { premium: "#A855F7", strong: "#6366F1", standard: "#3B82F6", fundamental: "#6B7280", unknown: "#6B7280" };

    // Convert USD to INR (approx 1 USD = 83 INR)
    function usdToINR(usd) {
      return Math.round(usd * 83);
    }

    function formatINR(amount) {
      if (amount >= 1000000) {
        return "₹" + (amount / 100000).toFixed(1) + "L";
      } else if (amount >= 1000) {
        return "₹" + (amount / 1000).toFixed(1) + "K";
      }
      return "₹" + amount;
    }

    var html =
      '<div class="market-summary-card">' +
        '<div class="market-summary-title">Portfolio: ' + (summary.portfolio_strength || "\u2014") + '</div>' +
        '<div class="market-summary-stats">Avg demand: ' + (summary.average_demand || 0) + '/100 &middot; ' +
        'Hot skills: ' + (summary.hot_skills_count || 0) + ' &middot; ' +
        'Top salary: ' + formatINR(usdToINR(summary.highest_potential_salary || 0)) + '</div>' +
      '</div>';

    html += '<div class="market-table-container"><table class="market-table">' +
      '<thead><tr>' +
      '<th class="market-th">Skill</th><th class="market-th">Demand</th><th class="market-th">Trend</th>' +
      '<th class="market-th">Avg Salary (INR)</th><th class="market-th">Value</th><th class="market-th">Roles</th>' +
      '</tr></thead><tbody>';

    skills.forEach(function(s) {
      var demand = clamp(Number(s.demand) || 0, 0, 100);
      var range = s.salary_range || [0, 0];
      var filled = Math.round(demand / 10);
      var bar = "\u2588".repeat(filled) + "\u2591".repeat(10 - filled);
      var salaryINR = range[1] > 0 
        ? formatINR(usdToINR(range[0])) + " - " + formatINR(usdToINR(range[1])) 
        : "Portfolio skill";
      var roles = (s.related_roles || []).slice(0, 2).join(", ") || "Broad use";
      var demandColor = demand >= 80 ? "#22C55E" : demand >= 60 ? "#F59E0B" : "#EF4444";

      html += '<tr class="market-row">' +
        '<td class="market-td skill-cell">' + escapeHtml(s.skill) + '</td>' +
        '<td class="market-td"><span class="demand-bar" style="color:' + demandColor + '">' + bar + '</span> <span class="demand-value">' + demand + '</span></td>' +
        '<td class="market-td"><span class="trend-badge" style="background:' + (trendColors[s.trend] || '#6B7280') + '20;color:' + (trendColors[s.trend] || '#6B7280') + '">' + (trendIcons[s.trend] || '') + ' ' + escapeHtml(s.trend || "unknown") + '</span></td>' +
        '<td class="market-td salary-cell">' + salaryINR + '</td>' +
        '<td class="market-td"><span class="value-badge" style="background:' + (valueColors[s.market_value] || '#6B7280') + '20;color:' + (valueColors[s.market_value] || '#6B7280') + ';font-weight:600;text-transform:uppercase;font-size:0.75rem">' + escapeHtml(s.market_value || "unknown") + '</span></td>' +
        '<td class="market-td roles-cell">' + escapeHtml(roles) + '</td></tr>';
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;
    container.style.display = "";
  }

})();
