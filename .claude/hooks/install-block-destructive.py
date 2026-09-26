#!/usr/bin/env python3
import json
from pathlib import Path
import shutil
import sys

def main():
    here = Path(__file__).resolve().parent
    source = here / 'block-destructive.py'
    if not source.exists():
        print('block-destructive.py is missing', file=sys.stderr)
        return 1
    hook_dir = Path.home() / '.claude' / 'hooks'
    hook_dir.mkdir(parents=True, exist_ok=True)
    target = hook_dir / 'block-destructive.py'
    shutil.copyfile(source, target)
    target.chmod(0o755)
    settings_path = Path.home() / '.claude' / 'settings.json'
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as exc:
            print('Refusing to overwrite invalid settings JSON: ' + str(exc), file=sys.stderr)
            return 1
    else:
        settings = {}
    if not isinstance(settings, dict):
        print('Claude settings root must be a JSON object', file=sys.stderr)
        return 1
    hooks = settings.setdefault('hooks', {})
    pre = hooks.setdefault('PreToolUse', [])
    command = 'python3 ' + json.dumps(str(target))
    entry = {
        'matcher': 'Bash',
        'hooks': [{'type': 'command', 'command': command}],
    }
    already = any(
        isinstance(group, dict)
        and any(
            isinstance(handler, dict) and handler.get('command') == command
            for handler in group.get('hooks', [])
        )
        for group in pre
    )
    if not already:
        pre.append(entry)
    settings_path.write_text(json.dumps(settings, indent=2) + '\n', encoding='utf-8')
    print('Installed hook at ' + str(target))
    print('Updated ' + str(settings_path))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
