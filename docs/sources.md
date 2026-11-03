# Source decisions

The first release was checked against upstream repository content on 2026-11-03.
Exact commits are in `registry/catalog.lock.json`; descriptions do not substitute
for review of those pinned instructions. This is a practical selection, not a
ranking derived from popularity.

| Source | Included use | Decision |
| --- | --- | --- |
| [Superpowers](https://github.com/obra/superpowers) | Debugging, verification, optional TDD | Selected skills, not the framework bootstrap or delegation hooks |
| [Matt Pocock](https://github.com/mattpocock/skills) | Module design, domain modeling, review | Current nested engineering paths verified |
| [Addy Osmani](https://github.com/addyosmani/agent-skills) | API design, planning, simplification, CI, security | Load task-specific workflows on demand |
| [Ponytail](https://github.com/DietrichGebert/ponytail) | Concrete change review | No unverified token/cost accounting claims |
| [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | UI/UX design search | Full local scripts, data and references retained |
| [Taste](https://github.com/Leonxlnx/taste-skill) | Alternative art direction | Separate profile; Node 22+ and Chromium required |
| [OpenAI](https://github.com/openai/skills) | Jupyter, PDF, browser, security, CI, .NET | Skill-specific license files retained |
| [Anthropic](https://github.com/anthropics/skills) | Internal communications and MCP building | Only the selected Apache-2.0 bundles |
| [K-Dense](https://github.com/K-Dense-AI/scientific-agent-skills) | Statistics, scientific writing, literature, ML and plots | Canonical repository name; keep optional service prerequisites visible |
| [Cloudflare](https://github.com/cloudflare/skills) | Workers, Wrangler, Durable Objects, Next.js | Deploying remains a project decision |
| [Vercel](https://github.com/vercel-labs/agent-skills) | React performance, composition, web review | MIT declaration in upstream README; exact installed contents pinned |
| [Planning with Files](https://github.com/OthmanAdi/planning-with-files) | Persistent long-task plans | Skill only; no lifecycle hooks or plugins automatically installed |
| [Caveman](https://github.com/JuliusBrussee/caveman) | Explicit terse-voice option | No default profile, no promised saving percentage |

## References kept outside the installation catalog

- **Karpathy skills:** a useful simplicity reference, but no explicit license was
  detected in the checked repository tree/metadata. Original `fleet-engineering`
  guidance covers minimal, thoughtful changes without copying that content.
- **Graphify:** moved to [Graphify-Labs](https://github.com/Graphify-Labs/graphify).
  The checked `v8` tree has no `SKILL.md`. It is a separate tool, not a bundle to
  pretend was installed as a skill.
- **Remotion:** [official agent skills](https://github.com/remotion-dev/skills)
  exist and contain a complete router bundle. No standalone repository license
  was found in the checked tree. SkillFleet ships original `fleet-video` workflow
  guidance and official documentation links, without redistributing that content.
- **Anthropic document skills:** upstream explicitly describes docx/pdf/pptx/xlsx
  as source-available, not open source. Their terms are not silently replaced by
  SkillFleet's MIT license. Use `fleet-documents` and the Apache OpenAI PDF workflow,
  or separately review those upstream terms in your environment.
- **Manim:** an animation runtime, not itself an agent skill. Original video
  guidance points to official documentation.
- **marimo-pair:** service-specific optional pairing. A running service and its
  credentials belong in the user's environment, not the central registry.

The earlier recommendations were not all installed verbatim. Real paths, complete
bundles, dependencies and distribution terms determined this first catalog.

## Client adaptation

Some upstream text uses client variables such as `CLAUDE_PLUGIN_ROOT`, `CODEX_HOME`
or paths from a global installation. SkillFleet does not rewrite signed/pinned
upstream files. In a project-only installation, resolve references from the actual
installed skill directory. For example, UI/UX search from the project root is:

```bash
python .agents/skills/ui-ux-pro-max/scripts/search.py "dashboard keyboard focus" --domain ux
```

Claude Code uses the equivalent `.claude/skills/...` path. Running a helper is a
separate action from installing the bundle; first inspect it and its prerequisites.
