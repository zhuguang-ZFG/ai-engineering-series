/* A finite, opt-in tour of precomputed teaching diagrams. The static story is
   the source of truth and remains readable when JavaScript is unavailable. */
(function () {
  "use strict";

  const preference = matchMedia("(prefers-reduced-motion: reduce)");
  const interval = 5200;

  document.querySelectorAll("[data-mechanism]").forEach((section) => {
    const controls = section.querySelector(".mechanism-controls");
    const stage = section.querySelector(".mechanism-stage");
    const complete = section.querySelector(".mechanism-static");
    const status = section.querySelector(".mechanism-status");
    const frames = [...section.querySelectorAll(".mechanism-frame")];
    const buttons = Object.fromEntries(["previous", "next", "play", "reset", "all"].map((action) => [action, controls?.querySelector(`[data-action="${action}"]`)]));
    if (!controls || !stage || !complete || !status || !frames.length || Object.values(buttons).some((button) => !button)) return;

    let current = 0;
    let playing = false;
    let showingAll = false;
    let timer = null;
    let announcement = null;
    const prefix = `mechanism-${section.dataset.mechanism}`;
    stage.id ||= `${prefix}-stage`;
    complete.id ||= `${prefix}-complete`;
    status.id ||= `${prefix}-status`;
    controls.setAttribute("role", "group");
    controls.setAttribute("aria-label", "分步看手绘");
    for (const button of Object.values(buttons)) button.setAttribute("aria-controls", `${stage.id} ${complete.id}`);

    function cancelAnnouncement() {
      if (announcement !== null) cancelAnimationFrame(announcement);
      announcement = null;
    }

    function say(message, delayed = false) {
      cancelAnnouncement();
      status.setAttribute("aria-live", playing ? "off" : "polite");
      const write = () => {
        status.textContent = message;
        announcement = null;
      };
      if (delayed) announcement = requestAnimationFrame(write);
      else write();
    }

    function description() {
      return `第 ${current + 1} / ${frames.length} 步：${frames[current].dataset.title}。`;
    }

    function refresh() {
      section.dataset.step = String(current);
      section.dataset.playing = String(playing);
      section.dataset.mode = showingAll ? "all" : "step";
      frames.forEach((frame, index) => {
        frame.hidden = index !== current;
        if (index === current) frame.setAttribute("aria-current", "step");
        else frame.removeAttribute("aria-current");
      });
      stage.hidden = showingAll;
      complete.hidden = !showingAll;
      buttons.previous.setAttribute("aria-disabled", String(showingAll || current === 0));
      buttons.next.setAttribute("aria-disabled", String(showingAll || current === frames.length - 1));
      buttons.play.setAttribute("aria-disabled", String(showingAll || preference.matches));
      buttons.play.setAttribute("aria-pressed", String(playing));
      buttons.play.textContent = preference.matches ? "自动播放已关闭" : playing ? "暂停" : current === frames.length - 1 ? "重播一遍" : "播放一遍";
      buttons.play.title = preference.matches ? "已遵循系统的减少动态设置，请使用上一步、下一步" : "每步停留约五秒；随时可以暂停";
      buttons.all.setAttribute("aria-expanded", String(showingAll));
      buttons.all.textContent = showingAll ? "回到分步" : "看完整分镜";
    }

    function stop(message, announce = true) {
      const wasPlaying = playing;
      playing = false;
      if (timer !== null) clearTimeout(timer);
      timer = null;
      refresh();
      if (announce && message) say(message, wasPlaying);
      else if (!announce) {
        cancelAnnouncement();
        status.setAttribute("aria-live", "polite");
      }
    }

    function advance() {
      if (!playing) return;
      if (preference.matches || document.hidden) {
        stop(`已暂停。${description()}`);
        return;
      }
      current += 1;
      refresh();
      if (current === frames.length - 1) {
        stop(`这一遍已结束。${description()}可以回看任意一步。`);
      } else {
        say(description());
        timer = setTimeout(advance, interval);
      }
    }

    buttons.previous.addEventListener("click", () => {
      if (showingAll || current === 0) return;
      stop(null, false);
      current -= 1;
      refresh();
      say(description());
    });
    buttons.next.addEventListener("click", () => {
      if (showingAll || current === frames.length - 1) return;
      stop(null, false);
      current += 1;
      refresh();
      say(description());
    });
    buttons.reset.addEventListener("click", () => {
      stop(null, false);
      current = 0;
      showingAll = false;
      refresh();
      say(`回到开头。${description()}`);
    });
    buttons.all.addEventListener("click", () => {
      stop(null, false);
      showingAll = !showingAll;
      refresh();
      say(showingAll ? "完整分镜已展开，可以按顺序阅读所有步骤。" : description());
    });
    buttons.play.addEventListener("click", () => {
      if (showingAll || preference.matches) return;
      if (playing) {
        stop(`已暂停。${description()}`);
        return;
      }
      if (current === frames.length - 1) current = 0;
      playing = true;
      refresh();
      say(description());
      timer = setTimeout(advance, interval);
    });
    preference.addEventListener("change", () => {
      if (preference.matches) stop(`已遵循减少动态设置。${description()}用上一步、下一步继续看。`);
      else {
        refresh();
        say(description());
      }
    });
    document.addEventListener("visibilitychange", () => {
      if (document.hidden && playing) stop(`已暂停。${description()}`);
    });
    window.addEventListener("pagehide", () => stop(null, false));
    if ("IntersectionObserver" in window) {
      new IntersectionObserver((entries) => {
        if (playing && entries.some((entry) => !entry.isIntersecting)) stop(`已暂停。${description()}`);
      }, { threshold: 0 }).observe(section);
    }

    refresh();
    say(`${description()}${preference.matches ? "已遵循减少动态设置，用上一步、下一步观看。" : "可以逐步看，也可以播放一遍。"}`);
    controls.hidden = false;
    section.dataset.enhanced = "true";
  });
})();
