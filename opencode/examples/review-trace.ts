import type { Plugin } from "@opencode-ai/plugin";

// Original teaching example for the v1.19.5 V1 hook interface.
// This is an observer, not a permissions boundary or durable audit log.
const REVIEW_NOTE = "Review correctness first. Cite files and explain unresolved assumptions.";
const MAX_PENDING = 128;

export const ReviewTrace: Plugin = async ({ client }) => {
  const pending = new Map<string, number>();
  let disposed = false;
  const key = (session: string, call: string) => JSON.stringify([session, call]);

  return {
    "experimental.chat.system.transform": async (_input, output) => {
      if (!disposed && !output.system.includes(REVIEW_NOTE)) {
        output.system.push(REVIEW_NOTE);
      }
    },
    "tool.execute.before": async (input, _output) => {
      if (disposed) return;
      const id = key(input.sessionID, input.callID);
      if (!pending.has(id) && pending.size >= MAX_PENDING) {
        pending.delete(pending.keys().next().value!);
      }
      pending.set(id, performance.now());
    },
    "tool.execute.after": async (input, output) => {
      if (disposed) return;
      const id = key(input.sessionID, input.callID);
      const started = pending.get(id);
      pending.delete(id);
      const trace = {
        correlated: started !== undefined,
        durationMs: started === undefined ? null : Math.max(0, performance.now() - started),
      };
      // The pinned subtask failure path can call this hook with undefined,
      // despite the published type describing a result object.
      if (output) output.metadata = { ...output.metadata, reviewTrace: trace };
      try {
        await client.app.log({
          body: {
            service: "book-review-trace",
            level: output ? "info" : "warn",
            message: output ? "Tool result observed" : "Tool callback has no result",
            extra: { tool: input.tool, sessionID: input.sessionID, callID: input.callID, ...trace },
          },
        });
      } catch {
        // Telemetry failure must not turn a completed tool into a failed tool.
        // SDK responses containing an error are also best-effort and ignored.
      }
    },
    dispose: async () => {
      disposed = true;
      pending.clear();
    },
  };
};
