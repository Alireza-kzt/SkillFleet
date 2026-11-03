---
name: fleet-context
description: Reduce unnecessary context and token use during repository work, investigations and long tasks through focused retrieval, bounded output and concise evidence-backed handoffs. Preserve technical precision and the user's language.
---

# Context efficiency

- Start with filenames, project instructions and the relevant module. Use rg to find definitions and callers; read bounded ranges around real matches. Avoid dumping the repository.
- Load only the skill needed for the current task, then only its relevant reference. Keep competing full workflow frameworks out of the same task.
- Batch independent reads. Reuse a verified fact until a mutation or new evidence makes it stale. Keep dependent writes and verification sequential.
- Prefer deterministic scripts for repetitive transformations and calculations. Inspect a summary plus failures instead of thousands of successful lines.
- For a long task, record only decisions, evidence locations, exact commands, unresolved issues and next actions in a project-local working note. Follow existing documentation conventions instead of generating a documentation tree.
- Make a handoff reproducible: goal; current branch and commit; changed paths; checks actually run; relevant artifact paths; remaining action. Exclude credentials and private environment dumps.
- Keep user-facing explanations clear and concise. Never abbreviate identifiers, omit units or assumptions, compress code into unreadable forms, or rewrite a scientific argument merely to save tokens.
- Use measured token or cost data only when the environment supplies it. Do not claim a fixed percentage saving from prose style or from file-based planning.
