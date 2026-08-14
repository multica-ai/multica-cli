#!/usr/bin/env python3
"""Pin the portable Skill's business-orchestration behavior."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def require(path: str, anchors: list[str], failures: list[str]) -> None:
    target = ROOT / path
    if not target.is_file():
        failures.append(f"{path}: file is missing")
        return
    content = " ".join(target.read_text(encoding="utf-8").split())
    for anchor in anchors:
        if anchor not in content:
            failures.append(f"{path}: missing {anchor!r}")


def main() -> int:
    failures: list[str] = []

    require(
        "skills/multica-cli/SKILL.md",
        [
            "open-ended business goal",
            "references/orchestration.md",
            "Route by intent, not resource count",
        ],
        failures,
    )
    require(
        "skills/multica-cli/references/orchestration.md",
        [
            "targeted read-only discovery",
            "Issues, Projects, Agents, Squads, Skills, and Autopilots",
            "search or list first",
            "business context and available capabilities",
            "dedicated",
            "shared",
            "unknown",
            "Treat unknown as shared",
            "Prefer reuse over creating a duplicate",
            "The in-chat orchestration design is the execution plan",
            "one user confirmation",
            "execute the plan directly",
            "separate confirmation immediately before changing an Agent or Skill",
            "material deviation",
            "Multica Web",
        ],
        failures,
    )
    require(
        "README.md",
        [
            "targeted workspace discovery",
            "reuse existing work instead of rebuilding it",
            "one confirmation",
        ],
        failures,
    )
    require(
        "README.zh.md",
        [
            "定向检索",
            "避免重复建设",
            "一次确认",
        ],
        failures,
    )
    require(
        "EXAMPLES.md",
        [
            "Turn a business goal into an execution plan",
            "inspect relevant existing resources",
            "execute it after one confirmation",
        ],
        failures,
    )

    if failures:
        print(f"{len(failures)} orchestration contract check(s) failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("Business orchestration contract passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
