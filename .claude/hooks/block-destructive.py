#!/usr/bin/env python3
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys

def blocked_reason(command):
    command = command or ''
    if re.search(r'\brm\s+-(?:rf|fr)\b', command, re.IGNORECASE):
        return 'rm -rf / rm -fr can recursively and forcibly delete data'
    if re.search(r'\bDROP\s+TABLE\b', command, re.IGNORECASE):
        return 'DROP TABLE can permanently remove a database table'
    if re.search(r'\bgit\s+push\b[^\n]*(?:--force(?:-with-lease)?|\s-f(?:\s|$))', command, re.IGNORECASE):
        return 'forced git push can rewrite shared history'
    if re.search(r'\bTRUNCATE(?:\s+TABLE)?\b', command, re.IGNORECASE):
        return 'TRUNCATE can remove all rows from a table'
    for statement in re.split(r'[;\n]+', command):
        if re.search(r'\bDELETE\s+FROM\b', statement, re.IGNORECASE) and not re.search(r'\bWHERE\b', statement, re.IGNORECASE):
            return 'DELETE FROM without a WHERE clause can remove every matching row'
    return None

def log_block(command, project_path, reason):
    log_dir = Path.home() / '.claude' / 'hooks'
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    safe_command = command.replace('\n', '\\n')
    with (log_dir / 'blocked.log').open('a', encoding='utf-8') as handle:
        handle.write(timestamp + '\tproject=' + project_path + '\treason=' + reason + '\tcommand=' + safe_command + '\n')

def deny(reason):
    print(json.dumps({
        'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': 'deny',
            'permissionDecisionReason': 'Destructive command blocked: ' + reason,
        }
    }))

def self_test():
    dangerous = [
        'rm -rf /tmp/example',
        'DROP TABLE users;',
        'git push --force origin main',
        'TRUNCATE TABLE sessions;',
        'DELETE FROM users;',
    ]
    safe = [
        'rm file.txt',
        'git push origin feature',
        'SELECT * FROM users;',
        'DELETE FROM users WHERE id = 42;',
        'npm test',
    ]
    assert all(blocked_reason(value) for value in dangerous)
    assert all(blocked_reason(value) is None for value in safe)
    print('self-test passed')

def main():
    if '--self-test' in sys.argv:
        self_test()
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if str(payload.get('tool_name', '')) != 'Bash':
        return 0
    tool_input = payload.get('tool_input') or {}
    command = str(tool_input.get('command', ''))
    reason = blocked_reason(command)
    if not reason:
        return 0
    project_path = str(payload.get('cwd') or os.environ.get('CLAUDE_PROJECT_DIR') or os.getcwd())
    log_block(command, project_path, reason)
    deny(reason)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
