# Business Goal Orchestration

Use this workflow when the user gives an outcome rather than a specific Multica
command: finding existing team knowledge, selecting capable resources,
coordinating dependent work, or defining a recurring automation. Keep a
concrete operation on a known target in the direct workflow from `SKILL.md`.

## Clarify only material facts

Resolve the profile and workspace first. Ask only for missing facts that change
the result: outcome, deliverable, frequency, data sources, constraints,
deadline, and acceptance criteria. Present two or more mutually exclusive
choices as a numbered list and accept a number-only reply.

Classify the goal before choosing resources:

- **one-time:** one Issue, optionally assigned to an Agent or attached to a
  Project;
- **recurring:** an Autopilot whose description is the complete task prompt;
- **coordinated:** a parent Issue with staged child Issues, optionally using a
  Squad when role separation adds real value.

## Discover and synthesize

The request authorizes targeted read-only discovery, not a full workspace
inventory. Query only resources that may supply relevant business context and
available capabilities: Issues, Projects, Agents, Squads, Skills, and
Autopilots. For each relevant resource, search or list first, then get only
plausible candidates.

```bash
multica issue search "<goal terms>" --include-closed --output json
multica project list --output json
multica agent list --output json
multica squad list --output json
multica skill list --output json
multica autopilot list --output json
```

Use each namespace's `get <id> --output json` command only for candidates that
may affect the proposal. Compare actual descriptions, instructions, bindings,
membership, status, active use, and relevant Issue discussions; do not select
a resource by name alone.

Synthesize the evidence before proposing work:

- what the workspace already knows about the goal;
- which existing resources provide each required capability;
- what is already in progress or previously decided;
- genuine capability or ownership gaps;
- source resource identifiers for every material conclusion.

This synthesis is how the user discovers team knowledge and capabilities
without rebuilding work or creating a second, inconsistent source of truth.

## Match capabilities and sharing risk

Classify every resource that might be changed:

- **dedicated:** evidence shows it serves this goal and has no known active
  external dependency;
- **shared:** another Project, Squad, Autopilot, active Issue, or workflow uses
  it;
- **unknown:** the available CLI reads cannot establish either state.

Treat unknown as shared. Prefer reuse over creating a duplicate when an
existing resource matches the purpose and can be used unchanged. Modify a
dedicated resource only when the evidence is sufficient. Keep shared and
unknown resources unchanged; if reuse would alter their behavior, propose an
isolated resource instead.

Use a Squad only when coordination or role separation adds value. An Autopilot
assigns an Agent, not a Squad; recurring coordinated work can assign the Squad
leader Agent and let that leader coordinate member Agents through child Issues.

## Protect Agents and Skills

Treat Agent and Skill mutations as high impact. Prefer an existing capable
Agent and already-installed Skills. The complete plan must show the exact
create, update, import, delete, binding, instruction, runtime, model,
permission, and environment delta without secret values.

The plan-level approval is not enough for these mutations: get separate
confirmation immediately before changing an Agent or Skill. Assigning an
unchanged Agent to an Issue or adding it to a Squad uses the Agent without
changing its configuration, so the plan-level confirmation is sufficient.

When no maintained Skill supplies a required capability, offer two choices:

1. put clearly marked temporary instructions in the Issue or Autopilot
   description when the Agent already has the required tools, permissions,
   credentials, and data access;
2. stop while the user creates or imports a maintained Skill.

Instructions cannot provide a missing tool or permission. For recurring work,
put the complete temporary instruction in the Autopilot description and remind
the user that stable rules belong in a maintained Skill.

## Present one executable plan

The in-chat orchestration design is the execution plan. It contains:

- goal, deliverables, frequency, and acceptance criteria;
- relevant existing resources and the evidence for reuse or isolation;
- capability coverage and genuine gaps;
- task breakdown, dependencies, and every proposed mutation;
- the Agent, Squad, Issue, Project, Skill, and Autopilot relationships;
- temporary instructions and their limitations;
- CLI-unsupported steps that must be completed in Multica Web;
- risks, verification, and resume behavior.

Get one user confirmation for the complete plan, except for the separate
Agent/Skill confirmation above. After confirmation, execute the plan directly
in dependency order. Do not create a repository design document,
specification, or software implementation plan unless the user explicitly asks
for that artifact.

Approval covers only the listed mutations in the stated workspace. A material
deviation in target, fields, resource choice, dependency, or impact stops
execution before the changed step. Show the difference and request revised
confirmation; never adapt silently.

## Execute and resume

Use only the authenticated `multica` CLI and record returned resource IDs for
dependent steps. Keep work passive only while dependencies are incomplete:

1. create or verify passive dependencies;
2. create an Issue directly as `todo` when it is ready to run;
3. use `backlog` only to park an Issue with unfinished dependencies;
4. create an Autopilot after its Agent, Project, and prompt are ready;
5. add or enable its trigger last.

Do not create a ready Issue as `backlog` merely to move it immediately to
`todo`. On failure, stop dependent steps and report completed resources, their
IDs, the observed error, steps not run, and the exact resume point. Resume by
getting each recorded ID; never recreate a resource by name.

If the CLI lacks a required operation, name it as a Multica Web step and wait
for the user to complete it before continuing dependent work. Never read a
saved token or call the Multica API directly as a fallback.
