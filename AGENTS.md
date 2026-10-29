# Repository Guidelines

## Project Structure

`book/` contains the assembled Markdown book and its cover. `videos/landscape/` and `videos/vertical/` are editable HyperFrames projects; each uses `index.html` for the root timeline, `compositions/` for scenes, and `assets/` for audio. Final MP4 and WebP files live in `deliverables/`. Repository validation is implemented in `scripts/validate.mjs`.

## Development Commands

- `npm test`: validate the complete repository and final media metadata.
- `npm run validate`: equivalent explicit validation command.
- `cd videos/landscape && npm run dev`: open the landscape preview.
- `cd videos/vertical && npm run dev`: open the portrait preview.
- `npm run check` inside either video directory: run HyperFrames lint, runtime, layout, motion, contrast, and audio checks.

## Style and Naming

Use two-space indentation for HTML, CSS, JavaScript, JSON, and YAML. Keep composition filenames and element IDs in kebab-case. HyperFrames animation must be deterministic: do not use timers, unseeded randomness, or infinite loops. Titles should remain concise and phone-readable; purposeful animation should demonstrate cause, progress, or completion.

## Verification

Run `npm test` before committing. Video changes additionally require the project-level `npm run check` and snapshots at edited timestamps. Do not replace final media without validating resolution, frame rate, duration, audio, and representative rendered frames.

## Commits and Pull Requests

Use Conventional Commit subjects, such as `feat(video): improve roadmap handoff` or `docs(book): clarify iteration workflow`. Keep commits focused. Pull requests should summarize affected book/video sections, list validation commands, and attach screenshots for visual changes.

## Generated and Sensitive Files

Do not commit `.hyperframes/`, caches, preview state, archived renders, credentials, or machine-specific paths. Keep only current delivery files under `deliverables/`.
