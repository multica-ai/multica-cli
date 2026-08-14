# Using this skill with Cursor

There are two ways to use the Multica CLI skill in Cursor.

Both require the `multica` CLI at **v0.4.26 or newer** — earlier versions lack
commands the skill and the rule rely on (notably `--no-start`). Check with
`multica version`.

## Option 1: Personal Agent Skill (recommended)

Cursor loads skills from `~/.cursor/skills`. Copy the skill there once and it is
available across projects:

```bash
mkdir -p ~/.cursor/skills/multica-cli
cp -R skills/multica-cli/* ~/.cursor/skills/multica-cli/
```

This gives Cursor the full [`SKILL.md`](skills/multica-cli/SKILL.md) reference,
including every command recipe and safety rule.

## Option 2: Project rule

This repo ships a Cursor project rule at
[`.cursor/rules/multica-cli.mdc`](.cursor/rules/multica-cli.mdc). It is an
*Agent Requested* rule (`alwaysApply: false`), so Cursor pulls it in when a task
involves Multica rather than injecting it into every prompt.

To use the same rule in another project, copy the file into that project's
`.cursor/rules/` directory (create the folder if needed):

```bash
mkdir -p /path/to/project/.cursor/rules
cp .cursor/rules/multica-cli.mdc /path/to/project/.cursor/rules/
```

The project rule is intentionally concise and points back to `SKILL.md` for the
full command reference, so install the skill (Option 1) when you want the
complete recipes.
