---
name: multica-cli
description: "Use when a local coding agent (Codex, Claude Code, Cursor, or similar) needs to operate Multica through the authenticated `multica` CLI: reading or updating issues, comments, metadata, projects, agents, squads, runtimes, repos, skills, autopilots, attachments, or workspace state; replying to a Multica issue from an external agent; creating or triaging issues; checking linked pull requests; or safely handling Multica mention/status side effects without relying on the Multica hosted agent runtime."
---

# Multica CLI

Use the local `multica` CLI as the source of truth. This skill teaches an
external agent how to drive Multica safely; it does not grant permissions.
Permissions come only from the user's installed CLI, selected profile,
workspace, and explicit approval to run commands.

## Start Safely

1. Verify the CLI and account state before doing work:

```bash
multica version
multica auth status
multica config show
```

If `multica auth status` reports no active session, the CLI is not logged in.
Stop and have the user authenticate; do not try to fake credentials:

```bash
multica login        # interactive auth + workspace setup
multica setup        # alternative: configure CLI, authenticate, start daemon
```

2. Use the correct workspace and profile. Discover what is available, then
prefer explicit flags when the user names them:

```bash
multica workspace list --output json                 # which workspaces exist
multica workspace switch <workspace-id>              # set the default for this profile
multica --profile <profile> --workspace-id <workspace-id> issue list --output json
```

3. Prefer `--output json` whenever a command supports it. Parse JSON rather than
scraping tables.

4. Never expose or store tokens, cookies, API keys, or CLI config secrets. Do
not bypass workspace permissions by calling private HTTP APIs directly.

## Command Reference

The flags below are the common ones for the issue workflow you will use most.
You do not need `--help` for these. Run `--help` only to confirm a rejected flag
or to explore the long-tail namespaces (`project`, `agent`, `squad`, `runtime`,
`repo`, `skill`, `autopilot`, `attachment`), whose shapes vary and are not
duplicated here. `[ ]` marks optional flags; `|` marks mutually exclusive ones.

```bash
# Read
multica issue get <id> --output json
multica issue list [--status <s>] [--assignee <name> | --assignee-id <uuid>] [--project <id>] [--priority <p>] [--limit N] [--metadata key=value] --output json
multica issue children <id> --output json
multica issue pull-requests <id> --output json
multica issue metadata list <id> --output json

# Comments (read)
multica issue comment list <id> --recent N --output json                    # N most active threads
multica issue comment list <id> --thread <comment-id> [--tail N] --output json  # one thread (root + replies)
multica issue comment list <id> --roots-only [--summary] --output json       # triage top-level threads
#   also: --since <RFC3339>, --before/--before-id <cursor> for pagination

# Create / update
multica issue create --title "..." [--description-file <path>] [--priority <p>] [--status <s>] [--assignee <name> | --assignee-id <uuid>] [--parent <id>] [--stage N] [--project <id>] [--due-date YYYY-MM-DD] [--attachment <path>] --output json
multica issue update <id> [--title "..."] [--description-file <path>] [--status <s>] [--priority <p>] [--assignee-id <uuid>] [--parent <id> | --parent ""] [--stage N] [--due-date YYYY-MM-DD]

# Status / assignment  (status values: backlog | todo | in_progress | in_review | done | blocked | cancelled)
multica issue status <id> <status>
multica issue assign <id> --to <name> | --to-id <uuid> | --unassign

# Comment (write) — body always via file, see Write Workflow below
multica issue comment add <id> [--parent <comment-id>] --content-file <path> [--attachment <path>]

# Metadata
multica issue metadata set <id> --key <k> --value <v> [--type string|number|bool]
multica issue metadata delete <id> --key <k>
```

Note `issue assign` uses `--to` / `--to-id` (not `--assignee`), while `issue
create` / `issue update` use `--assignee` / `--assignee-id`.

## Read Workflow

Use read commands first, then decide whether a write is needed.

```bash
multica issue get <issue-id-or-key> --output json
multica issue comment list <issue-id-or-key> --recent 10 --output json
multica issue metadata list <issue-id-or-key> --output json
multica issue pull-requests <issue-id-or-key> --output json
```

For large comment histories, prefer focused reads:

```bash
multica issue comment list <issue-id> --thread <comment-id> --tail 30 --output json
multica issue comment list <issue-id> --recent 10 --output json
```

For other resources, inspect the relevant namespace:

```bash
multica project --help
multica agent --help
multica squad --help
multica runtime --help
multica repo --help
multica skill --help
multica autopilot --help
multica attachment --help
```

## Write Workflow

Treat writes as side-effecting. If the user did not clearly ask for the write,
ask before running it. This includes creating comments, issues, status changes,
assignments, reruns, agent mentions, squad mentions, webhook/autopilot changes,
and repo checkout operations.

### Issue Comments

For agent-authored comments, always write the body to a UTF-8 file and pass it
with `--content-file`. Do not use inline `--content` for structured comments:
shells can rewrite backticks, `$()` expressions, variables, quotes, and
newlines before the CLI receives them.

```bash
# Create reply.md with real newlines first, then:
multica issue comment add <issue-id> --parent <comment-id> --content-file ./reply.md
rm ./reply.md
```

Keep the same `--parent` value as the comment being answered when replying to a
thread. Do not write literal `\n` escapes to fake line breaks.

### Issues and Metadata

Use files for long issue descriptions:

```bash
multica issue create --title "..." --description-file ./description.md
multica issue update <issue-id> --description-file ./description.md
```

Metadata is durable issue state, not a log. Read it on entry, but only write
high-signal facts future runs will re-read, such as `pr_url`, `pr_number`,
`pipeline_status`, `deploy_url`, `external_issue_url`, `waiting_on`,
`blocked_reason`, or `decision`.

```bash
multica issue metadata set <issue-id> --key pr_url --value <url>
multica issue metadata delete <issue-id> --key stale_key
```

## Mention Side Effects

Mention links are actions, not decoration:

```text
[@Name](mention://agent/<agent-id>)   # enqueues that agent
[@Name](mention://squad/<squad-id>)   # enqueues the squad leader
[@Name](mention://member/<user-id>)   # renders a person link
[MUL-123](mention://issue/<issue-id>) # renders an issue link
[@all](mention://all/all)             # broadcast, no specific agent run
```

Only `agent` and `squad` mentions enqueue agent work. A `member` mention is a
person link; an `issue` mention is a safe cross-reference.

Look up real UUIDs with JSON output before constructing mentions:

```bash
multica agent list --output json
multica squad list --output json
multica workspace member list --output json
```

Do not mention an agent just to thank, acknowledge, or sign off. Re-mentioning
an agent in a reply can trigger another run and create loops.

## Status and Assignment Side Effects

Status changes are not cosmetic. They can enqueue or stop work.

- `backlog` parks an agent-assigned issue.
- Moving `backlog` to `todo` or another active status can enqueue the assignee.
- `done` and `cancelled` are terminal states.
- `in_review` is useful while a PR or human review is pending, but it is still a
  write.

When creating sub-issues for ordered work, use stages and `backlog` for later
steps:

```bash
multica issue create --title "Research" --parent <id> --assignee <agent> --stage 1 --status todo
multica issue create --title "Build" --parent <id> --assignee <agent> --stage 2 --status backlog
multica issue children <id> --output json
```

## Pull Requests

When code changes are made for a Multica issue, include the routable issue key
in the PR title, body, or branch so Multica can link it.

```text
MUL-123: fix login redirect
```

Use close intent only when merging the PR should close the issue:

```text
Closes MUL-123
Fixes MUL-123
Resolves MUL-123
```

Read linked PR state from Multica rather than guessing from GitHub search or
metadata:

```bash
multica issue pull-requests <issue-id> --output json
```

## External Agent Boundaries

External agents do not receive Multica runtime context automatically. If the
user asks for work on a specific issue or comment, require or derive:

- issue id or issue key
- trigger comment id and parent thread, if replying
- intended workspace/profile, if more than one is configured
- whether writes are allowed
- whether mentions, status changes, reruns, or assignments are allowed

If any of these are missing and the operation would write state, ask before
proceeding. For read-only investigation, gather context with JSON output and
report what else is needed.
