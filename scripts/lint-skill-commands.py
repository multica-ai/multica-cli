#!/usr/bin/env python3
"""Check the documented `multica` commands against the installed CLI.

This skill is only useful while it matches the CLI it describes. Two checks run:

  validity  every command path and flag written in the docs must exist in
            `multica <path> --help`. Catches renamed or removed surface.
  coverage  every top-level namespace and every `multica issue` subcommand must
            be mentioned somewhere in SKILL.md. Catches surface that shipped
            after the docs were last touched — the failure mode that actually
            happened, where the skill silently lost half the issue namespace.

Deliberate omissions go in UNDOCUMENTED_OK below, with a reason.

Usage:
  scripts/lint-skill-commands.py [--verbose]

Requires the `multica` CLI on PATH. Only `--help` is invoked, so no login,
network, or workspace is needed.
"""

from __future__ import annotations

import argparse
import re
import shlex
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Files scanned for command examples. SKILL.md is the contract; the others are
# docs that get copy-pasted just as often, so they rot the same way.
DOC_FILES = [
    "skills/multica-cli/SKILL.md",
    "EXAMPLES.md",
    "README.md",
    "README.zh.md",
    "CURSOR.md",
    ".cursor/rules/multica-cli.mdc",
]

# The file that must actually teach the surface. Coverage is measured here only.
COVERAGE_FILE = "skills/multica-cli/SKILL.md"

# Surface intentionally left out of SKILL.md, with the reason it is not a gap.
UNDOCUMENTED_OK = {
    "daemon": "runtime host concern, not an agent operation",
    "update": "CLI self-update, belongs in install docs",
    "plugin": "workspace-private plugin authoring, out of scope for issue work",
    "issue reorder": "board cosmetics; no agent workflow needs it",
}

# Placeholder / shell noise that is never a real token.
PLACEHOLDER = re.compile(r"^<.*>$|^\.{3}$|^N$")
BARE_WORD = re.compile(r"^[a-z][a-z0-9-]*$")
# A flag as *declared* by cobra: line starts with optional short form, then long.
HELP_FLAG_DECL = re.compile(r"^\s+(?:-[A-Za-z],\s+)?(--[a-z0-9-]+)")
HELP_SHORT_DECL = re.compile(r"^\s+(-[A-Za-z]),")
# Subcommand as declared in a cobra COMMANDS block: "  name:  description".
HELP_SUBCOMMAND = re.compile(r"^\s{2,}([a-z][a-z0-9-]*):\s")

FENCED = re.compile(r"^```(\w*)\s*$")
INLINE_CODE = re.compile(r"`([^`\n]+)`")


class CliMissing(Exception):
    pass


def usage_path(help_text: str) -> str | None:
    """The command path cobra reports in its USAGE line, e.g. `issue get`."""
    lines = help_text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "USAGE":
            for candidate in lines[i + 1 :]:
                tokens = candidate.split()
                if tokens and tokens[0] == "multica":
                    words = []
                    for tok in tokens[1:]:
                        if BARE_WORD.match(tok):
                            words.append(tok)
                        else:
                            break
                    return " ".join(words)
            break
    return None


@lru_cache(maxsize=None)
def cli_help(path: str) -> str | None:
    """Return `multica <path> --help` output, or None if the path is unknown.

    Exit status is not enough: given an unknown subcommand plus `--help`, cobra
    prints the *parent's* help and exits 0, so `issue frobnicate` looks valid.
    Confirm the help we got back actually describes the path we asked for.
    """
    argv = ["multica", *shlex.split(path), "--help"] if path else ["multica", "--help"]
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    except FileNotFoundError as exc:  # pragma: no cover - guarded by main()
        raise CliMissing from exc
    out = proc.stdout + proc.stderr
    if proc.returncode != 0 or "unknown command" in out:
        return None
    if usage_path(out) != path:
        return None
    return out


def declared_flags(help_text: str) -> set[str]:
    """Flags cobra declares in this command's help, ignoring prose mentions."""
    flags: set[str] = set()
    for line in help_text.splitlines():
        m = HELP_FLAG_DECL.match(line)
        if m:
            flags.add(m.group(1))
        m = HELP_SHORT_DECL.match(line)
        if m:
            flags.add(m.group(1))
    return flags


def declared_subcommands(help_text: str) -> set[str]:
    in_commands = False
    found: set[str] = set()
    for line in help_text.splitlines():
        stripped = line.strip()
        if stripped.endswith("COMMANDS") and stripped.isupper():
            in_commands = True
            continue
        if in_commands:
            if stripped and stripped.isupper() and stripped.endswith(("FLAGS", "EXAMPLES", "VARIABLES", "MORE")):
                in_commands = False
                continue
            m = HELP_SUBCOMMAND.match(line)
            if m:
                found.add(m.group(1))
    return found


def extract_command_lines(text: str) -> list[tuple[int, str]]:
    """Pull `multica ...` invocations out of fenced shell blocks and inline code."""
    lines = text.splitlines()
    out: list[tuple[int, str]] = []
    fence_lang: str | None = None

    for idx, raw in enumerate(lines, start=1):
        fence = FENCED.match(raw)
        if fence:
            fence_lang = None if fence_lang is not None else (fence.group(1) or "")
            continue

        if fence_lang is not None:
            if fence_lang in ("bash", "sh", "shell", ""):
                candidate = raw.strip()
                if candidate.startswith("multica "):
                    out.append((idx, candidate))
            continue

        for span in INLINE_CODE.findall(raw):
            span = span.strip()
            if span.startswith("multica "):
                out.append((idx, span))

    return out


def normalize(line: str) -> list[str]:
    """Tokenize a documented invocation, dropping doc-syntax noise."""
    line = line.split(" #", 1)[0].strip()
    # `[--flag <v>]` optional markers and `a | b` alternation are doc syntax.
    line = line.replace("[", " ").replace("]", " ").replace("|", " ")
    try:
        return shlex.split(line)
    except ValueError:
        return line.split()


def resolve_path(tokens: list[str], top_level: set[str]) -> tuple[str, list[str], str | None] | None:
    """Split tokens into a valid command path, its flags, and a bad subcommand.

    Global flags may precede the command, so scan for the first token that names
    a top-level command. Then take the longest run of bare words that `--help`
    still accepts, so a positional value that happens to look like a word (e.g.
    `config set key`) is not mistaken for a subcommand.

    Walking back that way would also swallow a typo — `issue frobnicate` would
    quietly resolve to `issue`. So when the resolved path is a command *group*,
    the word that follows it had to be one of its subcommands; report it if not.
    """
    start = next((i for i, t in enumerate(tokens) if t in top_level), None)
    if start is None:
        return None

    words: list[str] = []
    for tok in tokens[start:]:
        if BARE_WORD.match(tok) and not PLACEHOLDER.match(tok):
            words.append(tok)
        else:
            break

    while words:
        path = " ".join(words)
        help_text = cli_help(path)
        if help_text is not None:
            flags = [t for t in tokens if t.startswith("-")]
            subs = declared_subcommands(help_text)
            leftover = tokens[start + len(words) :]
            bad_sub = None
            if subs and leftover and BARE_WORD.match(leftover[0]) and leftover[0] not in subs:
                bad_sub = leftover[0]
            return path, flags, bad_sub
        words.pop()
    return None


def check_validity(verbose: bool) -> list[str]:
    root_help = cli_help("")
    assert root_help is not None
    top_level = declared_subcommands(root_help)
    global_flags = declared_flags(root_help)

    errors: list[str] = []
    checked = 0

    for rel in DOC_FILES:
        path = REPO_ROOT / rel
        if not path.exists():
            errors.append(f"{rel}: listed in DOC_FILES but missing from the repo")
            continue

        for lineno, line in extract_command_lines(path.read_text(encoding="utf-8")):
            tokens = normalize(line)
            if not tokens or tokens[0] != "multica":
                continue

            resolved = resolve_path(tokens, top_level)
            if resolved is None:
                # Root-level invocation such as `multica --version`.
                bad = [f for f in tokens if f.startswith("-") and f not in global_flags]
                if bad:
                    errors.append(f"{rel}:{lineno}: unknown command or flags {bad} in: {line}")
                continue

            cmd_path, flags, bad_sub = resolved
            help_text = cli_help(cmd_path)
            assert help_text is not None
            allowed = declared_flags(help_text) | global_flags
            checked += 1

            if bad_sub is not None:
                errors.append(
                    f"{rel}:{lineno}: `multica {cmd_path}` has no subcommand `{bad_sub}`\n"
                    f"    in: {line}"
                )

            unknown = [f for f in flags if f not in allowed]
            if unknown:
                errors.append(
                    f"{rel}:{lineno}: `multica {cmd_path}` does not accept {', '.join(unknown)}\n"
                    f"    in: {line}"
                )
            elif verbose:
                print(f"  ok  {rel}:{lineno}  multica {cmd_path}")

    if verbose:
        print(f"\nvalidity: {checked} documented invocations resolved")
    return errors


def check_coverage(verbose: bool) -> list[str]:
    skill = (REPO_ROOT / COVERAGE_FILE).read_text(encoding="utf-8")
    root_help = cli_help("")
    assert root_help is not None

    errors: list[str] = []
    expected: list[str] = sorted(declared_subcommands(root_help))
    for sub in sorted(declared_subcommands(cli_help("issue") or "")):
        expected.append(f"issue {sub}")

    for name in expected:
        if name in UNDOCUMENTED_OK:
            continue
        # Always match on the full invocation: a bare namespace name like
        # "label" or "chat" would otherwise be satisfied by ordinary prose.
        needle = f"multica {name}"
        if needle not in skill:
            errors.append(
                f"{COVERAGE_FILE}: `multica {name}` exists in the CLI but is never mentioned.\n"
                f"    Document it, or add it to UNDOCUMENTED_OK in {Path(__file__).name} with a reason."
            )
        elif verbose:
            print(f"  ok  covered: multica {name}")

    stale = [k for k in UNDOCUMENTED_OK if k not in expected]
    for name in stale:
        errors.append(f"UNDOCUMENTED_OK lists `{name}`, which is no longer a CLI command — drop the entry.")

    if verbose:
        print(f"\ncoverage: {len(expected)} commands required, {len(UNDOCUMENTED_OK)} deliberately skipped")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--verbose", action="store_true", help="print every command as it is checked")
    args = parser.parse_args()

    if shutil.which("multica") is None:
        print(
            "error: the `multica` CLI is not on PATH.\n"
            "This lint compares the docs against the real CLI, so it needs the binary:\n"
            "  brew install multica-ai/tap/multica\n"
            "  # or: curl -fsSL https://raw.githubusercontent.com/multica-ai/multica/main/scripts/install.sh | bash",
            file=sys.stderr,
        )
        return 2

    try:
        version = subprocess.run(["multica", "version"], capture_output=True, text=True, timeout=30).stdout.strip()
        print(f"Linting docs against: {version.splitlines()[0] if version else 'multica (unknown version)'}\n")
        errors = check_validity(args.verbose) + check_coverage(args.verbose)
    except CliMissing:
        print("error: `multica` disappeared from PATH mid-run", file=sys.stderr)
        return 2

    if errors:
        print(f"\n{len(errors)} problem(s) found:\n", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        print(
            "\nThe docs have drifted from the CLI. Update them, or record the omission "
            "in UNDOCUMENTED_OK.",
            file=sys.stderr,
        )
        return 1

    print("OK — documented commands match the installed CLI.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
