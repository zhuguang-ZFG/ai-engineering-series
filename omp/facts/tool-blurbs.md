## bash
Execute a shell command in the session workspace, with optional PTY, background-job handling, or supervised service mode.
## Source
## Inputs
## Outputs
## Command policy and dedicated-tool routing
## Flow
## Modes / Variants
## Side Effects
## Limits & Caps

## eval
Execute one Python or JavaScript cell in a persistent language runtime. One tool call is one cell; state survives later calls.
## Source
## Inputs
## Scripts and dependencies
## Backend availability
## Outputs
## Execution flow
## Auto-backgrounding
## Runtime behavior

## lsp
Query language servers for diagnostics, navigation, symbols, renames, code actions, capabilities, and raw requests.
## Source
## Inputs
## Outputs
## Flow
## Modes / Variants
## Side Effects
## Limits & Caps
## Errors

## debug
Drive one DAP debug session; adjacent debug UI code reuses the same subsystem for logs, raw SSE capture, reports, profiling, and system diagnostics.
## Source
## Inputs
## Outputs
## Flow
## Modes / Variants
## Side Effects
## Limits & Caps
## Errors

## browser

## Source
## JavaScript API
## Python API
## Browser modes
## Screenshots and output
## Safety and lifecycle
## Common recovery

## computer
Drive the real host desktop from Eval through direct `computer` helpers and window/element handles, or persistent JavaScript via `computer.run`: enumerate windows and displays, capture screenshots, send native input, use OS accessibility (AX), and access the clipboard. This is not the `browser` prelude and exposes no DOM.
## Source
## Availability and declaration
## Settings
## Eval API
## Desktop API
## Outputs
## Flow and lifecycle
## Side effects

## web_search
Run one web query through the configured search chain and return the first usable answer/sources, with optional citations.
## Source
## Inputs
## Outputs
## Flow
## Modes / Variants
## Side Effects
## Limits & Caps
## Errors

## github
Dispatch GitHub CLI operations for repositories, repository files, pull requests, search, and Actions run watching.
## Source
## Availability and approval
## Inputs
## Outputs
## Flow
## Modes / Variants
## Side Effects
## Limits & Caps

## todo
Applies one mutation to the session todo list and returns a text summary plus the full phase/task state.
## Source
## Inputs
## Outputs
## Flow
## Modes / Variants
## Side Effects
## Limits & Caps
## Errors

## task
Spawn subagents — one per call, or a `tasks[]` batch per call (`task.batch`, default on). With `async.enabled=true`, ordinary spawns run in the background; otherwise the call blocks until they finish. Execution mode is per item: an item whose custom agent type declares `blocking: true` runs inline while non-blocking items in the same call still spawn as background jobs. No bundled agent currently declares `blocking: true`.
## Source
## Inputs
## Outputs
## Flow
## Modes / Variants
## Side Effects
## Limits & Caps
## Errors

## wait
Block until the next background result, peer message, or steering interrupt when there is no other work to do.
## Source
## Input and availability
## Behavior
## Related surfaces

## ast-grep
Structural code search over supported source files via native ast-grep.
## Source
## Inputs
## Outputs
## Flow
## Modes / Variants
## Side Effects
## Limits & Caps
## Errors

## ast-edit
Preview and apply structural rewrites over source files via native ast-grep.
## Source
## Inputs
## Outputs
## Flow
## Modes / Variants
## Side Effects
## Limits & Caps
## Errors

## write
Create or overwrite a file, writable internal resource, archive entry, SQLite row, or merge-conflict resolution.
## Source
## Inputs
## Outputs
## Flow
## Modes / Variants
## Side Effects
## Limits & Caps
## Errors
