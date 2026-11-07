/* Optional local reading aids. The lesson, contents and image links work without JS. */
(() => {
  "use strict";
  const article = document.querySelector("article.lesson");
  const tools = document.querySelector(".reader-tools");
  const sizeControl = document.getElementById("reader-size");
  if (!article || !tools || !sizeControl) return;

  const SIZE_KEY = "llm-reading-size-v1";
  const POSITION_KEY = "llm-reading-position-v1";
  const sizes = new Set([18, 20, 22]);
  const version = document.body.dataset.readingVersion || "";
  const lessonTitle = document.body.dataset.readingTitle || article.querySelector("h1")?.textContent.trim() || "";
  const slug = location.pathname.split("/").pop();
  const knownPages = new Set([...document.querySelectorAll(".course-menu a[href]")].flatMap(anchor => {
    const url = new URL(anchor.href);
    const local = new URL(".", location.href);
    return url.origin === local.origin && new URL(".", url).href === local.href && /^[a-z][a-z-]*\.html$/.test(url.pathname.split("/").pop())
      ? [url.pathname.split("/").pop()] : [];
  }));
  const headings = [...article.querySelectorAll(".article-body h2[id], .article-body h3[id]")]
    .filter(heading => !heading.closest("noscript, [data-experiment]"));
  const sectionMenu = document.querySelector("details.section-menu");
  const sidebar = document.querySelector(".sidebar");
  const contents = document.querySelector(".lesson-toc");
  const mobile = matchMedia("(max-width: 960px)");
  if (sectionMenu && matchMedia("(min-width: 961px)").matches) sectionMenu.open = true;
  let engaged = false;
  let scheduled = false;
  let lastSaved = "";
  let currentSection = "";
  let contentsDialog;
  let contentsTrigger;
  let contentsScroll = 0;
  let contentsAnchor;
  let contentsAnchorTop = 0;
  let contentsViewport = "";
  let contentsNavigation = false;
  let dialog;
  let figureTrigger;

  const read = key => {
    try { return JSON.parse(localStorage.getItem(key)); } catch { return null; }
  };
  const write = (key, value) => {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* Reading still works in private/restricted storage. */ }
  };
  const visible = element => element.getClientRects().length > 0;
  const validText = value => typeof value === "string" && value.length > 0 && value.length <= 180 && !/[\u0000-\u001f<>]/.test(value);
  const validSection = value => typeof value === "string" && value.length <= 160 && !/[\s\u0000-\u001f<>"']/u.test(value);

  function openAncestors(element) {
    for (let parent = element.parentElement; parent; parent = parent.parentElement) {
      if (parent.tagName === "DETAILS") parent.open = true;
    }
  }
  function followHash() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = id && document.getElementById(id);
    if (!target || !article.contains(target)) return;
    openAncestors(target);
    if (!target.hasAttribute("tabindex")) target.tabIndex = -1;
    requestAnimationFrame(() => {
      target.focus({ preventScroll: true });
      target.scrollIntoView({ block: "start", behavior: "instant" });
      queueUpdate();
    });
  }

  function currentHeading() {
    const passed = headings.filter(heading => visible(heading) && heading.getBoundingClientRect().top <= Math.min(innerHeight * .25, 180));
    return passed[passed.length - 1];
  }

  function markSection(force = false) {
    const section = currentHeading()?.id || "";
    if (!force && section === currentSection) return;
    currentSection = section;
    for (const link of document.querySelectorAll(".lesson-toc a, .reader-toc-links a")) {
      let id;
      try { id = decodeURIComponent(new URL(link.href).hash.slice(1)); } catch { continue; }
      if (id === section) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    }
  }

  function updateContentsTrigger() {
    if (!contentsTrigger || !sidebar) return;
    const shouldShow = mobile.matches && sidebar.getBoundingClientRect().bottom < 0;
    if (document.querySelector("dialog[open]")) { contentsTrigger.hidden = true; return; }
    // A keyboard user must be able to finish activating the shortcut even if
    // scrolling brings a control behind it. Reconsider placement on blur.
    if (document.activeElement === contentsTrigger && mobile.matches) return;
    if (!shouldShow) { contentsTrigger.hidden = true; return; }
    contentsTrigger.hidden = false;
    contentsTrigger.classList.remove("reader-toc-left");
    // Keep the shortcut out of the way of controls near the screen's bottom.
    const controls = [...article.querySelectorAll(".lab button, .lab input, .lab select, .lab textarea, .quiz button, .quiz input, a.figure-open")].filter(visible);
    const overlaps = () => {
      const rect = contentsTrigger.getBoundingClientRect();
      return controls.some(control => {
        const box = control.getBoundingClientRect();
        return box.right > rect.left - 8 && box.left < rect.right + 8 && box.bottom > rect.top - 8 && box.top < rect.bottom + 8;
      });
    };
    if (overlaps()) contentsTrigger.classList.add("reader-toc-left");
    if (overlaps()) contentsTrigger.hidden = true;
  }

  function showContents() {
    if (!contents || dialog?.open || !mobile.matches) return;
    if (!contentsDialog) {
      contentsDialog = document.createElement("dialog");
      contentsDialog.className = "reader-toc-dialog";
      contentsDialog.id = "reader-toc-dialog";
      contentsDialog.setAttribute("aria-labelledby", "reader-toc-title");
      contentsDialog.innerHTML = '<div class="reader-toc-header"><h2 id="reader-toc-title">本课目录</h2><button id="reader-toc-close" type="button" autofocus>返回正文</button></div><nav class="reader-toc-links" aria-label="本课小节"></nav>';
      const navigation = contentsDialog.querySelector("nav");
      const listing = contents.querySelector("ol, ul");
      if (listing) navigation.append(listing.cloneNode(true));
      else for (const link of contents.querySelectorAll("a")) navigation.append(link.cloneNode(true));
      for (const element of navigation.querySelectorAll("[id]")) element.removeAttribute("id");
      document.body.append(contentsDialog);
      contentsDialog.querySelector("#reader-toc-close").addEventListener("click", () => contentsDialog.close());
      contentsDialog.addEventListener("close", () => {
        contentsTrigger.setAttribute("aria-expanded", "false");
        if (!dialog?.open) document.documentElement.classList.remove("reader-modal-open");
        if (!contentsNavigation) {
          const resized = contentsViewport !== `${innerWidth}:${innerHeight}`;
          const top = resized && contentsAnchor
            ? scrollY + contentsAnchor.getBoundingClientRect().top - Math.min(contentsAnchorTop, innerHeight * .25)
            : contentsScroll;
          window.scrollTo({ top, behavior: "instant" });
          const returnToShortcut = mobile.matches && sidebar.getBoundingClientRect().bottom < 0;
          const target = returnToShortcut ? contentsTrigger : contentsAnchor || article.querySelector("h1");
          if (returnToShortcut) contentsTrigger.hidden = false;
          if (target) {
            if (!target.hasAttribute("tabindex") && target !== contentsTrigger) target.tabIndex = -1;
            target.focus({ preventScroll: true });
          }
          updateContentsTrigger();
        }
        queueUpdate();
      });
    }
    contentsNavigation = false;
    contentsScroll = scrollY;
    contentsAnchor = currentHeading();
    contentsAnchorTop = contentsAnchor?.getBoundingClientRect().top || 0;
    contentsViewport = `${innerWidth}:${innerHeight}`;
    markSection(true);
    contentsTrigger.setAttribute("aria-expanded", "true");
    document.documentElement.classList.add("reader-modal-open");
    contentsDialog.showModal();
    const current = contentsDialog.querySelector('[aria-current="location"]');
    const navigation = contentsDialog.querySelector("nav");
    if (current) {
      navigation.scrollTop += current.getBoundingClientRect().top - navigation.getBoundingClientRect().top - navigation.clientHeight / 3;
      current.focus({ preventScroll: true });
    } else contentsDialog.querySelector("#reader-toc-close").focus();
    updateContentsTrigger();
  }

  if (contents && sidebar && typeof HTMLDialogElement !== "undefined") {
    contentsTrigger = document.createElement("button");
    contentsTrigger.type = "button";
    contentsTrigger.id = "reader-toc-trigger";
    contentsTrigger.className = "reader-toc-trigger";
    contentsTrigger.textContent = "本课目录";
    contentsTrigger.hidden = true;
    contentsTrigger.setAttribute("aria-haspopup", "dialog");
    contentsTrigger.setAttribute("aria-expanded", "false");
    document.body.append(contentsTrigger);
    document.body.classList.add("reader-has-shortcut");
    contentsTrigger.addEventListener("click", showContents);
    contentsTrigger.addEventListener("blur", queueUpdate);
  }

  function applySize(size, preservePosition = false) {
    if (!sizes.has(size)) return;
    const anchor = preservePosition && [...article.querySelectorAll(".article-body > p, .article-body > h2, .article-body > h3, .article-body > figure")]
      .find(element => visible(element) && element.getBoundingClientRect().bottom > 100);
    const previousTop = anchor && anchor.getBoundingClientRect().top;
    document.documentElement.style.setProperty("--reading-size", `${size}px`);
    sizeControl.value = String(size);
    if (anchor) requestAnimationFrame(() => window.scrollBy({ top: anchor.getBoundingClientRect().top - previousTop, behavior: "instant" }));
  }
  applySize(read(SIZE_KEY) || 18);
  sizeControl.addEventListener("change", () => {
    const size = Number(sizeControl.value);
    applySize(size, true);
    if (sizes.has(size)) write(SIZE_KEY, size);
  });
  tools.hidden = false;

  const resume = document.getElementById("reader-resume");
  const saved = read(POSITION_KEY);
  if (resume && saved && saved.version === version && knownPages.has(saved.slug)
      && validSection(saved.section) && validText(saved.lessonTitle)
      && (saved.section === "" || validText(saved.sectionTitle))
      && (saved.slug !== slug || !saved.section || headings.some(heading => heading.id === saved.section))) {
    resume.href = saved.slug + (saved.section ? `#${encodeURIComponent(saved.section)}` : "");
    resume.textContent = `继续上次：${saved.sectionTitle || saved.lessonTitle}`;
    resume.hidden = false;
  }

  function savePosition() {
    if (!engaged || !knownPages.has(slug) || !version) return;
    const current = currentHeading();
    const position = { version, slug, section: current?.id || "", sectionTitle: current?.textContent.trim().slice(0, 180) || "", lessonTitle: lessonTitle.slice(0, 180) };
    const fingerprint = JSON.stringify(position);
    if (fingerprint !== lastSaved) { write(POSITION_KEY, position); lastSaved = fingerprint; }
  }
  function queueUpdate() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => { scheduled = false; markSection(); updateContentsTrigger(); savePosition(); });
  }
  window.addEventListener("wheel", () => { engaged = true; }, { passive: true });
  window.addEventListener("touchmove", () => { engaged = true; }, { passive: true });
  document.addEventListener("keydown", event => {
    if (["PageDown", "PageUp", "Home", "End", "ArrowDown", "ArrowUp", " "].includes(event.key)
        && !event.target.closest("input, textarea, select, button, dialog")) engaged = true;
  });
  window.addEventListener("scroll", queueUpdate, { passive: true });
  window.addEventListener("resize", queueUpdate, { passive: true });
  window.addEventListener("pagehide", savePosition);
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") savePosition(); });
  window.addEventListener("hashchange", followHash);

  document.addEventListener("click", event => {
    const link = event.target.closest(".lesson-toc a, .reader-toc-links a, .article-body a[href^='#'], #reader-resume");
    if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const url = new URL(link.href);
    if (url.pathname !== location.pathname || !url.hash) return;
    let id;
    try { id = decodeURIComponent(url.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (!target || !article.contains(target)) return;
    event.preventDefault();
    engaged = true;
    if (contentsDialog?.contains(link)) {
      contentsNavigation = true;
      contentsDialog.close();
    }
    const menu = link.closest("details");
    if (menu && !menu.contains(target) && !matchMedia("(min-width: 961px)").matches) menu.open = false;
    openAncestors(target);
    if (location.hash === url.hash) followHash();
    else location.hash = url.hash;
    queueUpdate();
  });
  if (location.hash) followHash();
  queueUpdate();

  function showFigure(link) {
    const original = link.closest("figure")?.querySelector("img");
    if (!original || new URL(link.href).href !== new URL(original.src).href || typeof HTMLDialogElement === "undefined") return false;
    if (contentsDialog?.open) return true;
    if (!dialog) {
      dialog = document.createElement("dialog");
      dialog.className = "reader-figure-dialog";
      dialog.setAttribute("aria-labelledby", "reader-figure-title");
      dialog.setAttribute("aria-describedby", "reader-figure-caption reader-figure-hint");
      dialog.innerHTML = '<div class="reader-figure-header"><h2 id="reader-figure-title">手绘细节</h2><div class="reader-figure-actions"><button id="reader-figure-zoom" type="button" aria-pressed="true">适合窗口</button><button id="reader-figure-close" type="button" autofocus>关闭大图</button></div></div><p class="reader-figure-caption" id="reader-figure-caption"></p><p class="reader-figure-hint" id="reader-figure-hint">可上下左右滑动查看；按 Esc 关闭</p><div class="reader-figure-canvas is-zoomed" tabindex="0" role="region" aria-label="手绘大图，可上下左右滚动"></div>';
      document.body.append(dialog);
      dialog.querySelector("#reader-figure-close").addEventListener("click", () => dialog.close());
      dialog.querySelector("#reader-figure-zoom").addEventListener("click", event => {
        const zoomed = dialog.querySelector(".reader-figure-canvas").classList.toggle("is-zoomed");
        event.currentTarget.setAttribute("aria-pressed", String(zoomed));
        event.currentTarget.textContent = zoomed ? "适合窗口" : "放大细看";
      });
      dialog.addEventListener("close", () => {
        if (!contentsDialog?.open) document.documentElement.classList.remove("reader-modal-open");
        figureTrigger?.focus({ preventScroll: true });
        queueUpdate();
      });
    }
    const canvas = dialog.querySelector(".reader-figure-canvas");
    const image = new Image();
    image.src = original.src;
    image.alt = original.alt;
    image.className = "reader-figure-image";
    image.style.setProperty("--reader-image-width", `${(Number(original.getAttribute("width")) || 480) * 1.5}px`);
    canvas.replaceChildren(image);
    const caption = link.closest("figure").querySelector("figcaption")?.cloneNode(true);
    if (caption) for (const control of caption.querySelectorAll(".figure-open")) control.remove();
    dialog.querySelector("#reader-figure-caption").textContent = caption?.textContent.trim() || original.alt;
    canvas.classList.add("is-zoomed");
    const zoom = dialog.querySelector("#reader-figure-zoom");
    zoom.setAttribute("aria-pressed", "true");
    zoom.textContent = "适合窗口";
    figureTrigger = link;
    document.documentElement.classList.add("reader-modal-open");
    dialog.showModal();
    updateContentsTrigger();
    canvas.scrollTo(0, 0);
    dialog.querySelector("#reader-figure-close").focus();
    return true;
  }
  document.addEventListener("click", event => {
    const link = event.target.closest("a.figure-open");
    if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (showFigure(link)) event.preventDefault();
  });
})();
