---
name: fleet-engineering
description: Produce readable, minimal, maintainable code when implementing, refactoring or reviewing a feature. Apply practical module boundaries, simple interfaces and risk-based verification without speculative architecture.
---

# Engineering standards

1. Read project instructions, the touched code, its callers and existing tests before editing. State the observable outcome and the smallest affected boundary.
2. Reuse established libraries, helpers and conventions. Prefer the standard library for a small task. Add a dependency only when its maintenance cost is justified.
3. Use names from the domain. Keep control flow explicit. Explain surprising decisions and invariants; omit comments that translate the code into prose.
4. Keep UI, domain decisions and I/O at their existing boundaries. Extract a module when it hides a meaningful decision or dependency. Avoid an interface with one trivial implementation, a generic framework for one use case, and layers that only forward calls.
5. Preserve observable behavior outside the request. Check all callers when changing a contract. Handle expected failures at the boundary; never silently catch every exception.
6. Verify the actual risk: test important behavior, failure paths and regressions. Use existing suites and focused integration checks. Do not write tests that merely restate a constant, template or implementation.
7. Review the final diff for dead code, duplicate configuration, needless files, accidental reformatting, leaked credentials and unnecessary abstraction.
8. Report the changed behavior, completed verification and remaining limitations. Do not claim an unrun test passed.

Scale process to the task. A small edit needs a small change; a complex feature may need a written plan. Clean architecture is a tool for controlling dependencies, not a target directory tree. Never sacrifice clarity merely to reduce line count.
