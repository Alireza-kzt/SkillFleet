---
name: fleet-rtl
description: Design and verify Persian and mixed RTL/LTR web, Flutter and document interfaces. Use for bidirectional text, typography, number/date formatting, directional icons, tables and responsive Persian layouts.
---

# Persian and RTL

1. Identify the framework, direction model, locale and existing font assets. Prefer the project's licensed font and typography scale.
2. Use semantic direction and logical spacing/alignment. Mirror directional navigation when appropriate; keep logos, media controls, plots and universal icons semantically correct.
3. Isolate URLs, emails, code, telephone numbers and English identifiers with bidi-aware elements or framework direction controls. Avoid manual reversal and hidden marks used as a blanket fix.
4. Verify parentheses and punctuation around mixed Persian/English phrases. Check table headers, footnotes, placeholders, validation text and multiline labels.
5. Choose number and date formatting by meaning and existing conventions. Do not change identifiers, API values or machine-readable timestamps to localized strings.
6. Exercise narrow screens, large text, zoom, wrapping, keyboard navigation, focus, screen-reader labels and loading/error states.
7. Inspect rendered output with real Persian strings, long names and mixed-direction examples. A CSS direction declaration or successful build is not visual verification.
