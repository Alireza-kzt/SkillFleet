---
name: fleet-video
description: Create clean product-demo or educational videos with deliberate storyboards, restrained motion, kinetic typography and deterministic Remotion compositions. Use for videos, demo playback, explainers and requested video exports.
---

# Video storytelling

1. Extract the audience, message, duration, aspect ratio, language and requested output. Reuse brand assets and fonts. If unspecified, choose a short storyboard and state the assumption.
2. Write a beat list: time interval, one message, visual subject, transition and audio. Start with the user's problem, show one meaningful transformation, finish with the value.
3. Use a restrained visual system: readable typography, generous spacing, a small palette and purposeful motion. Avoid crowded scenes, fake product claims and arbitrary decorative effects.
4. For Remotion, use useCurrentFrame, useVideoConfig, interpolate, spring and Sequence for deterministic frame-based motion. Do not use wall-clock timers or CSS animations for render-critical timing.
5. Keep reusable visual primitives separate from composition timing. Preload required fonts/media; handle layout and safe areas in the target aspect ratio.
6. For Persian, verify glyph shaping, RTL/LTR isolation, punctuation, captions and font embedding. For narration, synchronize visible beats with the actual recorded duration.
7. Preview representative frames, scene boundaries and the full timeline. Check clipping, contrast, continuity, audio levels, captions, final duration and the requested codec/resolution.
8. Export only when requested. Verify the produced file with a media inspector and sample rendered frames; do not call a browser animation an exported video.
9. Consult current official Remotion documentation for APIs and current library license terms before adopting a runtime. For mathematical explanations, choose Manim when deterministic geometry and formula transitions fit better.

Official references: https://www.remotion.dev/docs/ and https://docs.manim.community/
This is original workflow guidance. It does not bundle the Remotion runtime or the separately published Remotion skills.
