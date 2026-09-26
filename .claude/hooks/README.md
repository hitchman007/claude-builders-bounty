# Claude Code destructive-command guard

A PreToolUse command hook that reads Claude Code JSON tool input from stdin and denies destructive Bash commands before they run.

## Install

One command:

    python3 .claude/hooks/install-block-destructive.py

The installer copies the hook to ~/.claude/hooks/block-destructive.py and idempotently registers it in ~/.claude/settings.json for Bash tool calls.

## Blocked patterns

- rm -rf / rm -fr
- DROP TABLE
- git push --force, --force-with-lease, or git push -f
- TRUNCATE
- DELETE FROM statements without a WHERE clause

Every blocked attempt is appended to ~/.claude/hooks/blocked.log with UTC timestamp, attempted command, project path, and reason. Safe commands emit no hook decision and continue through Claude Code's normal permission flow.

## Verify

    python3 .claude/hooks/block-destructive.py --self-test

On a blocked command the hook returns the Claude Code PreToolUse hookSpecificOutput object with permissionDecision set to deny and a clear permissionDecisionReason.
