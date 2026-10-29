# Review

## Creative decisions

- Kept the existing editorial course style, but changed the dense eight-step list into four actions: find the problem, understand the need, build the solution, and deliver it.
- Timed each action to the narration, then revealed Stage 2 and Stage 3 only when the voice reaches them.
- Made the opening headline visible on frame 0 so the thumbnail communicates the premise immediately.
- Rejected adding decorative motion; movement now indicates teaching order.

## Verification

- `hyperframes check` passes with zero errors and zero warnings across runtime, layout, contrast, craft, and audio.
- A dense transition-boundary pass sampled 1,238 timestamps; it exposed caption collisions in the definition and roadmap scenes, which were moved above the caption band.
- Reviewed snapshots at the opening, definition steps, all four Stage 1 actions, Stage 2, Stage 3, and the final summary.
- Audio presence and timing were measured, not listened to.

## Remaining opportunity

The definition scene is still the most presentation-like shot. A later pass could replace its three text rows with one worked prompt traveling through “request → result → revision,” without changing the narration.

## Delivery verification — 2026-10-29

- Rendered `renders/llm101-film_2026-10-29_delivery.mp4` at delivery quality.
- Verified H.264 1920×1080 at 30 fps, AAC stereo at 48 kHz, duration 215.5 s, size 12,780,214 bytes.
- Render/reference comparisons at 0, 58, 126, 171, and 215 s match visually.
- Measured loudness is about −18.8 LUFS with a −1.5 dBTP peak and no clipping.

## Second clarity pass — 2026-10-29

- Replaced the abstract three-row definition with one worked example: request a hydration reminder, watch the AI stream its interpretation, inspect the prototype, then request a revision.
- Reused the deterministic cadence principles from the installed typed-prompt and streaming-text components.
- Removed a redundant process strip after review; the prompt, result, and revision already show the loop more clearly.
- Rechecked the changed scene at eight narration moments: zero runtime, layout, contrast, craft, or audio findings.
- Delivered as `renders/llm101-film_2026-10-29_v2_delivery.mp4`: 1920×1080, 30 fps, 215.5 s, H.264 video with 48 kHz stereo AAC.
- Render/reference comparisons at 22, 28, 36, 44, 126, and 215 s match visually. The original delivery MP4 remains available.

## Purposeful play pass — 2026-10-29

- Added one complete UI reward: pointer arrival, button compression, two restrained click rings, 3/8 → 4/8 count change, progress growth, water droplets, and a drawn success check.
- Based the interaction on the installed press-ripple and success-check component contracts, then restyled it for the existing course UI.
- The action plays once in about 1.3 seconds and ends completely still; no breathing, pulsing, or decorative loop was added.
- Full-film check and a 12-frame action strip pass with zero errors and zero warnings.
- This pass has not replaced the v2 delivery MP4 yet.

## Interactive reward pass — 2026-10-29

- Turned the hydration prototype into a real one-shot interaction: pointer arrival, press compression, restrained ripple, count and progress update, water-drop reward, and a drawn success mark.
- Adapted the installed press-ripple and success-check motion contracts to the existing green course UI.
- The interaction has a clear cause and result, finishes in about 1.3 seconds, and holds still afterward.
- Full-film check and a 12-frame motion strip pass with zero errors and zero warnings.
- This pass has not replaced the v2 delivery MP4 yet.

## Playable-example pass — 2026-10-29

- Replaced the static snake lesson cards with an actual game board: the snake follows an authored grid route, eats 春 / 风 / 来, updates the collection score, and builds the poem line in the same order.
- Adapted the deterministic grid-and-trail principles from the installed ascii-trail-reveal component; the motion is finite and has no gameplay loop.
- Kept the teaching conclusion on the left so the example demonstrates the point instead of becoming a disconnected game clip.
- Full-film check and a 16-frame gameplay strip pass with zero errors and zero warnings.
- This pass has not replaced the v2 delivery MP4 yet.

## Poetry-snake showcase pass — 2026-10-29

- Rebuilt the first-practice scene around a visible game board rather than explanatory cards.
- The snake follows a finite authored route, eats 春 / 风 / 来, updates its score, and assembles the poem line in the same order.
- Adapted the deterministic grid-and-trail principle from the installed ascii-trail-reveal component while keeping the course lesson visible beside the game.
- Full-film check and a 16-frame gameplay strip pass with zero errors and zero warnings.
- This pass has not replaced the v2 delivery MP4 yet.

## Product-demo polish pass — 2026-10-29

- Rebuilt the tools scene as one continuous device: a web chat receives the request, the same frame becomes a local AI IDE, files and code appear, then the terminal runs successfully.
- Rebuilt screenshot reconstruction as a persistent before/after comparison: the divider wipes the AI reconstruction over the muted reference while layout, style, and acceptance criteria appear beside it.
- Adapted the installed browser-device-stage, code-terminal-run, and comparison-split contracts to the course's existing visual language.
- Added narrowly scoped layout-intent markers only where the after layer intentionally covers the reference layer.
- Full-film check and two 14-frame motion strips pass with zero errors and zero warnings.
- This pass has not replaced the v2 delivery MP4 yet.

## Unified cover and title pass — 2026-10-29

- Unified the course identity as `VIBE CODING 101` across the static cover, opening title, and closing title.
- Reframed the promise as “不会写代码，也能做软件” with the concrete subtitle “从一句需求，到第一个可用作品.”
- Added an editable title-card variable so the opener states “零基础 · 实战入门 · 可跟做,” while the closer summarizes the one-change-at-a-time workflow.
- Full-film check passes with zero errors and zero warnings. Reviewed frames 0, 2.5, 190, 214, and the end hold.
- Delivered the complete current source as `renders/llm101-film_2026-10-29_v3_delivery.mp4` and copied the identical bytes to `renders/llm101-film_latest.mp4` for an unambiguous current handoff.
- Verified H.264 1920×1080 at 30 fps, AAC stereo at 48 kHz, duration 215.5 s, size 14,828,340 bytes.
- Render/reference comparisons at 0, 28, 58, 83, 103, 136, 171, 190, and 215 s match visually.
- Measured loudness is −18.7 LUFS with a −1.5 dBTP true peak and zero clipped samples.
- Moved the pre-v3 MP4 files and legacy PNG cover into `renders/archive/`; the renders root now contains only the v3 delivery, the identical `latest` handoff, and the current WebP cover.
