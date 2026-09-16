#!/usr/bin/env python3
"""Claude Code PreToolUse hook for Edit|Write.

Blocks writes to protected paths:
  - application.yml / application-*.yml
  - **/db/**
  - **/sql/**
  - settings.xml
  - pom.xml

Reads JSON from stdin (tool_input.file_path), emits a decision JSON on block, exits 0 silently otherwise.

落位说明：本文件在骨架中位于 hooks/，建设时复制到目标仓库 .claude/hooks/guard_write.py。
PROTECTED_PATTERNS 按目标仓库实际保护清单增删，须与 CLAUDE.md §10 一致。
"""
import json
import os
import re
import sys

PROTECTED_PATTERNS = [
    re.compile(r"application(-[\w-]+)?\.yml$", re.IGNORECASE),
    re.compile(r"docs/db/", re.IGNORECASE),
    re.compile(r"(^|/)db/", re.IGNORECASE),
    re.compile(r"(^|/)sql/", re.IGNORECASE),
    re.compile(r"settings\.xml$", re.IGNORECASE),
    re.compile(r"pom\.xml$", re.IGNORECASE),
]

BLOCK_REASON_TEMPLATE = (
    "保护目录禁止写入：{path}\n"
    "如需变更，请在 openspec/changes/{change}/design.md 中显式声明，"
    "并经 Reviewer 审核通过后再由 hook 临时放行。"
)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or ""
    if not file_path:
        sys.exit(0)

    normalized = file_path.replace("\\", "/")

    for pattern in PROTECTED_PATTERNS:
        if pattern.search(normalized):
            decision = {
                "decision": "block",
                "reason": BLOCK_REASON_TEMPLATE.format(
                    path=file_path,
                    change="<active-change-id>",
                ),
            }
            print(json.dumps(decision, ensure_ascii=False))
            sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
