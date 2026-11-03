# Maintenance and update review

The shared catalog is data, not permission to execute upstream code. Every source
is a public, credential-free GitHub HTTPS URL. Every installed upstream directory
is tied to a full Git commit and tree SHA; project files also have SHA-256 hashes.

## Catalog changes

1. Read the source repository, skill entry point, required references, declared
   dependencies and applicable license. Check whether relative references remain
   inside the complete skill directory. Do not index a runtime as a skill.
2. Add the smallest useful entry to `registry/catalog.json`. Keep overlapping,
   invasive, expensive or client-specific workflows optional.
3. Run `python skillfleet.py catalog check` for source compare links.
4. Run `python skillfleet.py catalog refresh`. Review changed source commits,
   license changes, scripts, network calls, hooks, external services and instructions.
5. Run the unit suite, `catalog validate`, then `catalog audit`. An audit fetches
   complete pinned directories and validates their names. It never executes their
   scripts and is not a semantic security certification.
6. Commit and review the catalog changes. Existing projects keep their explicit
   selections and pins until their maintainers propose and apply upgrades.

Built-in skill changes need a refreshed digest and a commit before connecting a
project. Initializing from an uncommitted skill would produce an unrestorable pin,
so it is refused. When forking, change the top-level `repository` URL in the
catalog before issuing new project pins.

## GitHub Actions

`ci.yml` runs the offline tests on Ubuntu/Windows and Python 3.10/3.13. Its separate
audit job checks real upstream bundles on the default branch and manual runs.
`upstream.yml` runs weekly or manually and creates a new draft update PR only when
there is source movement and no existing open SkillFleet update PR.

For automatic PRs, enable **Settings → Actions → General → Workflow permissions →
Allow GitHub Actions to create and approve pull requests**. The workflow requests
contents/pull-requests write permission only for its proposal job. The normal CI
workflow is read-only. Repository/org policy may disallow that setting; use the
generated report and open a review manually in that case.

Updates never auto-merge. Review the full upstream compare links, not just the
short lockfile diff. Source movement may affect only unrelated files; it is still
reported transparently. Review PRs generated with `GITHUB_TOKEN` manually: GitHub
may not automatically trigger another workflow from that token's events. The
proposal job runs validation itself before pushing its branch.

## Operational limits

- The Git cache is content-addressed by source URL. A cache lock rejects concurrent
  fetches rather than racing; retry after the other fetch ends.
- One project operation runs at a time. A persistent journal allows recovery after
  an interrupted multi-file operation. Files are replaced atomically one by one;
  readers should not use the project while installation is running.
- Offline mode disables lazy Git fetches. Restore requires cached objects when a
  built-in differs from the current central checkout. Commit installed skill files
  so a normal project clone does not need the cache.
- Managed scripts are installed as data; invoke helpers with their documented
  interpreter rather than relying on executable permission bits. If an agent later runs one, it needs its
  documented runtime, credentials, authorization and any platform-specific command
  adaptation. No client integration hooks are installed by SkillFleet.
- Do not customize managed upstream files in place. Put project overrides in the
  project's instructions, or maintain a separately reviewed fork in the catalog.
- Normal sync is conservative: a missing or modified managed file is reported,
  rather than overwritten. Restore intentional deletions from Git, then sync.
- Built-in source is MIT. Upstream license files are retained inside the skill or
  under `.skillfleet-licenses/`; the project lock records attribution and origin.

## Release checks

Run the documented quick start in an empty project and in a project with an
existing `AGENTS.md`. Exercise init, doctor, proposal/apply and rollback. Verify
complete scientific, design and notebook bundles, not only SKILL.md. Inspect CI
and the repository head after publishing; do not report a scheduled run as passed
before it actually runs.
