---
name: fleet-documents
description: Create and review Word, PowerPoint, spreadsheets and PDF deliverables using inspect-render-verify workflows, native editable formats, correct formulas and readable Persian/English layouts.
---

# Document production

1. Inspect the current file or template and preserve its structure, styles, formulas and identity. Choose the native editable format the user requested.
2. Use an existing dedicated authoring capability when available. Otherwise use established libraries such as python-docx, python-pptx, openpyxl or a suitable PDF/LaTeX tool; install dependencies only through the project's normal workflow.
3. Keep facts, calculations and citations traceable. For spreadsheets, use formulas for derived values, preserve types and recalculate using a compatible engine when available. Reading cached values does not prove formulas were evaluated.
4. Build hierarchy with styles and semantic headings. Keep tables readable, labels aligned and units explicit. Use chart data from a verified source.
5. For Persian, verify the actual font, paragraph/table direction, mixed punctuation, text shaping and page/slide reading order.
6. Render to PDF or images using a compatible installed renderer. Inspect every page/slide or representative views of repetitive sheets, including charts and print areas.
7. Fix overflow, clipping, isolated headings, unreadable figures, broken glyphs and unnecessary blank pages. Re-render after a layout change.
8. Validate the artifact opens and its formulas, links or media work. Report unavailable renderers or recalculation honestly; do not assert visual verification from XML inspection.
9. Deliver the final artifact with a clear filename and preserve the source file when requested. Do not treat a chat preview as proof the native file was saved.
