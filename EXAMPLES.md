# Examples

Concrete prompts and the commands a well-behaved agent runs under the hood. The
agent always reads before it writes, and asks before side-effecting writes.

## Read an issue and summarize

> Read MUL-123 and tell me what's blocking it.

Two bounded reads beat one bulk pull: scan the threads, then open only what
matters. `--compact` drops bookkeeping fields without touching content.

```bash
multica issue get MUL-123 --output json
multica issue comment list MUL-123 --roots-only --summary --compact --output json
multica issue comment list MUL-123 --thread <comment-id> --tail 30 --compact --output json
multica issue metadata list MUL-123 --output json
```

Resolved threads come back folded to their root plus conclusion, with the
dropped count reported. Pass `--full` when you need the settled discussion.

## Draft a reply for review

> Draft a reply to the latest comment on MUL-123, but don't post it yet.

The agent gathers the thread, writes a draft, and shows it to you. It posts only
after you approve:

```bash
multica issue comment list MUL-123 --thread <comment-id> --tail 30 --compact --output json
# write reply.md, then (after your approval):
multica issue comment add MUL-123 --parent <comment-id> --content-file ./reply.md
rm ./reply.md
```

Comment bodies always go through a file and `--content-file` — never inline
`--content` — so shells don't rewrite backticks, `$()`, quotes, or newlines.
The file must live **inside the current working directory**; `/tmp` and other
outside paths are rejected so a stale file from another run can't be picked up.

## Triage a new issue

> Create a bug issue titled "Login redirect loops" and assign it to me.

```bash
multica issue search "login redirect" --output json   # don't file a duplicate
multica issue create --title "Login redirect loops" --description-file ./desc.md
# look up the assignee id first, then assign (note: assign uses --to-id, not --assignee-id):
multica workspace member list --output json
multica issue assign <issue-id> --to-id <user-id>
```

`issue create` refuses when an active duplicate already exists. Read that issue
before reaching for `--allow-duplicate`.

## Turn a business goal into an execution plan

> Find the team's existing data-labeling workflow and capabilities, then plan
> weekly rainy-day dataset labeling. Execute it after I confirm.

The agent should inspect relevant existing resources, including Issue
discussions where prior decisions may live, and synthesize what can be reused.
It then presents the complete resource choices, capability gaps, mutations,
dependencies, and acceptance criteria, and can execute it after one
confirmation:

```bash
multica issue search "rainy data labeling" --include-closed --output json
multica project list --output json
multica agent list --output json
multica skill list --output json
multica autopilot list --output json
```

This is targeted discovery, not a full workspace dump. The agent gets details
only for plausible matches, cites their identifiers in the proposal, prefers
reuse when behavior need not change, and treats unknown sharing as shared. A
material difference discovered during execution pauses the affected step for a
revised confirmation.

## Record progress without starting another run

> Mark MUL-123 in progress — I'm already working on it.

Status, assignment, and update can each enqueue a fresh agent run. When you are
only writing down what is already happening, suppress it:

```bash
multica issue status MUL-123 in_progress --no-start
```

Omit `--no-start` when you actually want to hand the work to the assignee.

## Find out what an agent actually did

> MUL-123 says done but nothing changed. What happened?

```bash
multica issue runs MUL-123 --output json
multica issue run-messages <task-id> --issue MUL-123 --output json
multica issue usage MUL-123 --output json
```

## Check linked pull requests

> Is MUL-123's PR merged yet?

```bash
multica issue pull-requests MUL-123 --output json
```

Read PR state from Multica rather than guessing from GitHub search or metadata.

## Side effects to confirm first

These are not cosmetic — confirm with the user before running them:

- Posting a comment that mentions an agent or squad (it enqueues a run and costs
  money), a member (it notifies a person), or `@all` (it notifies everyone).
- Changing status (`todo`/`backlog`/`done` can enqueue or stop work).
- Assigning, rerunning, or creating sub-issues.
- `multica issue cancel-task` — it interrupts a running agent, losing in-flight work.
- Label, property, and subscriber changes.
- Anything that *writes* under `agent`, `skill`, `squad`, or `autopilot` — creating,
  updating, archiving, importing, or rotating a webhook URL. Read-only `list` and
  `get` calls in those namespaces need no confirmation.

See [`skills/multica-cli/SKILL.md`](skills/multica-cli/SKILL.md) for the full
command reference and safety rules.
