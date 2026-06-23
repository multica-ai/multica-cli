# Multica CLI Skill

> Built for [Multica](https://github.com/multica-ai/multica) — an open-source platform for running and managing coding agents with reusable skills.

A portable skill that teaches any local coding agent — Claude Code, Codex, Cursor,
and others — how to operate [Multica](https://github.com/multica-ai/multica)
through the authenticated `multica` CLI: read and triage issues, reply to
comments safely, manage metadata, and handle mention/status side effects.

English | [简体中文](./README.zh.md)

## What it does not do

This repository does **not** grant Multica access by itself. Permissions come
only from the user's local CLI login, selected profile, active workspace, and
explicit approval for any commands the agent runs. The skill teaches *how* to
drive Multica safely; it never bypasses workspace permissions or stores secrets.

## What it covers

- Checking CLI auth, profile, and workspace state (and how to log in)
- Reading issues, comments, metadata, projects, agents, squads, runtimes, repos,
  skills, autopilots, and attachments
- Writing safe issue comments with `--content-file`
- Creating or updating issues and high-signal metadata
- Handling mention, status, assignment, rerun, and sub-issue side effects
- Linking pull requests back to Multica issues

## Install

The skill lives at `skills/multica-cli/`. Pick the path for your tool.

### Claude Code (plugin marketplace)

```text
/plugin marketplace add multica-ai/multica-cli
/plugin install multica-cli@multica-cli
```

### Codex (skill installer)

```bash
install-skill-from-github.py --repo multica-ai/multica-cli --path skills/multica-cli
```

Restart Codex after installing new skills.

### Cursor

Copy the skill into your personal Cursor skills directory:

```bash
mkdir -p ~/.cursor/skills/multica-cli
cp -R skills/multica-cli/* ~/.cursor/skills/multica-cli/
```

Or drop the project rule [`.cursor/rules/multica-cli.mdc`](.cursor/rules/multica-cli.mdc)
into a project's `.cursor/rules/` directory. See [CURSOR.md](./CURSOR.md) for details.

### Any other agent

Copy [`skills/multica-cli/SKILL.md`](skills/multica-cli/SKILL.md) into wherever
your tool loads skills or instructions from.

## Requirements

- The `multica` CLI is installed locally.
- The user has run `multica login` (or `multica setup`) to authenticate.
- The intended workspace/profile is selected, or passed explicitly with
  `--workspace-id` and `--profile`.

## Usage

Ask your agent to work with Multica once the skill is installed, for example:

```text
Read MUL-123 with the multica CLI and draft a reply for me to review.
```

For write operations (comments, status changes, mentions, new issues), the agent
should ask before making state changes unless you have already clearly
authorized that exact action. See [EXAMPLES.md](./EXAMPLES.md) for more.

## License

[MIT](./LICENSE)
