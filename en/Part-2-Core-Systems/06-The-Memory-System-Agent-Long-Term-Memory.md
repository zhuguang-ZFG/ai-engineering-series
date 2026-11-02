# Chapter 6: The Memory System -- Agent Long-Term Memory

> **Learning Objectives:** What each of the four memory types holds and who extracts it; how the Fork pattern lets parallel Agents share one cache; how you build a memory system that lives on disk. By the end of this chapter you can make memory earn its keep the more you use it, and keep it tidy across projects.

---

Humans stay coherent across conversations because they have memory. Similarly, a truly useful Agent cannot start from scratch every conversation -- it needs to remember who the user is, what the project is doing, and which practices turned out to work. Claude Code's memory system (memdir) serves exactly this purpose: a file-based, typed, cross-session persistent memory architecture.

Comparing the memory system to "long-term memory" is a biologically precise analogy. Human memory falls into sensory memory (milliseconds), working memory (seconds, corresponding to the context management in Chapter 7), and long-term memory (minutes to years, corresponding to the memory system in this chapter). Claude Code's design follows this same layering: the context window is "working memory," temporarily holding information within a single session; while memdir is "long-term memory," persistently storing non-derivable critical knowledge across sessions.

## 6.1 Taxonomy of the Four Memory Types

### 6.1.1 Closed Type System

Claude Code keeps its memory inside a closed four-type system, spelled out in the memory type constants: user, feedback, project, and reference.

The design philosophy of these four types is: **only save information that you cannot derive from the current project state.** Tools (grep, git log) can fetch code patterns, architecture, file structure, and Git history in real time, so they do not fall within the scope of memory.

**Why must it be a closed system?**

An open type system (allowing arbitrary custom types) appears more flexible but has fatal flaws in the Agent scenario: (1) Type explosion -- different users and projects might create dozens of types, making it impossible for the Agent to efficiently determine which memories are relevant to the current conversation when reading; (2) Classification ambiguity -- the same piece of information might belong to multiple custom types, leading to duplicate storage; (3) Index bloat -- the MEMORY.md index would need to maintain classification logic for each type, adding unnecessary complexity.

The closed four-type design embodies a "constraint is freedom" philosophy: constraining the classification method yields efficient consistent reasoning and precise relevance judgment.

### 6.1.2 Detailed Analysis of the Four Types

The relationship between the four memory types can be understood through a two-dimensional matrix:

```mermaid
graph LR
    subgraph MemoryTypeMatrix["Memory Type 2D Matrix"]
        direction TB
        label_row1["Subjective/Directive"]
        label_row2["Objective/Factual"]
        label_col1["Personal Dimension<br/>(About the Person)"]
        label_col2["Project Dimension<br/>(About the Work)"]

        user["user<br/>User Profile<br/>Who is using?"]
        feedback["feedback<br/>Feedback Directives<br/>What practices are validated?"]
        empty_cell["(Usually not needed)"]
        project["project<br/>Project State<br/>Why is it done this way?"]
        reference["reference<br/>External References<br/>Where to find more info?"]
    end

    label_row1 --- user
    label_row1 --- feedback
    label_row2 --- empty_cell
    label_row2 --- project
    label_row2 --- reference
    label_col1 --> user
    label_col1 --> empty_cell
    label_col2 --> feedback
    label_col2 --> project
    label_col2 --> reference

    classDef subjective fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px,color:#1a237e
    classDef objective fill:#e8f5e9,stroke:#4caf50,stroke-width:2px,color:#1b5e20
    classDef dim fill:#f5f5f5,stroke:#bdbdbd,stroke-width:1px,color:#757575

    class user,feedback subjective
    class project,reference objective
    class empty_cell,dim dim
```

> **user** -- User Profile

Stores the user's role, goals, and knowledge background. Helps the Agent adjust its collaboration style for users of different expertise levels -- it should communicate differently with a senior engineer versus a beginner.

```
when_to_save: When learning about the user's role, preferences, or knowledge background
how_to_use:  When needing to adjust explanation depth and collaboration style based on the user profile
```

Example: When a user says "I've been writing Go for ten years, but this is my first time touching React," the Agent saves a user-type memory and uses backend analogies when explaining frontend concepts in the future.

**Practical Application Scenarios:**

Scenario 1: Cross-project user preferences. After a user expresses preferences in project A, the Agent can apply the same preferences in project B. Because user-type memories live in the user's global directory, cross-project sharing comes for free.

Scenario 2: Progressive understanding of the user. In the first conversation, the user mentions being a data scientist, and the Agent records this as a user memory. In the fifth conversation, the user demonstrates advanced Python skills, and the Agent updates the memory to add "proficient in Python, familiar with pandas/numpy." This progressive user profile building enhances the Agent's collaboration capabilities over time.

**feedback -- Feedback Directives**

Records the user's corrections and confirmations regarding Agent behavior. This is one of the most important memory types -- it enables the Agent to maintain behavioral consistency across future conversations.

```
when_to_save: When the user corrects your approach ("don't do that") or confirms a non-obvious successful practice
body_structure: The rule itself + Why: reason + How to apply: applicable scenarios
```

Key design: it records failures (corrections) and successes (confirmations). If you only save corrections, the Agent becomes overly cautious, deviating from validated methods.

**Practical Application Scenarios:**

Scenario 1: Code style preferences. The user says "don't use var, use const and let for everything," and the Agent saves this as a feedback memory. In all subsequent conversations, the Agent's generated code defaults to using const/let.

Scenario 2: Process requirements. The user says "lint must be run before committing code," and the Agent saves this as a feedback memory. Before every subsequent git commit execution, the Agent automatically runs the lint command.

Scenario 3: Lessons from failure. The user says "last time you directly modified package.json which caused version conflicts; from now on, check with me before changing dependencies," and the Agent saves this as a feedback memory, proactively requesting confirmation when modifying dependency files in the future.

**project -- Project State**

Records the non-code state of a project -- decisions, deadlines, work in progress. Code and Git history are derivable, but information like "why it happened this way" and "when the work is due" is not.

```
when_to_save: When learning about who is doing what, why, and when it will be completed
body_structure: Fact or decision + Why: motivation + How to apply: impact on recommendations
```

Special attention: Convert relative dates to absolute dates ("Thursday" -> "2026-03-05"), because memories persist across sessions, and relative dates lose their meaning in future conversations.

**Practical Application Scenarios:**

Scenario 1: Architecture Decision Records (ADR). The user says "the authentication module uses JWT instead of Session because it needs to support mobile clients," and the Agent saves this as a project memory. When authentication-related code needs modification in the future, the Agent can understand the background of this decision.

Scenario 2: Work in progress. The user says "I'm migrating the user module from REST to GraphQL; I've completed the query part and need to work on the mutation part next," and the Agent saves this as a project memory. In the next conversation, the Agent can continue working from the correct context.

Scenario 3: Team conventions. The user says "our team agreed that all API responses use camelCase, but database fields use snake_case," and the Agent saves this as a project memory, following this convention when generating code.

**reference -- External References**

Pointers to external systems -- Linear projects, Grafana dashboards, Slack channels. This information is not in the code repository but you need it to understand the project context.

```
when_to_save: When learning about external system resources and their purposes
how_to_use:  When the user references external systems or needs to look up external information
```

**Practical Application Scenarios:**

Scenario 1: Monitoring dashboards. The user says: "the production Grafana dashboard is at [https://grafana.company.com/d/abc123](https://grafana.company.com/d/abc123)." The Agent saves this as a reference memory. When the user asks, "any anomalies recently," the Agent can remind the user to check this dashboard.

Scenario 2: Documentation links. The user says: "the API docs are on Confluence at [https://confluence.company.com/pages/api-docs](https://confluence.company.com/pages/api-docs)." The Agent saves this as a reference memory.

Scenario 3: Communication channels. The user says "backend team discussions are in the #backend-dev Slack channel," and the Agent saves this as a reference memory, reminding the user when cross-team coordination comes up.

### 6.1.3 Explicitly Excluded Information

The memory type validation module explicitly lists content you should not save as memory:

- Code patterns, conventions, architecture, file paths -- derivable by reading code
- Git history -- `git log` / `git blame` are authoritative sources
- Debugging solutions -- the fix is already in the code, the context is in the commit message
- Documentation already in CLAUDE.md
- Temporary task details -- transient state of the current conversation

Even when a user **explicitly requests** saving such information, the system guides toward a more valuable direction: "If you want to save a list of PRs, tell me what's **surprising** or **non-obvious** about them -- that's what's worth saving."

**The Deeper Logic of This Exclusion Principle**

Many users, when first using the memory system, try to have the Agent memorize "the project's file structure" or "the API route list." This instinct is understandable -- humans do need this information when taking over a new project. But there is a key difference between Agents and humans: Agents can read the file system in real time during every conversation.

```
Information Acquisition Cost Comparison:

Human Developer:
  Memorize file structure -> hours of reading and understanding
  Recall when needed next time -> seconds (if remembered)
  -> Value of memory = time saved from re-reading

Agent:
  Read file structure in real time -> milliseconds for a tool call
  Cost of re-acquiring each time -> a few hundred tokens
  -> Value of memory ≈ 0 (because real-time acquisition cost is minimal)
```

Therefore, the memory system should focus on saving information that "you cannot acquire in real time" -- people's preferences, the rationale behind decisions, external links. The common characteristic of this information is that it exists in people's minds or external systems, and reading the code repository cannot supply it.

### 6.1.4 Best Practices for Memory Usage

**Memories That Should Be Saved (Positive Examples):**

| Scenario | Memory Type | Content to Save |
|----------|-------------|-----------------|
| User expresses preference | feedback | "User prefers Vitest over Jest" + Why: faster test execution |
| User corrects behavior | feedback | "Don't modify files in the generated folder" + Why: they are auto-generated by protoc |
| Architecture decision | project | "Use event-driven architecture instead of direct calls" + Why: need for service decoupling |
| External system link | reference | "Monitoring alerts are in PagerDuty's X service" |
| User background | user | "User is a full-stack developer, proficient in TypeScript and Python" |

**Memories That Should NOT Be Saved (Negative Examples):**

| Scenario | Why Not to Save | Correct Approach |
|----------|----------------|------------------|
| Project file listing | Can be obtained in real time via `ls` | No memory needed |
| API endpoint list | Can be obtained by reading route code | If there are non-obvious design decisions, save only the decisions |
| Bug fix steps | Already recorded in commit messages | If the fix involves counter-intuitive reasons, save the "why" |
| Third-party library versions | Can be obtained by reading package.json | If there are special reasons for the selection, save the reasons |

### 6.1.5 Common Misconceptions in Memory Management

**Misconception 1: More Memories Is Better**

This is the most common misconception. Some users have the Agent memorize every detail from conversations, leading to MEMORY.md index bloat and a large accumulation of low-value files in the memory directory. Too many memories not only increase the context burden for each conversation but may also bury the Agent in "noise", so it overlooks truly important memories.

**Correct approach:** Regularly review the memory directory and delete outdated or low-value memories. A good memory should pass the test of "if you deleted this memory, would the Agent's behavior be substantively different?"

**Misconception 2: Treating Memory as a Documentation System**

Some users try to use the memory system as a replacement for project documentation, having the Agent memorize all technical specifications and design documents. This violates the principle of "only save non-derivable information" -- technical specifications belong in the code repository's documentation directory, not in the memory system.

**Correct approach:** Place technical documentation in the `docs/` directory, and the "why" behind architectural decisions in memory.

**Misconception 3: Ignoring the Relative Date Problem**

The user says "this feature launches next Tuesday," and the Agent saves "launches next Tuesday." But two days later in the next conversation, "next Tuesday" has become "this Tuesday," and a week later it becomes "last Tuesday." This memory is not only useless but potentially misleading.

**Correct approach:** All time-related memories must use absolute dates. The Agent should convert "next Tuesday" to a specific date (e.g., 2026-04-07) before saving.

> **Cross-Reference:** The exclusion principle for memories shares the same philosophy as the compression strategy in Chapter 7 (Context Management) -- only retain information that cannot be re-acquired. Context compression clears old tool results (which can be re-acquired by re-executing tools), and the memory system excludes code patterns (which can be re-acquired by re-reading code).

## 6.2 Memory File Format

### 6.2.1 Frontmatter Format

Each memory is an independent Markdown file that uses YAML Frontmatter to declare metadata. The format requires three fields: name (memory name), description (a one-line description used to determine relevance in future conversations), and type (one of the four types). The `type` field must be one of the four types (strictly validated); legacy files without a type field still work, but you cannot filter them by type.

**Why use Markdown files instead of a database?**

This is an architectural choice worth analyzing. Using a file system instead of a database has the following advantages:

1. **Readability**: Developers can directly view and edit memory files with a text editor
2. **Version control**: Memory files naturally support Git tracking (if placed in a project directory)
3. **Portability**: The file system is the lowest common denominator, requiring no additional dependencies
4. **Debuggability**: When problems occur, simply `ls` and `cat` to diagnose
5. **Cost**: No need to maintain database connections, indexes, or backups

The downside is what you can ask of it -- no complex relational queries, no full-text search. However, for the Agent's memory scenario, the query pattern is a simple "load all relevant memories" rather than complex relational queries, and the file system's capabilities are sufficient.

### 6.2.2 MEMORY.md Index File

`MEMORY.md` is the entry point of the memory system -- it is not a memory itself but an index file. At the start of each conversation, the system automatically loads it into the context, which is how the Agent picks up an overview of existing memories.

The memory directory module's constants define the index capacity limits: the index file is named `MEMORY.md`, with a maximum of 200 lines and 25KB.

The format for index entries requires one line per entry, no more than 150 characters:

```markdown
- [Title](file.md) -- One-line hook description
```

The `truncateEntrypointContent` function sets two capacity gates: first truncation by lines (200-line limit), then truncation by bytes (25KB limit). When content exceeds a limit, the function appends a warning at the end of the file naming which gate tripped.

**The Design Wisdom of Dual Capacity Protection**

Why are two layers of limits needed? The line limit and byte limit each address different concerns:

- **Line limit (200 lines)**: Protects the Agent's comprehension efficiency. Even if each line is short, an index of more than 200 lines requires the Agent to spend more tokens understanding and filtering. The cap keeps the index a "quick browse" object instead of a document to read closely.
- **Byte limit (25KB)**: Protects the context budget. A single memory's index entry may contain a long description (approaching the 150-character limit), and 200 such entries could reach 30KB, putting pressure on the context window. The byte limit provides a hard cost ceiling.

The order of the two layers also matters -- truncation by lines first, then by bytes. When there are fewer memory entries but longer descriptions, the byte limit triggers first; when there are more memory entries but shorter descriptions, the line limit triggers first. In either case, there is a corresponding protection mechanism.

```ill
ch06-memory-funnel
```

### 6.2.3 Directory Structure of Memory Files

Functions in the path resolution module determine the storage path for memory files. The default path is:

```
~/.claude/projects/<sanitized-git-root>/memory/
```

Path resolution priority:

1. `CLAUDE_COWORK_MEMORY_PATH_OVERRIDE` environment variable (full path override for Cowork mode)
2. `autoMemoryDirectory` setting (only policySettings/localSettings/userSettings, **excluding projectSettings**)
3. Default `<memoryBase>/projects/<sanitized-git-root>/memory/`

projectSettings is once again excluded for the same reason as in the previous chapter -- preventing a malicious repository from redirecting writes to sensitive directories via `autoMemoryDirectory: "~/.ssh"`. The path validation function checks this strictly: rejecting relative paths, root paths, Windows drive letter roots, UNC paths, and null byte injection.

**Complete Defense Lines of Path Security Validation**

The path validation function's rejection list reveals the various path manipulation techniques an attacker might attempt:

| Attack Technique | Example | Defense Method |
|-----------------|---------|---------------|
| Relative path | `../../etc/passwd` | Reject non-absolute paths |
| Root path | `/` | Reject root paths |
| Windows drive letter root | `C:\` | Reject drive letter root paths |
| UNC path | `\\server\share` | Reject UNC paths |
| Null byte injection | `foo\0.txt` | Reject paths containing null bytes |
| Outside user directory | `/tmp/mem` | Reject paths not under allowed base directories |

These checks stack on top of each other to form a defense-in-depth system. Even if one check slips through, the next check can still block the attack.

> **Cross-Reference:** The projectSettings exclusion mechanism is consistent with the security boundary design in Chapter 5 (Settings and Configuration). Memory path validation is a specific application scenario of the configuration system's security policy.

## 6.3 Automatic Memory Extraction

### 6.3.1 Background Extraction Based on the Fork Pattern

The core of the memory extraction system resides in the memory extraction module. It is not executed directly by the main conversation but runs in the background through `runForkedAgent` -- a "perfect fork" pattern.

The so-called "perfect fork" means the background Agent shares the exact same system prompt and tool set as the main conversation:

- The background Agent has the same context understanding capabilities as the main Agent
- The background Agent uses the same tool set but with stricter permission restrictions
- **The main conversation and the background Agent share the prompt cache**

Extraction triggers at the end of each complete query loop (when the model produces a final response with no tool calls).

```mermaid
flowchart TD
    start["Conversation Ends"] --> check_flag{"Did the main Agent<br/>actively save a memory?"}
    check_flag -->|Yes| skip["Skip Extraction<br/>(Mutex Mechanism)"]
    check_flag -->|No| throttle{"Has the throttle counter<br/>reached the threshold?"}
    throttle -->|No| wait["Wait for next conversation"]
    throttle -->|Yes| fork["Fork Background Agent"]
    fork --> shared["Share System Prompt + Tool List<br/>(Cache-Aware Design)"]
    shared --> extract["Background Agent Analyzes Conversation<br/>Extracts Valuable Memories"]
    extract --> save["Write Memory Files<br/>(Memory Directory Only)"]
    save --> update_index["Update MEMORY.md Index"]

    trailing{"Is there pending<br/>trailing context?"}
    update_index --> trailing
    trailing -->|Yes| trail_extract["Trailing Extraction<br/>(Skip Throttle Counter)"]
    trailing -->|No| done["Complete"]
    trail_extract --> done

    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef decision fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#e65100
    classDef skip_node fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px,color:#b71c1c
    classDef success fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#1b5e20

    class fork,shared,extract,save,update_index process
    class check_flag,throttle,trailing decision
    class skip skip_node
    class done,wait success
```

**Why not extract memory directly in the main conversation?**

This design choice involves trade-offs across multiple dimensions:

```
Direct extraction in main conversation:
  Pros -> Simple implementation, no inter-process communication overhead
  Cons -> Increases user wait time, consumes main conversation's token budget,
         extraction logic failures may affect main conversation stability

Fork-based background extraction:
  Pros -> Does not affect user experience, independent token budget,
         failures do not affect main conversation, can share cache to reduce costs
  Cons -> Higher implementation complexity, requires mutex mechanism to prevent duplicate writes
```

User experience is the most critical consideration. At the end of a long conversation, the user expects to see the final result immediately and start the next interaction. If they also have to wait for memory extraction to complete, even just a few seconds of delay, the cumulative impact would severely degrade interaction fluency.

### 6.3.2 Mutex Mechanism

The mutex check function in the memory extraction module is straightforward: if the main Agent has already written a memory file during the current conversation, the system skips the background extraction entirely. The main conversation's system prompt already includes complete memory saving instructions. When the main Agent actively saves a memory, the forked background Agent detects this fact and skips the current extraction -- the two are **mutually exclusive**, preventing duplicate writes.

**The mutex mechanism is an "eventual consistency" design.**

```mermaid
sequenceDiagram
    participant MainConversation as Main Conversation
    participant MemoryFlag as Memory Flag
    participant BackgroundAgent as Background Agent

    Note over MainConversation: Case 1: Main Agent actively saves memory
    MainConversation->>MainConversation: T1: Conversation starts
    MainConversation->>MemoryFlag: T3: Main Agent saves feedback memory
    Note over MemoryFlag: Write flag is set
    MainConversation->>BackgroundAgent: T4: Conversation ends, triggers background extraction
    BackgroundAgent->>MemoryFlag: T5: Detects write flag
    Note over BackgroundAgent: Skip extraction (mutex takes effect)

    Note over MainConversation,BackgroundAgent: ---
    Note over MainConversation: Case 2: No active memory save
    MainConversation->>MainConversation: T1: Conversation starts
    MainConversation->>BackgroundAgent: T2: Conversation ends, no active save
    BackgroundAgent->>BackgroundAgent: T4: Analyzes conversation, extracts 2 memories
    Note over BackgroundAgent: Normal extraction
```

The advantage of this design is avoiding redundant memories caused by "duplicate extraction." Imagine: if the main Agent saves "user prefers pnpm," and the background Agent independently analyzes and determines "user prefers pnpm," the same information produces two memories, wasting storage space and increasing the burden of future filtering.

### 6.3.3 Tool Permission Allowlist

The `createAutoMemCanUseTool` function strictly controls the background Agent's tool permissions:

| Tool | Permission | Design Rationale |
|------|-----------|-----------------|
| Read / Grep / Glob | Unrestricted (read-only) | Need to read code to understand conversation context |
| Bash | Read-only commands only (ls, find, grep, etc.) | Need to view file state but cannot execute modification commands |
| Edit / Write | Paths within memory directory only | Need to write memory files but cannot modify project code |
| REPL | Allowed (but internal calls are subject to above restrictions) | May need to execute code to verify information |
| All other tools | Denied | Background Agent should not trigger side effects like network requests |

This design gives the background Agent sufficient read capabilities to understand conversation content, while restricting write capabilities to the memory directory -- it cannot modify project code or execute dangerous commands.

**The Principle of Least Privilege in Practice**

The tool permission allowlist follows the Principle of Least Privilege: the background Agent only gets the minimum set of permissions its job needs. Specifically:

- **Why is Glob allowed?** The background Agent may need to discover relevant files to verify memory accuracy (e.g., whether a file mentioned in memory still exists)
- **Why is Bash restricted to read-only?** To prevent the background Agent from executing destructive commands (like `rm -rf`) without the user's knowledge
- **Why are Edit/Write restricted to the memory directory?** To prevent the background Agent from modifying project code (which could change build results or introduce bugs)

### 6.3.4 Throttling and Coordination

Extraction does not run after every conversation. The system throttles by counting rounds: extraction runs only after several more rounds, with the threshold set through feature flags.

Additionally, there is a **trailing extraction** mechanism to handle concurrency issues. When an extraction is in progress and another conversation completes, the system stages the new context. After the current extraction completes, a trailing extraction runs using the latest staged context. Trailing extraction bypasses the throttle counter -- it handles already-completed work, and throttling should not delay it.

**Timing Diagram of the Trailing Extraction Mechanism**

```mermaid
sequenceDiagram
    participant ConvA as Conversation A
    participant ExtrA as Extraction A
    participant ConvB as Conversation B
    participant TrailB as Trailing Extraction B
    participant ConvC as Conversation C
    participant ExtrC as Extraction C

    ConvA->>ExtrA: Conversation completes, triggers extraction
    Note over ExtrA: Normal extraction in progress...
    ConvB->>ConvB: Conversation completes, stages context
    Note over ConvB: Waiting for Extraction A to complete...
    ExtrA-->>TrailB: Extraction completes
    TrailB->>TrailB: Uses Conversation B context<br/>Skips throttle counter
    ConvC->>ExtrC: Conversation completes, triggers extraction
```

Without the trailing extraction mechanism, Conversation B might never get an extraction pass -- the next extraction uses Conversation C's context, so the unique, memory-worthy information in B would slip through.

**Design Considerations for the Throttle Counter**

The throttle counter design reflects a cost-benefit analysis: each memory extraction requires a complete API call (even with cache sharing, output token costs still apply). For frequent short conversations (like simple Q&A), the cost of memory extraction may exceed its value. The throttling mechanism ensures that extraction fires only after enough conversation rounds accumulate, improving the "information density" of each extraction.

## 6.4 Cache-Aware Memory Architecture

### 6.4.1 Prompt Cache Sharing

In LLM APIs, prompt cache is an important cost optimization mechanism -- if two requests share the same prefix, the API can reuse the already-computed KV cache, significantly reducing latency and cost.

Claude Code's forked Agent pattern uses the `CacheSafeParams` type to share the cache. The parameter extraction function extracts shared parameters from the context, including the system prompt, user context, system context, tool usage context, and message history.

The background extraction Agent's API request prefix is identical to the main conversation's, so the provider hits the cached prefix instead of recomputing it -- a substantial saving in tokens over a typical session.

**Cost Impact of Cache Sharing -- A Simplified Calculation**

```
Assumptions:
- System prompt + tool definitions ≈ 30,000 tokens
- Message history ≈ 50,000 tokens (a medium-length conversation)
- Cached input price = $0.30 / MTok (a hit is billed at 10% of the input price)
- Standard input price = $3.00 / MTok (no cache)

Without cache sharing:
  Extraction Agent resends 80,000 tokens → $0.24

With cache sharing:
  Extraction Agent reuses cache → $0.024 (pays only cache read fees)

Savings: 90%
```

In scenarios with frequent Agent usage (dozens of conversations per day), the cost savings from cache sharing are substantial.

### 6.4.2 Tool List Consistency Requirement

Cache sharing has an implicit constraint: **the tool list is part of the API cache key.** If the forked Agent uses a different tool set from the main Agent, the cache cannot be hit. This is why tool permission filtering uses the `canUseTool` callback rather than a different tool list -- the tool list remains consistent, with filtering applied only at execution time.

**This design choice demonstrates an important architectural principle: consistent interface, variable behavior.**

```mermaid
flowchart LR
    subgraph ApproachA["Approach A (Not Recommended): Different Tool Lists"]
        ma["Main Agent Tool Set<br/>Read, Write, Edit, Bash, Grep, Glob..."]
        ea["Extraction Agent Tool Set<br/>Read, Grep, Glob, MemoryWrite"]
        ma -.->|"Different cache key"| x["Cache Miss<br/>Increased Cost"]
        ea -.-> x
    end

    subgraph ApproachB["Approach B (Recommended): Same Tool List, Different Permissions"]
        mb["Main Agent Tool Set<br/>Read, Write, Edit, Bash, Grep, Glob..."]
        eb["Extraction Agent Tool Set<br/>Read, Write, Edit, Bash, Grep, Glob..."]
        perm["Extraction Agent Permissions<br/>canUseTool Callback Filter"]
        mb -.->|"Same cache key"| check["Cache Hit<br/>Cost Savings"]
        eb -.-> check
        eb --- perm
    end

    classDef agent fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef bad fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px,color:#b71c1c
    classDef good fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef perm_node fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#e65100

    class ma,mb,eb agent
    class x bad
    class check good
    class perm perm_node
```

The same trade-off holds outside the memory system, as guidance for designing high-performance Agent architectures: keep cache-related interface parameters (tool lists, system prompt prefixes) unchanged as much as possible, and place differentiation logic in runtime behavioral control.

### 6.4.3 Memory Lifecycle

The path resolution module defines the decision chain for enabling memory:

1. `CLAUDE_CODE_DISABLE_AUTO_MEMORY` environment variable (1/true -> disabled)
2. `--bare` (SIMPLE mode) -> disabled
3. CCR without persistent storage (no `CLAUDE_CODE_REMOTE_MEMORY_DIR`) -> disabled
4. `autoMemoryEnabled` field in `settings.json`
5. Default: enabled

Background extraction also needs to pass through a GrowthBook feature gate. This is dual-layer control: a compile-time feature flag plus a runtime GrowthBook experiment.

**Memory Lifecycle State Machine**

```mermaid
stateDiagram-v2
    [*] --> MemoryDoesNotExist
    MemoryDoesNotExist --> MemoryCreated: Agent saves memory / Background extraction
    MemoryCreated --> MemoryActive: Loaded in subsequent conversation
    Note right of MemoryCreated: MEMORY.md index updated
    MemoryActive --> MemoryInvalidatedDeleted: Memory content outdated / Manual deletion
    Note right of MemoryActive: Agent references in conversation
    MemoryInvalidatedDeleted --> [*]
    Note right of MemoryInvalidatedDeleted: MEMORY.md index entry removed
```

Memory never expires on its own. Claude Code does not implement an automatic memory expiration mechanism -- once you save a memory, it stays until someone deletes it by hand or a later memory overrides it. So the quality of the store rests on two habits: the Agent declining to save what is not worth saving, and the user pruning what is there.

### 6.4.4 Memory Reading and Validation

The memory type validation module defines the core principle for memory reading: **memory is a point-in-time snapshot, not a current fact.**

```
"Memory says X exists" does not mean "X currently exists."
```

Specific validation rules:

- If the memory names a file path: check if the file exists
- If the memory names a function or flag: grep to find it
- If the user is about to act on your recommendation (rather than asking about history): validate first

The rule behind these checks: **memory is a trusted clue, not a trusted conclusion.** It guides the Agent on where to find information but does not replace the Agent's independent verification of the current state.

**Design Philosophy of Validation Levels**

```mermaid
graph TD
    subgraph TrustLevels["Memory Trust Levels (Low to High)"]
        L0["Level 0: No Trust<br/>Re-acquire all information"]
        L1["Level 1: Trust as Clue<br/>Memory indicates direction, independently verify facts<br/>✓ Claude Code adopts this level"]
        L2["Level 2: Trust as Fact<br/>Memory is the current truth"]
    end

    L0 --> L1 --> L2

    classDef low fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px,color:#b71c1c
    classDef mid fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    classDef high fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px,color:#b71c1c

    class L0 low
    class L1 mid
    class L2 high
```

Claude Code choosing Level 1 is the pragmatic middle ground. Level 0 is too conservative -- if you completely distrust memories, the memory system loses its value. Level 2 is too aggressive -- the code repository's state may have changed, and outdated memories can mislead decisions. Level 1 lets memories serve as "indices" and "guides" while maintaining independent verification of the current state.

This principle is particularly important in the following scenarios:

1. **Code references**: The memory says "user authentication is in `src/auth/handler.ts`," but a refactoring may have moved the file. The Agent should check if the file exists before directly referencing it.
2. **Dependency versions**: The memory says "the project uses React 18," but the team may have upgraded to React 19. The Agent should read `package.json` to confirm the current version.
3. **Decision rationale**: The memory says "we chose PostgreSQL because we needed complex queries," and this decision rationale is unlikely to become outdated -- it explains "why" rather than "what," so you can trust it directly.

> **Cross-Reference:** The "clue not conclusion" principle for memory validation is closely related to the compression strategy in Chapter 7 (Context Management). Compressed summaries follow the same principle -- summaries are historical clues, and the Agent should verify the current state mentioned in summaries when necessary.

---

## Practical Exercises

### Exercise 1: Memory Type Classification

Which memory type should you save the following information as?

1. "Our team uses the Linear project 'BACKEND' to track backend bugs"
2. "The user is a junior developer, using TypeScript for the first time"
3. "Integration tests must use a real database, no mocking -- last time mocking caused a production incident"
4. "The authentication middleware rewrite was due to legal compliance requirements, not technical debt"
5. "The API documentation Swagger UI is at http://localhost:3000/api-docs"
6. "Every time you create a new component, write tests before implementation"

**Reference Answers:**
1. `reference` -- external system pointer
2. `user` -- user profile
3. `feedback` -- behavioral directive (includes Why: production incident)
4. `project` -- project decision (includes Why: legal compliance)
5. `reference` -- external reference (development environment URL)
6. `feedback` -- behavioral directive (includes an explicit rule and an implied reason)

### Exercise 2: Frontmatter Writing

Write the Frontmatter and content for a memory file for the following scenario:

Scenario: The user says "from now on, run `npm run lint` before every code commit; last time someone committed unlinted code and CI failed for a whole day."

**Reference Answer:**

```markdown
---
name: pre-commit-lint-requirement
description: Must run npm run lint before every commit; CI failed for a full day due to unlinted code
type: feedback
---

**Rule**: Run `npm run lint` before every code commit.

**Why**: A previous commit with unlinted code caused CI to fail for an entire day, blocking the team.

**How to apply**: Before using git commit, always run `npm run lint` first and fix any errors. This applies to all files changed in the commit, not just new files.
```

**Extended Reflection:** If the user says a week later "the pre-commit hook now covers the lint rules, no need to run manually anymore," how should the Agent handle this memory? Should it delete it or update it?

### Exercise 3: Cache-Aware Architecture Analysis

Suppose you want to add a new tool `MemorySearch` (for semantic search of memory files) to the forked Agent. Which of the following two approaches is better?

- Approach A: Add `MemorySearch` to the forked Agent's tool list, replacing `Grep`
- Approach B: Keep the tool list unchanged, restrict Grep to only search the memory directory through the `canUseTool` permission callback

**Reference Answer:** Approach B is better. Approach A changes the tool list, resulting in a different API cache key and preventing sharing of the main conversation's prompt cache. Approach B maintains tool list consistency, with permissions filtered at execution time rather than definition time, preserving cache sharing capability.

### Exercise 4: Memory Management Strategy Design

You maintain 5 projects simultaneously, each with 20-30 memories in its memory directory. Design a memory management strategy that addresses the following issues:

- How to avoid cross-project memory confusion?
- How to handle outdated memories?
- How to ensure the MEMORY.md index stays within limits?

**Reference Answer Hints:**
- Memories naturally stay isolated by project (paths follow the Git root directory); only user-type memories cross projects
- Regularly review the memory directory and delete low-value memories that fail the "would behavior change if deleted" test
- Control the description length of each memory entry, and periodically merge memory entries on related topics

---

## Key Takeaways

1. **Closed Four-Type System**: user, feedback, project, reference -- only save information you cannot derive from code, excluding derivable content like code patterns and Git history. The closed type system enables efficient consistent reasoning.
2. **Dual Capacity Protection**: The MEMORY.md index is limited to 200 lines / 25KB, with line truncation applied first then byte truncation, ensuring the index always remains a "quick browse" tool rather than a "deep reading" document.
3. **Fork Pattern**: The background Agent perfectly forks the main conversation, sharing prompt cache and limiting write permissions through the `canUseTool` allowlist. It does not affect user experience and has an independent token budget.
4. **Mutex Extraction**: Memory writes by the main Agent and the background Agent are mutually exclusive -- when the main Agent writes, the background skips, avoiding redundant memories from duplicate extraction.
5. **Cache Awareness**: Tool list consistency is a prerequisite for cache sharing. Permission filtering uses runtime callbacks rather than compile-time different tool lists. Consistent interface, variable behavior.
6. **Validation First**: Memory is a snapshot, not a fact; verify the current state before making recommendations. "Clue not conclusion" is the correct mindset for using memory.
7. **Least Privilege**: The background Agent's tool permission allowlist strictly limits write capabilities, embodying the Principle of Least Privilege.
8. **Trailing Extraction**: The trailing extraction mechanism ensures that during concurrent extraction, no conversation misses its memory extraction opportunity.
