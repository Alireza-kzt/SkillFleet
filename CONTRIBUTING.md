# Contributing

Keep SkillFleet small. Add capabilities because a real workflow needs them, not
because another abstraction is possible.

- Keep application-specific choices in application repositories.
- Prefer the Python standard library; separate catalog, Git access and project writes.
- Add a focused regression test for risky behavior or a real bug.
- Verify the source, complete bundle, actual skill name, relative references and license.
- Keep overlapping skills optional and prerequisites visible.
- Never include secrets, tokens, personal project settings or proprietary artifacts.

Run the suite and catalog checks described in [maintenance](docs/maintenance.md).
Describe changed behavior and actual verification in a pull request.
