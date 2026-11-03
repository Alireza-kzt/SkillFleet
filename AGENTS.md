# Working on SkillFleet

SkillFleet contains shared registry data, source pins, reusable profiles, common
standards and lifecycle tooling. Never add application-specific selections,
credentials or private project context.

Keep the CLI dependency-free at runtime and compatible with Python 3.10+. Separate
catalog decisions, Git plumbing and project filesystem operations. Choose small,
readable implementations; do not replace a few standard-library calls with a framework.

Run `python -m unittest discover -s tests -v` and `python skillfleet.py catalog validate`
after relevant changes. Run `catalog audit` when upstream pins or bundle handling
change. Tests must cover behavior and data protection, not implementation trivia.

Never execute upstream scripts during catalog validation or installation. Preserve
complete bundles and license files. Reject unknown paths, symlinks and modified
managed files. Review source compare links before accepting new upstream pins.
