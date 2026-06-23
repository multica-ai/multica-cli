# Multica CLI

A Codex skill that teaches local coding agents how to operate Multica through
the authenticated `multica` CLI.

This repository does not grant Multica access by itself. Permissions come from
the user's local CLI login, selected profile, active workspace, and explicit
approval for any commands the agent runs.

## What It Covers

- Checking CLI auth, profile, and workspace state
- Reading issues, comments, metadata, projects, agents, squads, runtimes, repos,
  skills, autopilots, and attachments
- Writing safe issue comments with `--content-file`
- Creating or updating issues and high-signal metadata
- Handling mention, status, assignment, rerun, and sub-issue side effects
- Linking pull requests back to Multica issues

## Install

Install the skill from this repository with path `multica-cli`:

```bash
install-skill-from-github.py --repo multica-ai/multica-cli --path multica-cli
```

Restart Codex after installing new skills.

## Requirements

- The `multica` CLI is installed locally.
- The user has run `multica login` or otherwise authenticated the CLI.
- The intended workspace/profile is selected, or passed explicitly with
  `--workspace-id` and `--profile`.

## Usage

Invoke the skill when asking a local agent to work with Multica:

```text
Use $multica-cli to read MUL-123 and draft a reply.
```

For write operations, the agent should ask before making state changes unless
the user has already clearly authorized that exact action.
