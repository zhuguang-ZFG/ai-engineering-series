# Chapter 8: The Hook System -- Agent's Lifecycle Extension Points

> **In one line:** The permission pipeline is the guardrail; hooks are the reflex arc -- at 22 lifecycle points they can watch, rewrite, or flatly refuse.

> **Learning Objectives:** By the end of this chapter, you can:
>
> - Tell what each of the five hook types can intercept, and where each one stops
> - Say when each of the 22 lifecycle events fires, what it receives, and what its exit code means
> - Write structured hook responses that steer behavior through `decision`, `updatedInput` and `additionalContext`
> - Recall the three gates: global disable, managed hooks only, workspace trust
> - Reason out which hook runs first when several match, and how conflicts settle
> - Configure hooks without stepping into the usual traps
> - See how hooks hand off to the permission pipeline (Chapter 4) and the configuration system (Chapter 5)

**Difficulty:** 8.1's five hook types are the starting rung; 8.2's 22 events are backbone material to read like a manual -- no need to memorize them in one sitting; 8.3's response protocol is backbone material you must read. 8.4's security gates sit at the Advanced tier but repay a close read; 8.5 closes the backbone -- save the anti-patterns for the day you write your first hook.

---

<!-- block: ch08.b-78bc89ed -->
You wrote a PreToolUse hook to intercept `rm -rf`. The hook ran, but you gave it exit code 1 -- a line in the warning log, and the command executed anyway. You blamed the hook's configuration; really you had not internalized what the exit codes mean. Across 22 lifecycle points, what each one can and cannot intercept lives in a single unified response protocol.

Hooks are the Agent's reflex arc: the permission pipeline decides whether an operation *can* run, while hooks decide what happens *before and after* it runs. From session startup to tool invocation, from user input to context compression, every critical node can observe, rewrite, or flatly refuse.

> **What you can do after this chapter:**
> - Say what each of the five hook types can and cannot intercept, and pick the right one for the job
> - Write structured responses with `decision`, `updatedInput`, and `additionalContext` so exit code and JSON never contradict each other
> - Reason out which hook runs first when several match, how conflicts settle, and how to avoid the three security gates

> **Cross-reference:** How another harness wires the same hooks -- see omp volume, Chapter 21, "Custom Tools and Hooks".

<!-- block: ch08.b-c8738fc4 -->
From an engineering perspective, the hook system combines the **Observer Pattern** with the **Chain of Responsibility Pattern**. Each lifecycle event publishes a signal, and matching hooks form a priority-ordered processing chain; the event and hook kind determine whether a handler may only observe, may rewrite data, or may block. The core engine depends on the shared response protocol rather than any extension's implementation, keeping user-defined behavior decoupled from the execution core.

## 8.1 Hook Types and Execution Model

<!-- block: ch08.b-2c8d52ba -->
Hooks are user-customizable extension points in Claude Code's lifecycle. Through hooks, users can inject custom logic at critical nodes without modifying Claude Code source code -- from approving tool calls, modifying tool inputs, to intercepting user requests, injecting additional context.

```mermaid
flowchart TD
    event["Lifecycle event trigger"] --> collect["Collect all matching hooks"]
    collect --> security["Security gate check"]
    security -->|"Not passed"| reject["Skip hook execution"]
    security -->|"Passed"| sort["Sort by priority<br/>userSettings > projectSettings<br/>> localSettings > plugin"]
    sort --> execute["Execute hooks in order"]
    execute --> check{"Hook returns<br/>decision: block?"}
    check -->|"Yes"| blocked["Operation blocked"]
    check -->|"No"| next{"More hooks?"}
    next -->|"Yes"| execute
    next -->|"No"| done["Continue normal flow"]

    classDef event fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px,color:#1a237e
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef decision fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#e65100
    classDef blocked_node fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px,color:#b71c1c
    classDef success fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#1b5e20

    class event event
    class collect,security,sort,execute process
    class check,next decision
    class reject,blocked blocked_node
    class done success
```

### Five Hook Types

<!-- block: ch08.b-224a19b7 -->
The hook Schema definition module defines four persistable hook types, plus FunctionHook which only exists at runtime, making five total. This comparison table helps you quickly understand each hook type's positioning and capability boundaries:

```mermaid
graph TD
    subgraph FiveHookTypes["Five Hook Types Capability Map"]
        cmd["Command Hook<br/>──────────<br/>Engine: Shell<br/>Persistable: Yes<br/>Config Format: JSON<br/>Complexity: Low<br/>Latency: Milliseconds<br/>Typical Scenario: Script checks"]
        prompt["Prompt Hook<br/>──────────<br/>Engine: LLM inference<br/>Persistable: Yes<br/>Config Format: JSON<br/>Complexity: Medium<br/>Latency: Seconds<br/>Typical Scenario: Content moderation"]
        agent["Agent Hook<br/>──────────<br/>Engine: LLM multi-step<br/>Persistable: Yes<br/>Config Format: JSON<br/>Complexity: High<br/>Latency: Seconds to Minutes<br/>Typical Scenario: Test verification"]
        http["HTTP Hook<br/>──────────<br/>Engine: HTTP request<br/>Persistable: Yes<br/>Config Format: JSON<br/>Complexity: Medium<br/>Latency: Network-dependent<br/>Typical Scenario: CI integration"]
        func["Function Hook<br/>──────────<br/>Engine: TS callback<br/>Persistable: No<br/>Config Format: TypeScript API<br/>Complexity: Low<br/>Latency: Milliseconds<br/>Typical Scenario: Runtime interception"]
    end

    classDef cmd fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef prompt fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef agent fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#e65100
    classDef http fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef func fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#880e4f

    class cmd cmd
    class prompt prompt
    class agent agent
    class http http
    class func func
```

**1. Command Hook** (`BashCommandHookSchema`)

The most common hook type, executes Shell commands. You can choose the Shell interpreter (bash/powershell), a custom timeout, a custom status message, and an `once` flag (automatically removed after one execution).

Applicable scenarios: Executing script checks, filesystem operations, calling external CLI tools, conditional approval or rejection of operations.

Configuration example:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "python3 scripts/validate_command.py",
        "timeout": 5000,
        "message": "Validating bash command safety..."
      }]
    }]
  }
}
```

**2. Prompt Hook** (`PromptHookSchema`)

Calls an LLM to evaluate the hook input, outputs a JSON response. You can specify the model (defaults to a fast small model) and use the `$ARGUMENTS` placeholder to reference the hook input.

Applicable scenarios: Approval flows requiring "intelligent judgment" rather than hardcoded rules. For example, determining whether a code modification is safe relies not on regex matching of keywords but on letting an LLM understand code semantics to make judgments.

Configuration example:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write",
      "hooks": [{
        "type": "prompt",
        "prompt": "Analyze this file write operation. If it modifies any file in src/core/, respond with {\"decision\": \"block\", \"reason\": \"Core module changes require code review\"}. Otherwise respond with {\"decision\": \"approve\"}. Input: $ARGUMENTS"
      }]
    }]
  }
}
```

**3. Agent Hook** (`AgentHookSchema`)

Agentic validator hook. Similar to Prompt hook but designed for validation scenarios requiring multi-step reasoning, such as verifying whether unit tests pass -- it may need to first run tests, read results, analyze coverage, before making a judgment.

Applicable scenarios: Complex approval flows requiring multi-step, iterable validation. For example, verifying all related tests still pass after code modifications.

**4. HTTP Hook** (`HttpHookSchema`)

POSTs the hook input JSON to a specified URL. You can set custom request headers and interpolate environment variables (controlled through the `allowedEnvVars` whitelist), which suits integration with external systems.

Applicable scenarios: Integration with CI/CD systems (like Jenkins, GitHub Actions), sending audit logs to SIEM systems, calling enterprise internal approval services.

Configuration example:

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "http",
        "url": "https://audit.example.com/api/log",
        "headers": {
          "Authorization": "Bearer $AUDIT_TOKEN",
          "Content-Type": "application/json"
        },
        "allowedEnvVars": ["AUDIT_TOKEN"]
      }]
    }]
  }
}
```

> **Anti-pattern warning:** When using `allowedEnvVars` in HTTP hooks, be sure to only expose necessary variables. Don't open the entire environment variable whitelist, as this could lead to credential leakage in multi-user environments.

**5. Function Hook**

In-memory hooks that only exist at runtime, executing TypeScript callback functions. You cannot persist them to configuration files, with a lifecycle bound to the session. Callbacks receive message arrays and an optional abort signal, returning a boolean indicating success.

Applicable scenarios: Scenarios requiring deep interaction with Claude Code runtime state, such as dynamic behavior control in SDK embedding mode.

<!-- block: ch08.b-9c89338a -->
> **Design reflection:** Why can't you persist Function hooks? Because TypeScript callback functions are in-memory executable code references that you cannot serialize to JSON configuration. This is the boundary between "code as configuration vs configuration as code" -- persistable hooks (Command/Prompt/Agent/HTTP) are fundamentally **declarative configuration**, while Function hooks are **imperative code**. Mixing both in the same configuration system would lead to unpredictable behavior and security risks.

### Sync vs Async Hooks

Command hooks have three execution modes:

- **Synchronous mode** (default): Blocks current operation, waits for hook completion before deciding whether to continue. This is the most common and safest mode, suitable for "approve before execute" scenarios.
- **Asynchronous mode** (`async: true`): Runs in background, doesn't block current operation. Hook results are not visible to the model. Suitable for "fire-and-forget" logging or notification scenarios.
- **Async-rewake mode** (`asyncRewake: true`): Runs in the background, but when the hook exits with code 2, it injects an error message to wake the model for continued conversation. This implies the `async` attribute. Suitable for long-running monitoring tasks -- normal operation doesn't disturb the Agent, and it only intervenes when it detects an anomaly.

```mermaid
flowchart TD
    subgraph sync_mode["Synchronous Mode (default)"]
        direction TB
        s1["Agent executes operation"] -->|"Pause wait"| s2["Hook executes"]
        s2 -->|"Based on result"| s3["Continue / Block"]
    end

    subgraph async_mode["Asynchronous Mode (async)"]
        direction TB
        a1["Agent executes operation"] -->|"No wait"| a2["Hook executes in background"]
        a1 --> a3["Normal flow continues"]
    end

    subgraph async_rewake["Async-rewake Mode (asyncRewake)"]
        direction TB
        ar1["Agent executes operation"] -->|"No wait"| ar2["Hook executes in background"]
        ar2 -->|"Exit code ≠ 2"| ar3["Normal operation"]
        ar2 -->|"Exit code = 2"| ar4["Wake model for continued conversation"]
    end

    classDef agent fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef hook fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#e65100
    classDef result fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef alert fill:#ffebee,stroke:#f44336,stroke-width:2px,color:#b71c1c

    class s1,a1,ar1 agent
    class s2,a2,ar2 hook
    class s3,a3,ar3 result
    class ar4 alert
```

Async hooks run inside the background execution functions. Async-rewake mode hooks bypass the regular registry, injecting messages through the notification queue when they finish. Async hook execution stays off the Agent's main loop, and the hook can still "sound the alarm" when it needs to.

---

<!-- block: ch08.b-239ed648 -->
## 8.2 Core Lifecycle Events

The SDK core types module defines the complete `HOOK_EVENTS` array; this chapter introduces 22 of its lifecycle events, covering the critical nodes of tool invocation, user interaction, session management, sub-agents, compression, permissions and configuration changes.

The best way to understand these events is to imagine an Agent's complete execution cycle as an "assembly line". Materials (user requests) enter from one end, pass through multiple stations (lifecycle events) for processing, and finally exit from the other end as finished products (Agent responses). Each station has "sensors" (events) installed, and hooks are the "control units" connected to these sensors.

```mermaid
flowchart TD
    subgraph SessionLayer["Session Layer"]
        SessionStart["SessionStart"] --> UserLoop["User Interaction Loop"]
        UserLoop --> SessionEnd["SessionEnd"]
    end

    subgraph UserInteractionLayer["User Interaction Layer"]
        UserPromptSubmit["UserPromptSubmit"] --> AgentProcess["Agent Processing"]
        AgentProcess --> Stop["Stop / StopFailure"]
    end

    subgraph ToolCallLayer["Tool Call Layer"]
        PreToolUse["PreToolUse"] --> ToolExec["Tool Execution"]
        ToolExec --> PostToolUse["PostToolUse / PostToolUseFailure"]
    end

    subgraph SubAgentLayer["Sub-agent Layer"]
        SubagentStart["SubagentStart"] --> SubagentExec["Sub-agent Execution"]
        SubagentExec --> SubagentStop["SubagentStop"]
    end

    subgraph CompressionLayer["Compression Layer"]
        PreCompact["PreCompact"] --> CompactExec["Compression Execution"]
        CompactExec --> PostCompact["PostCompact"]
    end

    subgraph OtherEvents["Other Events"]
        Other["PermissionRequest / PermissionDenied<br/>ConfigChange / CwdChanged / FileChanged<br/>Notification / Setup / Elicitation / InstructionsLoaded"]
    end

    UserLoop --> UserPromptSubmit
    AgentProcess --> PreToolUse
    AgentProcess --> SubagentStart
    AgentProcess --> PreCompact

    classDef session fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px,color:#1a237e
    classDef user fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef tool fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#e65100
    classDef sub fill:#e8f5e9,stroke:#4caf50,stroke-width:2px,color:#1b5e20
    classDef compact fill:#fce4ec,stroke:#e91e63,stroke-width:2px,color:#880e4f
    classDef other fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px,color:#4a148c
    classDef process fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#616161

    class SessionStart,SessionEnd session
    class UserPromptSubmit,Stop user
    class PreToolUse,PostToolUse,PostToolUseFailure tool
    class SubagentStart,SubagentStop sub
    class PreCompact,PostCompact compact
    class Other other
    class ToolExec,AgentProcess,SubagentExec,CompactExec,UserLoop process
```

Below, we introduce the core events grouped by function, with a detailed explanation of the trigger timing, input structure, and usage scenarios for each event.

### Tool Call Lifecycle

Tool call lifecycle events are the most frequently used set of events in the hook system. They form a "sandwich" structure: PreToolUse intercepts before execution, PostToolUse handles after success, PostToolUseFailure catches after failure.

**PreToolUse** (Before tool execution)

The most important interception point. Input is the tool call's parameter JSON. Hooks can block tool execution by returning `decision: "block"`, or modify the tool's actual input parameters through `updatedInput`. Exit code semantics:

<!-- block: ch08.b-33c3f760 -->
- Exit code 0: stdout/stderr not shown to model (silent pass)
- Exit code 2: Show stderr to model and block tool call (active block)
- Other exit codes: Show stderr to user but don't block (warning mode)

> **Cross-reference with Chapter 4:** PreToolUse hooks occur after the permission pipeline. The permission pipeline determines "whether to allow the tool to execute", while PreToolUse hooks determine "given allowed execution, whether to attach additional conditions or modify parameters". So a PreToolUse hook can still "veto" even after the permission pipeline passes.

Typical use cases:

1. **Security auditing**: Log before dangerous operations like `rm`, `delete`
2. **Input correction**: Automatically add safety prefixes to Bash commands (like `--dry-run`)
3. **Environment checks**: Verify current environment is correct before deployment operations
4. **Compliance approval**: Require additional approval for operations involving production environments

Configuration example -- Block all writes to production environment config files:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write",
      "hooks": [{
        "type": "command",
        "command": "echo $INPUT_JSON | python3 -c \"import sys,json; d=json.load(sys.stdin); exit(2) if 'prod' in d.get('file_path','') else exit(0)\"",
        "message": "Checking production file protection..."
      }]
    }]
  }
}
```

**PostToolUse** (After tool execution)

Input contains tool call parameters and response. Can be used for audit logs, result post-processing. You can also set the `updatedMCPToolOutput` field to override MCP tool's actual output.

Typical use cases:

1. **Audit trail**: Record each tool call's parameters and results to external systems
2. **Result enhancement**: Append additional notes or warnings after tool output
3. **Automatic notification**: Send Slack/email notifications after specific tool calls
4. **MCP output override**: Rewrite or sanitize the values MCP tools return

> **Best practice:** Prefer async mode (`async: true`) when PostToolUse only records audits, metrics, or notifications and nothing downstream must consume its response before the next model turn. Keep it synchronous when the response overrides MCP output, adds context needed immediately, or otherwise affects the next step. The deciding question is whether downstream work must wait, not whether the tool has already finished.

**PostToolUseFailure** (After tool execution failure)

Triggered when tool execution fails due to error, interruption, or timeout. Input contains `error`, `error_type`, `is_interrupt` and `is_timeout` fields, providing detailed failure diagnostics.

Typical use cases:

1. **Error reporting**: Report tool failure info to monitoring systems (like Sentry)
2. **Automatic retry suggestion**: Generate retry strategies based on error type
3. **Failure analysis**: Collect failure scene info for post-analysis
4. **Graceful degradation**: Automatically switch to backup plan when critical tools fail

### User Interaction Lifecycle

**UserPromptSubmit** (When user submits prompt)

Triggered after user submits message, before model processing. This is the key timing to modify user input or inject additional context. Exit code 2 can completely block message processing and erase original prompt.

This event is the translation layer between "user intent" and "model understanding". You can use it to provide additional information to the model without the user knowing, or completely block message sending under specific conditions.

Typical use cases:

1. **Sensitive word filtering**: Detect and block messages containing sensitive information
2. **Context injection**: Automatically attach relevant project documentation based on user message content
3. **Input enhancement**: Expand user's brief questions into more complete prompts
4. **Usage limits**: Block message sending when quota exceeded

Configuration example -- Automatically attach current Git branch info to each user question:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "echo '{\"additionalContext\": \"Current git branch: '$(git branch --show-current)'. Recent commits: '$(git log --oneline -3)'\"}'",
        "message": "Attaching git context..."
      }]
    }]
  }
}
```

**Notification** (When the system sends a notification)

Triggered when system sends notification. Notification types include `permission_prompt`, `idle_prompt`, `auth_success`, etc.

Typical use cases: Integration with external notification systems (like Slack, Teams), sending reminders when Agent needs user intervention.

### Session Lifecycle

Session lifecycle events constitute the complete narrative of an Agent from "birth" to "death".

**SessionStart** (Session startup)

Triggered when session starts, sources include `startup` (new start), `resume` (resume session), `clear` (clear reset), `compact` (restart after compression). Hook's stdout goes to Claude. The system ignores blocking errors -- session start hooks shouldn't block session startup.

<!-- block: ch08.b-cde0bf05 -->
> **Design philosophy:** Why does the system ignore SessionStart hook blocking errors? Because session startup is the system initialization process; if hooks could block startup, one misconfigured hook could make the entire system unstartable -- this violates the "graceful degradation" principle. Core system functions should not let extension logic hijack them.

Typical use cases:

1. **Environment reporting**: Display current environment status at session start (Node version, Git status, etc.)
2. **Project context**: Automatically inject project-specific instructions and constraints
3. **State recovery**: Reload previous working state when resuming sessions
4. **Welcome message**: Display usage guide for new users

Configuration example -- Automatically report project status at session start:

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "echo 'Project: '$(basename $(pwd))', Branch: '$(git branch --show-current)', Status: '$(git status --short | head -5)",
        "message": "Loading project context..."
      }]
    }]
  }
}
```

**SessionEnd** (Session end)

Triggered when session ends, reasons include `clear`, `logout`, `prompt_input_exit`, `other`. Note SessionEnd hooks have separate timeout limits (default 1,500ms) because they run during the shutdown process.

Typical use cases:

1. **Cleanup work**: Delete temporary files, release resources
2. **Session summary**: Save session records to project logs
3. **Usage statistics**: Report session duration and operation statistics
4. **Environment reset**: Restore temporary modifications to hooks or configuration

> **Best practice:** SessionEnd hooks should be as lightweight as possible. A 1,500ms timeout means the system forcibly terminates any operation that exceeds it. If you need time-consuming operations (like uploading large files), trigger a background process in SessionEnd rather than waiting for completion.

**Stop** (Before assistant response ends)

Triggered just before Claude is about to end response. Exit code 2 can inject stderr to model and force continued conversation. This is the key event for implementing "ensure task completion" logic.

This event addresses a concrete problem: LLMs sometimes stop generating before a task is fully complete (e.g., due to token limits or "feeling the answer is sufficient"). Stop hooks give users a chance to "pull the model's sleeve" to continue working.

Typical use cases:

1. **Completeness check**: Check if the model actually completed all requested tasks
2. **Quality gate**: Automatically check code quality after model output
3. **Force continue**: Force model to continue when detecting unfinished TODOs
4. **Auto-summary**: Generate execution summary after model answers

Configuration example -- Ensure model response includes code examples:

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "if echo \"$CLAUDE_OUTPUT\" | grep -q '```'; then exit 0; else echo 'Please include code examples in your response.' >&2; exit 2; fi",
        "message": "Checking response completeness..."
      }]
    }]
  }
}
```

**StopFailure** (When ending due to API error)

Triggered when turn ends due to API error (rate limiting, auth failure, etc.), replacing Stop event. This is a fire-and-forget event -- the system ignores hook output and exit codes.

Typical use cases: Automatic reporting and diagnostic logging of API errors.

### Sub-agent Lifecycle

**SubagentStart / SubagentStop**

Triggered when sub-agent (Agent tool call) starts and ends. Input contains `agent_id` and `agent_type`. SubagentStart's stdout goes to the sub-agent; SubagentStop's exit code 2 can let sub-agent continue running.

> **Cross-reference with Chapter 7:** Sub-agents are a key concept in context management. When the main Agent's context space is insufficient for all information in a complex task, it delegates sub-agents to handle subtasks. Sub-agent lifecycle hooks let you monitor and intervene in this delegation process.

Typical use cases:

1. **Sub-agent auditing**: Record which subtasks went to sub-agents
2. **Resource limits**: Inject resource usage constraints when sub-agent starts
3. **Result validation**: Validate sub-agent output quality after completion
4. **Timeout protection**: Monitor long-running sub-agents

### Compression Lifecycle

**PreCompact / PostCompact**

Triggered before and after compression. PreCompact's stdout joins the compression prompt as custom compression instructions, which is how users customize summarization behavior. Exit code 2 can block compression. PostCompact receives compression summary as input.

PreCompact hook processing flow includes: building hook input, executing hook, extracting custom instructions, merging user instructions with hook instructions.

> **Design reflection:** Why allow hooks to customize compression instructions? Because different projects have different definitions of "what information is important". In an API project, interface definitions and parameter types are critical; in a frontend project, component hierarchy and state management are critical. PreCompact hooks let users customize compression strategies for different projects, so compression keeps what that project calls important.

Typical use cases:

1. **Critical information protection**: Specify which code regions compression must preserve
2. **Compression condition control**: Block compression under specific conditions (like ongoing debugging sessions)
3. **Compression quality monitoring**: Check whether summary lost critical information after compression
4. **Custom summary template**: Define different summary formats for different project types

### Permission and Security Events

**PermissionRequest**: Triggered when permission dialog displays. Hook can return `decision` to allow or deny, and automated approval flows build on that.

> **Cross-reference with Chapter 4:** This event sits in the fourth stage of the permission pipeline. Chapter 4's four stages are validateInput (input validation), hasPermissionsToUseTool (rule matching), checkPermissions (context evaluation) and the interactive prompt (user confirmation); hooks, the classifier and the user are the three decision-makers sharing that last stage, and a PermissionRequest hook can return a `decision` that settles the request before the user ever sees the dialog.

**PermissionDenied**: Triggered when auto-mode classifier rejects tool call. Hook can suggest retry or provide alternatives. This is useful for implementing "soft rejection" strategies -- not simply blocking operations but guiding the model to use a safer way to get the same result.

### Other Events

<!-- block: ch08.b-880141d1 -->
- **Setup**: Triggered during repository initialization and maintenance. Suitable for environment checks or dependency installation when a project is first opened by Claude Code.
- **ConfigChange**: Triggered when configuration file changes. Hook can block changes from taking effect. This is a security audit critical point -- preventing malicious modification of config files to bypass security policies.
- **Elicitation / ElicitationResult**: Triggered when MCP server requests user input. Used for MCP server's interactive authentication or parameter collection flows.
- **CwdChanged / FileChanged**: Triggered when working directory and files change. Suitable for implementing filesystem monitoring and auto-refresh caches.
- **InstructionsLoaded**: Triggered when the system loads instruction files (observable only, blocking not supported). Suitable for auditing and logging, understanding what instructions the system loaded.

The table below summarizes the classification, blockability and typical uses of these 22 events:

| Event Name | Category | Blockable | Core Use |
|---------|------|-------|---------|
| PreToolUse | Tool call | Yes | Intercept/modify tool input |
| PostToolUse | Tool call | No | Audit/post-process tool output |
| PostToolUseFailure | Tool call | No | Failure diagnosis/reporting |
| UserPromptSubmit | User interaction | Yes | Modify/block user message |
| Notification | User interaction | No | Notification integration |
| SessionStart | Session management | No* | Environment initialization/context injection |
| SessionEnd | Session management | No | Cleanup/summary |
| Stop | Session management | Yes | Force continue/quality check |
| StopFailure | Session management | No | Error reporting |
| SubagentStart | Sub-agent | No | Sub-agent monitoring |
| SubagentStop | Sub-agent | Yes | Result validation |
| PreCompact | Compression | Yes | Custom compression strategy |
| PostCompact | Compression | No | Compression quality check |
| PermissionRequest | Permission | Yes | Auto permission approval |
| PermissionDenied | Permission | No | Alternative suggestion |
| Setup | Initialization | No | Environment preparation |
| ConfigChange | Configuration | Yes | Config change audit |
| Elicitation | MCP interaction | No | MCP input monitoring |
| ElicitationResult | MCP interaction | No | MCP result monitoring |
| CwdChanged | Environment | No | Directory change notification |
| FileChanged | Environment | No | File change notification |
| InstructionsLoaded | Instructions | No | Instruction loading audit |

* The system ignores SessionStart blocking (graceful degradation design)

A hook takes over at four moments: the event rings, a matcher hooks it, the script runs, the next step gets rewritten.

```ill
ch08-hook-line
```

---

## 8.3 Hook Response Protocol

Hook output is a structured JSON response protocol, parsed by the output parsing function in the hook execution module. Understanding this protocol is the foundation for designing advanced hooks.

> **Design reflection:** Why is hook output structured JSON instead of simple stdout text? Because hooks need precise control over Claude Code's behavior -- not just "say something", but clearly specify "allow" or "block", "modify input" or "inject context". Plain text output can't express this structured intent. Keeping stdout as unstructured output channel (for logging and debugging) while JSON as structured control channel, this dual-channel design balances flexibility and precision.

### Response Protocol Overview

```mermaid
graph TD
    subgraph HookResponseProtocol["Hook JSON Response Protocol"]
        root["Hook Response JSON"]
        root --> decision["decision<br/>approve | block<br/>Global decision"]
        root --> reason["reason<br/>Block reason (when blocking)"]
        root --> context["additionalContext<br/>Inject additional context"]
        root --> cont["continue<br/>true | false<br/>Whether to continue generating"]
        root --> stop["stopReason<br/>Stop reason"]
        root --> hook_specific["hookSpecificOutput<br/>Event-specific output"]
        hook_specific --> event_name["hookEventName<br/>Target event name"]
        hook_specific --> event_fields["Event-specific fields..."]
    end

    subgraph DualChannels["Dual-channel Output"]
        stdout["stdout<br/>Non-JSON part → shown to user<br/>(when exit code non-0)"]
        stderr["stderr<br/>Shown to model (exit code 2)<br/>or user (other non-0 exit codes)"]
    end

    classDef main fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef field fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#424242
    classDef channel fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#e65100

    class root,decision,reason,context,cont,stop,hook_specific main
    class event_name,event_fields field
    class stdout,stderr channel
```

### Top-level Decision Fields

**decision field**: `approve` or `block`

When the hook returns `{"decision": "approve"}`, the tool call goes ahead; when it returns `{"decision": "block"}`, the pipeline blocks the tool call and shows the `reason` field as the block reason.

When the hook output processing function parses the `decision` field, `approve` corresponds to allowing continued execution, `block` corresponds to denial with block reason.

This field's design follows the "default allow, explicit block" principle. If hook output isn't valid JSON, or JSON doesn't have `decision` field, system default behavior is to continue execution (exit code semantics still apply). This design ensures a malformed hook output doesn't accidentally block normal operations.

### hookSpecificOutput Event-specific Output

`hookSpecificOutput` field contains event-specific structured response, identified by `hookEventName` for target event:

**PreToolUse specific fields**:

- `permissionDecision`: Override permission decision, values are `allow`, `deny`, or `ask`
- `permissionDecisionReason`: Decision reason
- `updatedInput`: Runtime modification of tool input

`updatedInput` lets hooks change the parameters actually sent to a tool without changing user intent. For example, automatically adding specific prefixes to all Bash commands, or filtering sensitive parameters.

> **Best practice:** `updatedInput` is a double-edged sword. Used well, it can enhance security without modifying user operations (like auto-adding `--dry-run` flag); abused, it breaks user expectations (like silently modifying file paths causing operations to wrong locations). When using, follow the "transparency principle" -- modifications should be predictable, documented, and visible to users.

**UserPromptSubmit specific fields**:

- `additionalContext`: Inject additional context into user prompt

This field allows hooks to attach extra context information before the user message reaches the model, without modifying the user's original input. This preserves the integrity of user input while giving the model richer background information.

### additionalContext: Injecting Additional Context

`additionalContext` is a generic field shared by multiple events. It injects hook-generated additional information into model context, attached as system reminder messages. This is particularly useful in the following scenarios:

- Injecting project status information in `SessionStart` event
- Adding extra usage notes in `PostToolUse` event
- Injecting environment configuration info in `Setup` event
- Attaching relevant project documentation in `UserPromptSubmit` event

> **Cross-reference with Chapter 5:** `additionalContext` injection mechanism is similar to `customInstructions` in Chapter 5's configuration system, but with a key difference: `customInstructions` are static, determined at config load time, while `additionalContext` is dynamic, generated differently each time hook executes. This is like the difference between "prefabricated panels" and "poured concrete" -- the former is uniform but inflexible, the latter is flexible but requires more on-site work.

### continue Field

The `continue` field controls whether the assistant should continue responding. When set to `false`, the assistant stops generating, and the `stopReason` field can provide the stop reason. This allows hooks to force the assistant to stop when detecting specific conditions.

Typical application: In the Stop event, when the hook detects that the model has output sufficient content, or detects that the model is drifting off-topic, it can force generation termination via `continue: false`.

### Collaboration Between Exit Codes and JSON Response

Two dimensions jointly control hook behavior: **exit code** (process level) and **JSON response** (content level). Understanding their collaboration is key to designing correct hooks:

```mermaid
flowchart TD
    hook["Hook execution complete"] --> exit{"Exit code?"}
    exit -->|"0"| e0{"JSON decision?"}
    e0 -->|"approve or none"| pass["Normal pass"]
    e0 -->|"block"| json_block["Block (JSON priority)"]

    exit -->|"2"| e2["Block<br/>stderr shown to model"]
    e2 --> json_any["Regardless of JSON decision"]

    exit -->|"Other non-0"| e3{"JSON decision?"}
    e3 -->|"approve"| warn["Warning but continue"]
    e3 -->|"block"| other_block["Block"]

    classDef decision fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#e65100
    classDef pass_node fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef block_node fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px,color:#b71c1c
    classDef warn_node fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#f57f17

    class exit,e0,e3 decision
    class pass pass_node
    class json_block,e2,json_any,other_block block_node
    class warn warn_node
```

| Exit Code | JSON decision | Final Effect |
|--------|--------------|---------
| 0 | approve or none | Normal pass |
| 0 | block | Block (JSON priority) |
| 2 | Any | Block, stderr shown to model |
| Other non-0 | approve | Warning but continue |
| Other non-0 | block | Block |

> **Anti-pattern warning:** Don't rely on exit codes and JSON decision to express contradictory intents. For example, exit code 0 but decision block, or exit code 2 but decision approve. Although system has clear processing priority, contradictory signals will confuse maintainers and increase debugging difficulty.

---

<!-- block: ch08.b-a4493a50 -->
## 8.4 Hook Configuration and Security

### Configuration Validation

Zod Schema strictly validates hook configuration. The hook Schema module defines the complete type system:

- `HookCommandSchema`: Discriminated union of four persistable hooks -- the `type` field (`command`, `prompt`, `agent`, `http`) does the discriminating
- `HookMatcherSchema`: Matcher configuration, containing `matcher` string pattern and `hooks` array
- `HooksSchema`: Top-level configuration, mapping events to matcher arrays using `partialRecord`

> **Cross-reference with Chapter 5:** Hook configuration is an important component of the six-layer configuration system introduced in Chapter 5. Each layer stores hook configuration in its `hooks` field, following the same merge and override rules as regular settings. Understanding Chapter 5's configuration merge mechanism helps you understand why hooks with the same name defined in different config files exhibit specific priority behaviors.

Matchers filter by permission rule syntax (`if` condition field). For example `"Bash(git *)"` only triggers hook when Bash tool call starts with `git`. This condition field is an optional string matched with permission rule syntax.

Complete hook configuration structure example:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 scripts/check_bash_safety.py",
            "timeout": 5000
          }
        ]
      },
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if this file write is safe. $ARGUMENTS"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cat .claude/context.md 2>/dev/null || echo 'No project context file found'",
            "message": "Loading project context..."
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 scripts/check_task_completion.py",
            "asyncRewake": true
          }
        ]
      }
    ]
  }
}
```

### Hook Sources and Priority

Hooks come from multiple configuration sources. The `getAllHooks` function shows the collection process: first check if restricted to managed hooks only, if not restricted, collect hooks from userSettings, projectSettings, localSettings sources, finally getting session hooks.

The `sortMatchersByPriority` function defines priority ordering. Priority is based on configuration source constant array with order: localSettings, projectSettings, userSettings.

Complete priority order:

```mermaid
graph TD
    subgraph HookPriority["Hook Priority (High to Low)"]
        p1["1. userSettings<br/>User global settings ~/.claude/settings.json"]
        p2["2. projectSettings<br/>Project settings .claude/settings.json"]
        p3["3. localSettings<br/>Local settings .claude/settings.local.json"]
        p4["4. pluginHook<br/>Plugin hooks (priority = 999)"]
        p5["5. builtinHook<br/>Built-in hooks"]
        p6["6. sessionHook<br/>Session temporary hooks"]
    end

    p1 --> p2 --> p3 --> p4 --> p5 --> p6

    classDef high fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef mid fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#e65100
    classDef low fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#757575

    class p1 high
    class p2,p3 mid
    class p4,p5,p6 low
```

Sorting hands plugin hooks and built-in hooks the lowest priority values, so they never override user-configured hooks.

> **Design reflection:** Why do the user's global settings rank highest? Because of user sovereignty -- users' personal configuration should be able to override project configuration and plugin defaults. This aligns with Chapter 4's permission pipeline design philosophy of "user decisions take precedence over auto-mode classifier". In a multi-user collaborative project, each developer should be able to customize hook behavior according to their own security preferences.

### Priority Conflict Resolution Case Studies

The best way to understand priority ordering is through practical cases.

**Case 1: Multiple hooks for same event**

Suppose three configuration sources define hooks for `PreToolUse` event:

```
userSettings:    [Hook A: Audit log]
projectSettings: [Hook B: Security check]
localSettings:   [Hook C: Local debugging]

Execution order (by priority high to low):
  1. Hook A (userSettings) -- executes first
  2. Hook B (projectSettings) -- executes second
  3. Hook C (localSettings) -- executes last
```

Note: All matching hooks will execute, unless one hook returns `decision: "block"`. Once a hook blocks the operation, subsequent lower-priority hooks will still execute (they just see the blocked state), but the operation itself is already blocked.

**Case 2: Matcher fine-grained control**

Same event can have multiple matchers, each targeting different tools:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(rm *)",
        "hooks": [{"type": "command", "command": "python3 check_delete.py"}]
      },
      {
        "matcher": "Bash(npm publish *)",
        "hooks": [{"type": "command", "command": "python3 check_publish.py"}]
      },
      {
        "matcher": "Write",
        "hooks": [{"type": "command", "command": "python3 check_write.py"}]
      }
    ]
  }
}
```

In this configuration, if the model executes `rm -rf /tmp/test`, only the first matcher triggers; if it executes `npm publish`, only the second matcher triggers; if it is a file write operation, only the third matcher triggers.

### Emergency Disable Switches

Claude Code provides multiple security switches to handle hook-related risks. That is "Defense in Depth" -- no single measure carries the load, and every gate gets its own barrier.

```mermaid
flowchart TD
    start["Hook trigger"] --> layer1{"Layer 1: Global disable<br/>disableAllHooks: true?"}
    layer1 -->|"Yes"| disabled["All hooks disabled<br/>(Emergency security incident / Troubleshooting)"]
    layer1 -->|"No"| layer2{"Layer 2: Managed mode check<br/>allowManagedHooksOnly: true?"}
    layer2 -->|"Yes"| managed["Only allow enterprise policy-configured hooks<br/>(Enterprise compliance environment)"]
    layer2 -->|"No"| layer3{"Layer 3: Workspace trust check<br/>Is workspace trusted?"}
    layer3 -->|"No"| untrusted["Refuse to execute user/project configured hooks<br/>(Cloned third-party repository)"]
    layer3 -->|"Yes"| execute["Execute hooks normally"]

    classDef gate fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#e65100
    classDef blocked fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px,color:#b71c1c
    classDef allowed fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef managed_node fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1

    class layer1,layer2,layer3 gate
    class disabled,untrusted blocked
    class execute allowed
    class managed managed_node
```

**Global disable**: When `policySettings` (enterprise policy configuration) has `disableAllHooks: true`, the system disables all hooks (including managed hooks). This is the ultimate emergency switch.

**Restrict to managed hooks only**: Check `allowManagedHooksOnly` field in policy settings; when this mode is on, the system blocks all hooks from user/project/local configs, only allowing hooks deployed by enterprise admins through policy configuration.

**Workspace trust check**: All hooks in interactive mode require you to trust the workspace first. The check function determines whether the current session is non-interactive (SDK mode implicitly grants trust) and whether the user has accepted the trust dialog.

In interactive mode, every hook needs you to trust the workspace first. This is a defense-in-depth measure -- hook configuration lives in `.claude/settings.json`; executing these commands in an untrusted workspace is unsafe. Imagine: you cloned an open-source project, the project's `.claude/settings.json` might contain malicious hooks (like PreToolUse hook sending your sensitive data to external servers). Workspace trust check is the key defense against this "supply chain attack".

The `executeHooks` function chains these checks together, forming complete security gating: first check global disable switch, then check simple mode flag, finally check workspace trust status; only after all pass does normal hook execution proceed.

### Session Hook Special Design

Session hooks use `Map` instead of `Record` to store state, a deliberate performance design.

In parallel workflows, N Agents might register hooks in the same synchronous clock cycle. Using `Record` spread operations would cause O(N^2) total overhead, while `Map.set()` is O(1), and returning the unmodified `prev` reference avoids triggering ~30 store listeners.

> **Performance analysis:** Why is this optimization so important? In a typical parallel Agent scenario, assume 10 sub-agents simultaneously register hooks. With `Record`, each registration creates a new object and triggers every listener, so the overhead is 10 * 10 = 100 listener triggers. With `Map`, `set()` modifies in place and returns the same reference, so listeners do not fire. In high-frequency hook registration/deregistration, the gap widens: on a high-concurrency path, data structure choice is not a preference question but a correctness question.

---

## 8.5 Hook Best Practices and Anti-patterns

The places where hooks go wrong are quite fixed; one table collects them:

| Common mistake | Correct approach |
|:--------------:|-----------------|
| Expect exit code 1 to block an operation; it only logs a warning | To block, exit 2 -- that is when stderr reaches the model (8.3) |
| Run a five-minute code review inside PreToolUse | Keep synchronous hooks under a second; long tasks go async or asyncRewake (8.5) |
| No matcher, so your hook fires on every tool call | Filter precisely with `"matcher": "Bash"`; skip the wasted runs (8.5) |
| `updatedInput` silently changes a file path; the user finds the operation landed elsewhere | Rewrites must be predictable, documented, and visible to the user (8.3) |
| Hooks in a cloned third-party repo run without a second thought | The workspace trust check stands in front; untrusted means refused (8.4) |

### Best Practices Checklist

**1. Keep hooks lightweight**

Hooks run on Agent's main execution path (in sync mode). A 5-second hook makes users feel Claude Code is "stuck". Try to keep hook execution time under 1 second. For time-consuming operations, use async mode or async-rewake mode.

**2. Handle exceptions gracefully**

Hooks should be responsible for their own errors. Don't let hook exceptions crash the Agent. Use `try-catch` in Command hook scripts (or Shell's `||` fallback), ensuring the script returns meaningful exit codes even when it errors.

**3. Use matcher for precise filtering**

Don't register a hook without matcher on `PreToolUse` then judge tool type in script -- this causes your hook to execute on every tool call, even when it only needs to handle `Bash` tool. Using `"matcher": "Bash"` for precise filtering greatly reduces unnecessary hook execution.

**4. Document your hook intent**

Use comments in config files (or adjacent README files) to explain each hook's purpose and behavior. You, returning to look at the config three months later, will thank yourself for writing comments now.

**5. Follow principle of least privilege**

Only intercept events you need, only use response fields you need. Don't register hooks on all events "just in case" -- each hook has performance overhead and maintenance cost.

### Anti-pattern Warnings

**Anti-pattern 1: Executing time-consuming operations in PreToolUse**

```json
// Anti-pattern: Complete code review before every tool call
{
  "PreToolUse": [{
    "hooks": [{
      "type": "command",
      "command": "npm run full-code-review",
      "timeout": 300000
    }]
  }]
}
```

This makes you wait 5 minutes for code review before every tool call. The correct approach is to use async mode only for review in the `Write` tool's `PostToolUse`.

**Anti-pattern 2: Circular dependencies between hooks**

Hook A's execution triggers event Hook B listens to, Hook B's execution triggers event Hook A listens to. Claude Code has internal mechanisms preventing infinite recursion, but circular dependencies cause performance degradation and unpredictable behavior.

**Anti-pattern 3: Overusing updatedInput**

```json
// Anti-pattern: Silently modify all Bash commands
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{
      "type": "command",
      "command": "echo $INPUT_JSON | jq '.tool_input.command |= \"sudo \" + .' | jq '{\"hookSpecificOutput\": {\"hookEventName\": \"PreToolUse\", \"updatedInput\": .tool_input}}'"
    }]
  }]
}
```

Adding `sudo` to all commands may cause privilege escalation risk. `updatedInput` should only be used for security enhancement, not changing operation's essential semantics.

**Anti-pattern 4: Ignoring timeout settings**

Command hooks have a default timeout, but if it is not explicitly set, the hook may block the Agent indefinitely due to a script hang. Always set reasonable timeout values for your hooks.

### Complete Practical Case: Enterprise-level Security Audit System

Below is an enterprise-level security audit configuration comprehensively using multiple hook types and lifecycle events:

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "python3 scripts/session_init.py --report-env",
        "message": "Initializing security audit session..."
      }]
    }],
    "PreToolUse": [
      {
        "matcher": "Bash(rm *)",
        "hooks": [{
          "type": "command",
          "command": "python3 scripts/validate_delete.py",
          "timeout": 3000,
          "message": "Validating delete operation..."
        }]
      },
      {
        "matcher": "Write",
        "hooks": [{
          "type": "prompt",
          "prompt": "Analyze the file being written. If it modifies production config files (*.production.*), return {\"decision\": \"block\", \"reason\": \"Production config changes require approval\"}. Otherwise return {\"decision\": \"approve\"}. File content: $ARGUMENTS"
        }]
      }
    ],
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "http",
        "url": "https://audit.internal.company.com/api/log",
        "headers": {
          "Authorization": "Bearer $AUDIT_TOKEN"
        },
        "allowedEnvVars": ["AUDIT_TOKEN"],
        "async": true
      }]
    }],
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "python3 scripts/check_completion.py",
        "asyncRewake": true
      }]
    }],
    "SessionEnd": [{
      "hooks": [{
        "type": "command",
        "command": "python3 scripts/session_summary.py",
        "timeout": 1500
      }]
    }]
  }
}
```

This one configuration produces a complete security audit flow: recording environment info at session initialization, checking security before deletions, having the LLM review file write content, async audit log reporting after Bash operations, task completeness check at response end, and summary report generation at session end.

---

## Practical Exercises

**Exercise 1: Configure security review hook**

Write a PreToolUse hook configuration requiring:
- Only intercept `Write` tool calls
- Check if target path is within allowed directories (like `src/` and `test/`)
- If path is invalid, block operation with exit code 2 and show reason

Hint: Hook input comes via stdin in JSON format, containing `tool_name` and `tool_input` fields.

**Extended challenge:** Extend your hook to also support intercepting file write commands in `Bash` tool (like `cp`, `mv`, `>` redirection). Think about how to extract target path from Bash command string.

**Exercise 2: Session context injection**

Design a SessionStart hook that at each session start:
- Reads project's `package.json` to get dependency list
- Injects key dependency info as `additionalContext`

Think: How to handle case where `package.json` doesn't exist? How to handle JSON parsing errors?

**Extended challenge:** Design a UserPromptSubmit hook that dynamically retrieves relevant content from project documentation based on user message keywords and injects as `additionalContext`. This requires combining file search and keyword matching logic.

**Exercise 3: Hook priority analysis**

Given following hook configurations (for same event):
- `~/.claude/settings.json` defines Hook A (audit log)
- `.claude/settings.json` defines Hook B (security check)
- Plugin registers Hook C (auto-formatting)
- Runtime registers Hook D (dynamic validation) via `addFunctionHook`

Analyze:
1. When event triggers, what is the execution order of these hooks?
2. If Hook A returns `decision: "block"`, will Hook B/C/D still execute?
3. If Hook B modifies `updatedInput`, does Hook C see original input or modified input?

**Exercise 4: Async hook design**

Design an async-rewake hook for Stop event requiring:
- Monitor an external task queue in background
- When detecting new high-priority task (exit code 2), wake model to continue processing
- Normal operation (exit code 0) doesn't disturb model

Think: How to avoid "thrashing" -- the model wakes up and stops again right away, over and over?

**Exercise 5: Security scenario analysis**

Analyze following scenarios and provide hook configuration recommendations:

A team is developing a web application handling user sensitive data. Team has following security requirements:
1. Forbid Agent from modifying `src/config/production.ts`
2. All modifications to database-related files need LLM review
3. You need to report every session's operation records to the internal audit system
4. Agent should automatically run related tests after completing code modifications

Design a complete hook configuration solution meeting above requirements.

---

## Key Takeaways

1. **Five hook types**: command (Shell command), prompt (LLM evaluation), agent (Agentic validation), http (HTTP call), function (runtime callback); the first four are persistable, the last lives only in session memory. The decision tree reads: use Command to run a system command, Prompt when a step needs judgment, Agent for multi-step validation, HTTP to integrate an external system, Function for deep runtime interaction.

2. **22 lifecycle events**: Covering complete Agent lifecycle including tool calls, user interaction, session management, sub-agents, compression, permissions, configuration changes. Each event has clear trigger timing, input structure, and exit code semantics.

3. **Structured response protocol**: Hook output is JSON containing `decision` (approve/block), `updatedInput` (modify tool input), `additionalContext` (inject context) fields. Exit codes and JSON response jointly control hook behavior; both should express consistent intent.

4. **Priority ordering**: userSettings > projectSettings > localSettings > pluginHook > builtinHook > sessionHook; user configuration always has highest priority. Multiple matching hooks execute in priority order; any hook's block decision takes effect.

5. **Multi-layer security mechanism**: Global disable switch (`disableAllHooks`), managed-hooks-only mode (`allowManagedHooksOnly`), workspace trust check -- three security gates filter progressively. This embodies defense-in-depth security design philosophy.

6. **Async hooks**: `async` and `asyncRewake` modes allow hooks to run in background; latter can wake model on error, suitable for long-running monitoring tasks. Async hooks interact with main loop through notification queue, not blocking Agent execution.

7. **Session hook Map design**: Using `Map` instead of `Record` for storage reduces O(N^2) overhead to O(1) in high-concurrency scenarios. This is a classic case of data structure choice affecting system performance.

8. **Collaboration with permission pipeline** (Chapter 4): PreToolUse hooks run after permission pipeline, as second security check. Permission pipeline determines "whether can execute", hooks determine "how to execute". Both together form Claude Code's security protection system.

9. **Collaboration with configuration system** (Chapter 5): Hook configuration follows six-layer configuration system merge rules, supporting different security policies at different levels. Enterprise policy layer can control global behavior through `disableAllHooks` and `allowManagedHooksOnly`.

> **Three sentences to keep:** ①Every hook speaks one language: a JSON response protocol plus exit codes -- the engine trusts the protocol, never the implementation. ②One shared protocol lets five hook types plug into 22 lifecycle points, and any hook's block decision takes effect. ③Keep the division of labor straight: the permission pipeline decides whether an action may run, hooks decide how it runs -- after the guardrail, hooks are the second security check.
