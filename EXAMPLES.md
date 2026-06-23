# Examples

Concrete prompts and the commands a well-behaved agent runs under the hood. The
agent always reads before it writes, and asks before side-effecting writes.

## Read an issue and summarize

> Read MUL-123 and tell me what's blocking it.

```bash
multica issue get MUL-123 --output json
multica issue comment list MUL-123 --recent 10 --output json
multica issue metadata list MUL-123 --output json
```

## Draft a reply for review

> Draft a reply to the latest comment on MUL-123, but don't post it yet.

The agent gathers the thread, writes a draft, and shows it to you. It posts only
after you approve:

```bash
multica issue comment list MUL-123 --thread <comment-id> --tail 30 --output json
# write reply.md, then (after your approval):
multica issue comment add MUL-123 --parent <comment-id> --content-file ./reply.md
rm ./reply.md
```

Comment bodies always go through a file and `--content-file` — never inline
`--content` — so shells don't rewrite backticks, `$()`, quotes, or newlines.

## Triage a new issue

> Create a bug issue titled "Login redirect loops" and assign it to me.

```bash
multica issue create --title "Login redirect loops" --description-file ./desc.md
# look up the assignee id first, then assign (note: assign uses --to-id, not --assignee-id):
multica workspace member list --output json
multica issue assign <issue-id> --to-id <user-id>
```

## Check linked pull requests

> Is MUL-123's PR merged yet?

```bash
multica issue pull-requests MUL-123 --output json
```

Read PR state from Multica rather than guessing from GitHub search or metadata.

## Side effects to confirm first

These are not cosmetic — confirm with the user before running them:

- Posting a comment that `@mentions` an agent or squad (it enqueues a run).
- Changing status (`todo`/`backlog`/`done` can enqueue or stop work).
- Assigning, rerunning, or creating sub-issues.

See [`skills/multica-cli/SKILL.md`](skills/multica-cli/SKILL.md) for the full
command reference and safety rules.
