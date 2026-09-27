#!/usr/bin/env python3
"""claude-review: analyze a GitHub PR diff with Claude Code and post a
structured Markdown review comment.

Usage:
    claude-review --pr https://github.com/owner/repo/pull/123
    claude-review --pr https://github.com/owner/repo/pull/123 --output review.md
    claude-review --pr https://github.com/owner/repo/pull/123 --post

Requirements:
    - GitHub CLI (`gh`) installed and authenticated: https://cli.github.com
    - Claude Code CLI (`claude`) installed and authenticated:
      https://docs.claude.com/en/docs/claude-code
"""
import argparse
import re
import shutil
import subprocess
import sys

PROMPT_TEMPLATE = """You are a senior code reviewer. You will be given a unified diff for a GitHub pull request titled "{title}" ({url}).

Analyze the diff and respond with ONLY a Markdown document using exactly this structure:

## Summary
<2-3 sentences describing what the change does>

## Identified Risks
- <risk 1>
- <risk 2>
(use "- None identified" if there truly are none)

## Improvement Suggestions
- <suggestion 1>
- <suggestion 2>

## Confidence Score
<Low | Medium | High> - <one sentence justification>

Do not include any text outside this structure. Here is the diff:

```diff
{diff}
```
"""


def parse_pr_url(url):
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+)/pull/(\d+)", url.strip())
    if not m:
        raise ValueError(f"Not a valid GitHub PR URL: {url}")
    owner, repo, number = m.groups()
    return owner, repo, number


def require_binary(name, hint):
    if shutil.which(name) is None:
        print(f"error: '{name}' not found on PATH. {hint}", file=sys.stderr)
        sys.exit(1)


def run(cmd, input_text=None):
    result = subprocess.run(
        cmd, input=input_text, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"command failed: {' '.join(cmd)}")
    return result.stdout


def fetch_pr_title(owner, repo, number):
    out = run([
        "gh", "api", f"repos/{owner}/{repo}/pulls/{number}", "--jq", ".title",
    ])
    return out.strip()


def fetch_pr_diff(url):
    return run(["gh", "pr", "diff", url])


def generate_review(url, title, diff, model=None):
    prompt = PROMPT_TEMPLATE.format(title=title, url=url, diff=diff)
    cmd = ["claude", "-p", prompt]
    if model:
        cmd += ["--model", model]
    return run(cmd).strip()


def post_comment(url, body_text):
    return run(["gh", "pr", "comment", url, "--body", body_text])


def main(argv=None):
    parser = argparse.ArgumentParser(prog="claude-review", description=__doc__)
    parser.add_argument("--pr", required=True, help="GitHub PR URL, e.g. https://github.com/owner/repo/pull/123")
    parser.add_argument("--output", help="Write the review Markdown to this file")
    parser.add_argument("--post", action="store_true", help="Post the review as a comment on the PR")
    parser.add_argument("--model", help="Optional Claude model override passed to `claude --model`")
    args = parser.parse_args(argv)

    require_binary("gh", "Install from https://cli.github.com and run `gh auth login`.")
    require_binary("claude", "Install Claude Code and ensure `claude` is on PATH.")

    owner, repo, number = parse_pr_url(args.pr)
    print(f"Fetching PR #{number} from {owner}/{repo}...", file=sys.stderr)
    title = fetch_pr_title(owner, repo, number)
    diff = fetch_pr_diff(args.pr)

    print("Analyzing diff with Claude...", file=sys.stderr)
    review = generate_review(args.pr, title, diff, model=args.model)

    print(review)

    if args.output:
        with open(args.output, "w") as f:
            f.write(review + "\n")
        print(f"Saved review to {args.output}", file=sys.stderr)

    if args.post:
        post_comment(args.pr, review)
        print("Posted review as a PR comment.", file=sys.stderr)


if __name__ == "__main__":
    main()
