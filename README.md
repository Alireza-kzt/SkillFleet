# SkillFleet

**Useful agent skills. Exact versions. Independent projects.**

SkillFleet is a small, dependency-free Python CLI and a curated registry for Codex,
Claude Code and Cursor. It connects only the skills a project needs, keeps exact
versions in that project, and makes upgrades reviewable and reversible.

- **51 installable skills** from 13 upstream repositories and 10 original SkillFleet workflows.
- **21 reusable profiles** for engineering, Python, Flutter/GetX, web, research,
  notebooks, academic writing, organizational work, documents and video.
- Two default skills: readable engineering and focused context use.
- Complete skill directories, references, assets and applicable license files.
- No upstream scripts, hooks, package installers or paid services run during installation.
- No runtime Python dependencies, account or telemetry. Python 3.10+ and Git required.

## Quick start

Clone SkillFleet **once**, outside your application repositories:

```bash
git clone https://github.com/Alireza-kzt/SkillFleet.git
```

Run from the project you want to connect, using the actual checkout path:

```bash
python /path/to/SkillFleet/skillfleet.py init --profile python --profile research --profile notebook
python /path/to/SkillFleet/skillfleet.py doctor
```

On Windows, `py -3 C:/Tools/SkillFleet/skillfleet.py` can replace `python ...`.
Use `python3` where `python` is unavailable. Paths containing spaces must be quoted.
Omit `--profile` to detect basic Python, React/Next.js, Flutter and notebook markers.
Research, security and organizational intent require explicit selection.

For a shorter command, optionally install **from this retained checkout**:

```bash
python -m pip install -e /path/to/SkillFleet
skillfleet init --profile web --profile design --profile rtl
```

This release is checkout-based; retain the checkout. A standalone wheel/PyPI package
is not published. The direct Python command needs no installation.

## Profiles

Every initial profile selection includes `core`. Shared profile definitions are
templates; their expansion is frozen into the project's explicit skill list.
Changing a central profile never silently changes an existing project's selection.

| Profile | Purpose |
| --- | --- |
| `core` | Small, readable changes; efficient context |
| `python` | Python, FastAPI, OpenCV and module boundaries |
| `flutter` | Flutter/Dart/GetX ownership and lifecycles |
| `web` | React/Next.js performance, composition and interface review |
| `design` | UI/UX Pro Max with its complete search data |
| `taste` | Alternative art-direction workflow; Node 22+ and Chromium |
| `rtl` | Persian typography and mixed RTL/LTR layouts |
| `research` | Experiment integrity and statistical analysis |
| `ml` | Scientific Python, scikit-learn, Lightning and plotting |
| `notebook` | Jupyter templates and reproducible experiments |
| `academic` | Verified sources, literature reviews and manuscripts |
| `organization` | Sprint tasks, acceptance criteria, ADRs and updates |
| `video` | Original storyboarding and Remotion/Manim workflow |
| `documents` | Native editable artifacts, rendering and PDF |
| `cloudflare` | Workers and Wrangler |
| `security` | Security practices and threat modeling |
| `quality` | Review, simplification and verification |
| `devops` | CI/CD and GitHub Actions investigations |
| `dotnet` | ASP.NET Core |
| `mcp` | MCP servers and API contracts |
| `long-task` | Persistent planning; no upstream hooks installed |

Choose one primary design workflow (`design` or `taste`) unless you intentionally
coordinate their overlapping instructions. Framework-wide workflow skills and
Caveman are available individually, rather than injected into every project.

```bash
skillfleet list
skillfleet list --profile research
skillfleet add performance-optimization
skillfleet remove performance-optimization
```

See [the complete catalog](docs/catalog.md) and [source decisions](docs/sources.md).
Installing instructions does not install PyTorch, Flutter, browser binaries,
document renderers, credentials or client plugins. Each catalog entry records
prerequisites. Core works without any optional service.

## What lives in each project

- `skillfleet.json`: explicit skills, chosen agents, exclusions and profile provenance.
- `skillfleet.lock.json`: exact source commits, directory trees and installed file hashes.
- `.agents/skills/`: Codex and Cursor skill directories.
- `.claude/skills/`: Claude Code copies, only if selected.
- `.skillfleet/INSTRUCTIONS.md`: short shared standards referenced by project instructions.
- A small marked block appended to `AGENTS.md` and/or `CLAUDE.md`.

Existing project instructions and other skills are preserved. An edited managed
file blocks replacement, removal and upgrade. Keep project-specific constraints
in the project's existing instructions; the central repository contains no
application-specific configurations, names, secrets or environments.

Commit the config, lock, installed skill folders, instruction block and
`.skillfleet/INSTRUCTIONS.md` / `.skillfleet/.gitignore`. Local history, proposals
and transaction journals are ignored. Team members get the same vendored skills
from a normal project clone; the Git cache is only an optimization.

## Restore, review, update and roll back

```bash
skillfleet sync                  # Keep this project's exact pins
skillfleet check                 # Report upstream source movement; install nothing
```

Maintainers review upstream changes in the central repository. Once a catalog
update is merged, update your central checkout and propose changes in the project:

```bash
git -C /path/to/SkillFleet pull --ff-only
skillfleet update                # Writes .skillfleet/update.diff; installs nothing
skillfleet update --apply        # Apply that exact proposal after reviewing the diff
skillfleet doctor
# Run this project's relevant checks, then commit the project changes.
```

```bash
skillfleet rollback              # Undo the last local SkillFleet transaction
skillfleet --offline sync        # Restore using only current local/cached objects
```

`--offline` is a global option and belongs **before** the subcommand. Offline
restoration needs the relevant objects cached, or unchanged local built-ins.
Normal project clones already contain their committed installed files.

Rollback refuses later local edits instead of overwriting them. It is a local
snapshot stack; use Git to restore an older committed selection across machines.
Interrupted file operations have a recovery journal:

```bash
skillfleet recover
```

If an operation lock remains after a killed process, first confirm no SkillFleet
process is still running, remove only `.skillfleet/operation.lock`, then recover.
There is no silent `--force` overwrite mode.

## Automatic upstream checks

The repository includes weekly and manually triggered **draft update proposals**.
The workflow reports source compare links, refreshes and verifies the catalog,
and opens at most one draft PR at a time. It never merges updates or changes any
connected project. Review the linked upstream changes before merging.

GitHub must allow Actions to create pull requests for the automatic draft step;
see [maintenance](docs/maintenance.md). A report artifact remains available if PR
creation is unavailable. No ChatGPT subscription or scheduling service is required.

## Development

```bash
python -m unittest discover -s tests -v
python skillfleet.py catalog validate
python skillfleet.py catalog audit       # Fetch and verify complete pinned bundles
```

Linux and Windows are in the CI matrix. CI validates the actual catalog, exercises
filesystem transactions and Git fixtures, and audits upstream bundles separately.
The bundled standards guide agents; the manager verifies files and versions, not
whether every future change follows Clean Code. Project tests remain essential.

## فارسی

[راهنمای فارسی و دستور اتصال پروژه‌ها](docs/README.fa.md)

SkillFleet code and original skills are MIT-licensed. Upstream skills retain their
own licenses and attribution; [source notes](docs/sources.md) explain exclusions.
