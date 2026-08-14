#!/usr/bin/env python3
"""Regression tests for lint-skill-commands.py.

A lint that only ever runs against correct docs proves nothing — it can pass
because it found no problems, or because it cannot find problems. Each case here
feeds the linter a deliberately broken (or deliberately fine) fixture and asserts
what it reports.

Usage:
  scripts/test-lint.py

Requires the `multica` CLI on PATH, same as the linter itself.
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "lint-skill-commands.py"


def load_linter():
    spec = importlib.util.spec_from_file_location("linter", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_case(linter, *, skill_body: str, undocumented_ok: dict[str, str] | None = None) -> list[str]:
    """Lint a throwaway repo containing just SKILL.md, and return its errors."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        skill_rel = "skills/multica-cli/SKILL.md"
        skill_path = root / skill_rel
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text(skill_body, encoding="utf-8")

        original = (
            linter.REPO_ROOT,
            linter.DOC_FILES,
            linter.COVERAGE_FILE,
            linter.UNDOCUMENTED_OK,
            linter.VERSION_DECLARED_IN,
        )
        linter.REPO_ROOT = root
        linter.DOC_FILES = [skill_rel]
        linter.COVERAGE_FILE = skill_rel
        linter.VERSION_DECLARED_IN = []
        if undocumented_ok is not None:
            linter.UNDOCUMENTED_OK = undocumented_ok
        try:
            return linter.check_validity(False) + linter.check_coverage(False)
        finally:
            (
                linter.REPO_ROOT,
                linter.DOC_FILES,
                linter.COVERAGE_FILE,
                linter.UNDOCUMENTED_OK,
                linter.VERSION_DECLARED_IN,
            ) = original


def block(*commands: str) -> str:
    body = "\n".join(commands)
    return f"```bash\n{body}\n```\n"


# Every CLI command, so a fixture only fails coverage when the case intends to.
def full_coverage_block(linter) -> str:
    root_help = linter.cli_help("")
    names = sorted(linter.declared_subcommands(root_help))
    names += [f"issue {s}" for s in sorted(linter.declared_subcommands(linter.cli_help("issue") or ""))]
    mentions = "\n".join(f"- `multica {n}`" for n in names)
    return f"\nCommands referenced for coverage:\n\n{mentions}\n"


def main() -> int:
    if shutil.which("multica") is None:
        print("error: `multica` CLI not on PATH; these tests exercise the real help output", file=sys.stderr)
        return 2

    linter = load_linter()
    covered = full_coverage_block(linter)
    failures: list[str] = []

    def check(name: str, errors: list[str], *, expect: str | None) -> None:
        joined = "\n".join(errors)
        if expect is None:
            if errors:
                failures.append(f"{name}: expected no errors, got:\n{joined}")
            else:
                print(f"  ok  {name}")
            return
        if expect in joined:
            print(f"  ok  {name}")
        else:
            failures.append(f"{name}: expected an error containing {expect!r}, got:\n{joined or '(none)'}")

    # 1. An unknown top-level command must be reported. Regression: this used to
    #    pass silently, because anything unresolved was treated as a root-level
    #    flag invocation like `multica --version`.
    check(
        "unknown top-level command",
        run_case(linter, skill_body=block("multica frobnicate") + covered),
        expect="has no command `frobnicate`",
    )

    # 1b. ...including when it carries only valid global flags, which is what
    #     made the original hole invisible.
    check(
        "unknown top-level command with a valid global flag",
        run_case(linter, skill_body=block("multica frobnicate --debug") + covered),
        expect="has no command `frobnicate`",
    )

    # 1c. Cobra also accepts global flags *before* the command. A boolean flag
    #     consumes nothing, so the word after it is still a command that must
    #     exist. Assuming every flag swallows the next token hid this.
    for boolean_flag in ("--debug", "-h", "--help", "-v", "--version"):
        check(
            f"unknown top-level command after boolean {boolean_flag}",
            run_case(linter, skill_body=block(f"multica {boolean_flag} frobnicate") + covered),
            expect="has no command `frobnicate`",
        )

    # 1d. A value-taking global flag genuinely does consume the next token, so
    #     that token must NOT be reported as a command. Deliberately no
    #     resolvable command here: with one (`... issue list`), resolve_path()
    #     succeeds and the stray-word branch this is meant to pin is never run.
    check(
        "value-taking global flag consumes its argument",
        run_case(linter, skill_body=block("multica --profile dev --version") + covered),
        expect=None,
    )

    # 1e. ...and the same asserted directly, so the branch is pinned even if the
    #     surrounding fixture changes shape later.
    root_specs = linter.declared_flag_specs(linter.cli_help(""))
    direct = [
        ("multica --profile dev", []),
        ("multica --debug frobnicate", ["frobnicate"]),
        ("multica --profile=dev frobnicate", ["frobnicate"]),
    ]
    for line, expected in direct:
        got = linter.stray_words(linter.normalize(line), root_specs)
        if got == expected:
            print(f"  ok  stray_words({line!r}) -> {got}")
        else:
            failures.append(f"stray_words({line!r}): expected {expected}, got {got}")

    # 2. An unknown subcommand must be reported. Cobra prints the *parent's*
    #    help and exits 0 here, so exit status alone would miss it.
    check(
        "unknown subcommand",
        run_case(linter, skill_body=block("multica issue frobnicate MUL-1") + covered),
        expect="has no subcommand `frobnicate`",
    )

    # 3. An unknown flag must be reported.
    check(
        "unknown flag",
        run_case(linter, skill_body=block("multica issue get MUL-1 --outputt json") + covered),
        expect="does not accept --outputt",
    )

    # 4. A CLI command absent from SKILL.md must be reported.
    check(
        "undocumented command",
        run_case(linter, skill_body=block("multica issue get MUL-1 --output json")),
        expect="exists in the CLI but is never mentioned",
    )

    # 5. A stale allowlist entry must be reported, so exemptions cannot outlive
    #    the command they excuse.
    check(
        "stale UNDOCUMENTED_OK entry",
        run_case(
            linter,
            skill_body=block("multica issue get MUL-1") + covered,
            undocumented_ok={"issue ghostcmd": "removed upstream"},
        ),
        expect="no longer a CLI command",
    )

    # 6. Real usage must NOT trip the linter. Positional values that look like
    #    subcommands, global flags before the command, inline flag values, and a
    #    genuine root-level invocation are all legitimate.
    check(
        "no false positives on valid usage",
        run_case(
            linter,
            skill_body=block(
                "multica config set workspace_id abc123",
                "multica --profile dev --workspace-id <ws> issue list --output json",
                "multica --profile=dev issue list --output json",
                "multica --version",
                "multica issue status <id> in_progress --no-start",
                "multica issue comment list <id> --roots-only --summary --compact --output json",
            )
            + covered,
        ),
        expect=None,
    )

    print()
    if failures:
        print(f"{len(failures)} test(s) failed:\n", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}\n", file=sys.stderr)
        return 1

    print("All lint regression tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
