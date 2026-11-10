---
name: aurora-review
description: Review an Aurora fixture by its rules, retain input hashes, and distinguish document links from example URLs.
---

# Review an Aurora project

Use this skill for the book's Aurora project or a project explicitly adopting its rules.
Ask for the project directory if it is absent from the task. Read rules.json and the
current docs/index.md before deciding the scope. The rules control archive inclusion.

Run the book repository's hermes/examples/aurora_lab.py check with that directory.
Exit code 0 means this limited checker found no broken local links; exit code 1 means
reviewable issues; exit code 2 means execution or configuration failed. A previous
reports/latest.json cannot prove that the latest command completed successfully.

Check each issue against its source file and line. The checker handles simple inline
Markdown links and fences, not every CommonMark form or remote URL availability.
For example-url observations, explain whether the URL is an intentional placeholder;
do not reclassify every example URL as a dead production link.

Keep the input_digest, rules hash, changed filenames, actual command, and result.
After an authorized edit, rerun the checker. If the inputs changed meanwhile, discard
old file-level conclusions and inspect the current content before editing further.

Save a durable project fact only when it is confirmed and likely useful next time.
Keep the method here, the current project scope in rules.json, and this run's evidence
in its report. Do not upload files or send messages as part of this skill.
