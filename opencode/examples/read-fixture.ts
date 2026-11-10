import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { tool, type Plugin } from "@opencode-ai/plugin";

/** A deliberately narrow tool: it only reads fixture.txt in this project. */
export const ReadFixture: Plugin = async () => ({
  tool: {
    book_probe: tool({
      description: "Read fixture.txt in the current project after checking book_read permission.",
      args: {},
      async execute(_args, context) {
        await context.ask({
          permission: "book_read",
          patterns: ["fixture.txt"],
          always: ["fixture.txt"],
          metadata: {},
        });
        if (context.abort.aborted) throw new Error("Fixture read was cancelled");
        const output = await readFile(join(context.directory, "fixture.txt"), {
          encoding: "utf8",
          signal: context.abort,
        });
        return { title: "Project fixture", output, metadata: { source: "fixture.txt" } };
      },
    }),
  },
});
