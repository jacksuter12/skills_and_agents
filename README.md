# skills_and_agents

A home for Claude Code skills and subagents.

## Layout

```
.claude/
  skills/<skill-name>/      # one directory per skill
    SKILL.md                # frontmatter (name, description) + instructions
    references/             # docs/templates the skill reads on demand
    scripts/                # code the skill runs (not read into context)
    examples/               # finished outputs, for reference
  agents/<agent-name>.md    # subagent definitions (frontmatter + system prompt)
```

Keeping everything under `.claude/` means Claude Code picks the skills and agents up automatically when you work inside this repo. To use one everywhere, link it into your user directory:

```bash
ln -s "$PWD/.claude/skills/html-diagram" ~/.claude/skills/html-diagram
```

## Skills

| Skill | What it does |
|-------|--------------|
| [html-diagram](.claude/skills/html-diagram/SKILL.md) | Diagrams as self-contained HTML + inline SVG, with a Playwright screenshot-and-lint loop. Needs [`uv`](https://docs.astral.sh/uv/). |
