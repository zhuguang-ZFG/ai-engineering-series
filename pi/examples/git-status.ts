import { Type } from "typebox";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
    pi.registerTool({
        name: "book_git_status",
        label: "Git status",
        description: "Read the current repository status without changing files",
        parameters: Type.Object({}),
        async execute(_id, _params, signal, onUpdate, ctx) {
            signal?.throwIfAborted();
            onUpdate?.({
                content: [{ type: "text", text: "正在读取 Git 状态……" }],
                details: {},
            });
            const result = await pi.exec("git", [
                "--no-optional-locks", "-C", ctx.cwd,
                "status", "--short", "--untracked-files=no",
            ], { signal, timeout: 10000 });
            signal?.throwIfAborted();
            if (result.killed || result.code !== 0) {
                throw new Error(result.killed
                    ? "Git 状态读取超时或被中止"
                    : `Git 状态读取失败，退出码 ${result.code}`);
            }
            const output = result.stdout.trimEnd();
            const limit = 6000;
            return {
                content: [{ type: "text", text: output.length > limit
                    ? output.slice(0, limit) + "\n[输出已截断]"
                    : output || "没有已跟踪文件的改动（未列出未跟踪文件）" }],
                details: { truncated: output.length > limit },
            };
        },
    });
}
