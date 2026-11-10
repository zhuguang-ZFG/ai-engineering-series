/** Book-owned review services running on real Cordis, not dsh-tools or an Agent. */
export function createReviewLab({ Service }) {
  class ReviewJournal extends Service {
    entries = [];
    constructor(ctx) { super(ctx, "bookJournal"); }
    append(kind, data = {}) {
      const event = Object.freeze({ seq: this.entries.length, kind,
        data: Object.freeze(structuredClone(data)) });
      this.entries.push(event);
      return event;
    }
    snapshot() { return structuredClone(this.entries); }
  }

  class ReviewTools extends Service {
    definitions = new Map();
    nextId = 0;
    constructor(ctx) { super(ctx, "bookTools"); }
    register(name, execute) {
      if (this.definitions.has(name)) throw new Error(`DUPLICATE_TOOL:${name}`);
      const entry = { execute };
      this.definitions.set(name, entry);
      return () => {
        if (this.definitions.get(name) === entry) this.definitions.delete(name);
      };
    }
    async call(name, args) {
      const entry = this.definitions.get(name);
      if (!entry) throw new Error(`TOOL_NOT_FOUND:${name}`);
      const request = Object.freeze({ id: ++this.nextId, name,
        args: Object.freeze(structuredClone(args)) });
      return this.ctx.waterfall("book/execute", request, () => entry.execute(request));
    }
  }

  function reviewPlugin({ checkpoint = async () => {}, close = async () => {},
                           failAfterRegister = false } = {}) {
    return Object.assign(function reviewText(ctx) {
      const journal = ctx.bookJournal;
      const tools = ctx.bookTools;
      const active = new Map();
      let accepting = true;
      journal.append("plugin:load");
      ctx.effect(() => {
        const remove = tools.register("review_text", request => {
          if (!accepting) throw new Error("PLUGIN_UNLOADED");
          if (typeof request.args.text !== "string") throw new TypeError("TEXT_REQUIRED");
          const controller = new AbortController();
          const task = (async () => {
            journal.append("tool:start", { id: request.id });
            try {
              await checkpoint({ signal: controller.signal, request });
              controller.signal.throwIfAborted();
              const text = request.args.text;
              const result = Object.freeze({ lines: text === "" ? 0 : text.split("\n").length,
                characters: [...text].length, todo: text.includes("TODO") });
              journal.append("tool:result", { id: request.id, ...result });
              return result;
            } catch (error) {
              journal.append("tool:error", { id: request.id, message: String(error.message) });
              throw error;
            } finally {
              await close(request.id);
              active.delete(request.id);
              journal.append("tool:settled", { id: request.id });
            }
          })();
          active.set(request.id, { controller, task });
          return task;
        });
        return async () => {
          accepting = false;
          remove();
          const pending = [...active.values()];
          journal.append("plugin:stop", { active: pending.length });
          for (const item of pending) item.controller.abort(new Error("PLUGIN_UNLOADED"));
          await Promise.allSettled(pending.map(item => item.task));
          journal.append("plugin:closed");
        };
      });
      ctx.on("book/note", text => journal.append("note", { text }));
      if (failAfterRegister) throw new Error("FAIL_AFTER_REGISTER");
    }, { inject: ["bookJournal", "bookTools"] });
  }

  function policy({ reject = () => false, record = () => {} } = {}) {
    return function reviewPolicy(ctx) {
      ctx.on("book/execute", async (request, next) => {
        record(`policy:before:${request.id}`);
        if (reject(request)) throw new Error("POLICY_DENIED");
        try { return await next(); }
        finally { record(`policy:after:${request.id}`); }
      });
    };
  }
  return { ReviewJournal, ReviewTools, reviewPlugin, policy };
}

/** A controllable wait: cancellation rejects it, with no timers or network. */
export function waitForAbort(signal) {
  if (signal.aborted) return Promise.reject(signal.reason);
  return new Promise((resolve, reject) => {
    signal.addEventListener("abort", () => reject(signal.reason), { once: true });
  });
}

export function deferred() {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return { promise, resolve };
}
