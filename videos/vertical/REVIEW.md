# Review

## Creative decisions

- Put the full hook on frame 0: “不会写代码，也能做软件”.
- Rewrote the definition as a concrete loop: “你说需求 → AI 做原型 → 你看结果 → 继续改”.
- Rebuilt the three-stage map as large vertical milestone cards and moved the call to action into the platform-safe reading area.
- Used staggered reveals to show learning order instead of revealing the whole roadmap at once.

## Verification

- `hyperframes check` passes with zero errors and zero warnings across runtime, layout, contrast, craft, and audio.
- Reviewed frame 0, the definition, each roadmap milestone, and the final call to action at phone size.
- Audio presence and timing were measured, not listened to.

## Remaining opportunity

The key ideas are readable without sound, but the full narration is not word-for-word captioned. A later accessibility pass could add concise burned-in captions while keeping the current uncluttered layout.

## Delivery verification — 2026-10-29

- Rendered `renders/llm101-reel_2026-10-29_delivery.mp4` at delivery quality.
- Verified H.264 1080×1920 at 30 fps, AAC stereo at 48 kHz, duration 39.5 s, size 1,889,385 bytes.
- Render/reference comparisons at 0, 11.8, 30, and 39 s match visually.
- Measured loudness is about −13.7 LUFS with a −1.5 dBTP peak and no clipping.

## Caption accessibility pass — 2026-10-29

- Added five concise beat-level captions for the definition and the three practical steps.
- Used the minimal weight-shift principle: stable dark caption cards, one green keyword, and no per-character bounce.
- Moved the practical-step cards upward so captions remain inside the portrait platform-safe reading band.
- Local word-level transcription was unavailable, so these are explicitly editorial summaries aligned to authored scene beats, not claimed word-for-word subtitles.
- Full transition-boundary check passes with zero errors and zero warnings.
- Delivered as `renders/llm101-reel_2026-10-29_v2_delivery.mp4`: 1080×1920, 30 fps, 39.5 s, H.264 video with 48 kHz stereo AAC.
- Render/reference comparisons at 4.8, 9, 14.5, 19.5, 24.5, and 35.5 s match visually. The original delivery MP4 remains available.

## Playful learning-path pass — 2026-10-29

- Added a small pixel snake that follows a three-stop milestone rail, lighting each node as the corresponding practical step arrives.
- The snake briefly eats an apple at step three, foreshadowing the next episode without covering instructional text.
- Based the travel law on the installed offset-path-traveler component: authored stops, deterministic transforms, and no free-running loop.
- Full transition-boundary check and a 16-frame motion strip pass with zero errors and zero warnings.
- This pass has not replaced the v2 delivery MP4 yet.

## Snake milestone pass — 2026-10-29

- Added a compact pixel snake beside the three practical-step cards; it travels once, stops at each milestone, and lights the corresponding node.
- The apple appears only at step three and disappears on contact, creating a payoff while foreshadowing the next episode.
- Adapted the installed offset-path-traveler motion law while keeping the character outside all reading zones.
- Full transition-boundary check and a 16-frame motion strip pass with zero errors and zero warnings.
- This pass has not replaced the v2 delivery MP4 yet.

## Map handoff pass — 2026-10-29

- Extended the snake's authored journey beyond the three practical steps and carried it upward into the S1 / S2 / S3 learning-map cards.
- Faded the old milestone rail before the carry, so the character is the only continuity object and no obsolete diagram remains on screen.
- The handoff removes the former low-energy gap at 27.5 s while keeping every map label readable.
- Full transition-boundary check and a 14-frame handoff strip pass with zero errors and zero warnings.
- This pass has not replaced the v2 delivery MP4 yet.

## Continuous-map handoff — 2026-10-29

- Carried the snake from the third practical step into the S1 / S2 / S3 roadmap rather than letting the film fall into an empty transition beat.
- The old step rail fades before the carry; the snake then stops beside each roadmap card and exits before the CTA.
- The change adds continuity without adding another caption or competing focal point.
- Full transition-boundary check and a 14-frame handoff strip pass with zero errors and zero warnings.
- This pass has not replaced the v2 delivery MP4 yet.

## Worked-example definition pass — 2026-10-29

- Replaced the definition-only card with a concrete miniature workflow: the prompt arrives in readable chunks, a snake prototype appears, the snake earns 10 points, and a precise revision changes its speed.
- Adapted the deterministic chunk cadence from the registry's `typed-prompt` component while keeping the final scene native to the existing course card.
- Added the matching book explanation: “you are the director, AI is the crew,” followed by a visible loop and a before/after revision example.
- Full video check passes with zero errors and zero warnings across lint, runtime, layout, motion, contrast, craft, and audio.
- Reviewed a 12-frame strip from 4.4–11.0 seconds plus the full beat and 360 px phone sheets. The prompt, prototype, result, and revision remain readable without sound.
- Audio presence and timing were measured, not listened to. The quietest visual beat remains the snake-to-roadmap handoff at 27.65 seconds; it was left unchanged because the moving snake is the intended continuity object.
- This pass has not replaced the v2 delivery MP4 yet.

## Unified cover and title pass — 2026-10-29

- Unified the portrait cover and true frame-zero title under `VIBE CODING 101 · EP.01`.
- Kept the main hook large and added the concrete value line “从一句需求，到第一个可用作品” directly inside the title block.
- Reduced title line height and moved the worked-example card down 25 px so the title, subtitle, and demo form three clean reading layers at phone size.
- Updated the standalone portrait cover to emphasize the worked examples and the “先做出来，再逐步升级” learning promise.
- Full-video check passes with zero errors and zero warnings. Reviewed frames 0, 3.5, 5, the 360 px opening sheet, and the end card.
- Delivered the complete current source as `renders/llm101-reel_2026-10-29_v3_delivery.mp4` and copied the identical bytes to `renders/llm101-reel_latest.mp4` for an unambiguous current handoff.
- Verified H.264 1080×1920 at 30 fps, AAC stereo at 48 kHz, duration 39.5 s, size 2,411,456 bytes.
- Render/reference comparisons at 0, 9, 27.65, and 39 s match visually.
- Measured loudness is −13.6 LUFS with a −1.5 dBTP true peak and zero clipped samples.
- Moved the pre-v3 MP4 files and legacy PNG cover into `renders/archive/`; the renders root now contains only the v3 delivery, the identical `latest` handoff, and the current WebP cover.
