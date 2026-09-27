# claude-review

A Claude Code powered sub-agent that reviews a GitHub pull request and posts a
structured Markdown review comment: summary, risks, suggestions, and a
confidence score.

## How it works

1. Fetches the PR title and unified diff via the GitHub CLI (`gh`).
2. Sends the diff to Claude Code (`claude -p`) with a fixed prompt template
   that forces a consistent Markdown structure.
3. Prints the review, optionally saves it to a file, and optionally posts it
   as a comment on the PR.

## Setup

1. Install the GitHub CLI and authenticate:
   ```bash
   gh auth login
   ```
2. Install Claude Code and make sure the `claude` binary is on your `PATH`
   (see https://docs.claude.com/en/docs/claude-code for install steps), then
   authenticate with your Anthropic account.
3. Make the script executable and put it on your `PATH`:
   ```bash
   chmod +x claude-review/claude_review.py
   ln -s "$(pwd)/claude-review/claude_review.py" /usr/local/bin/claude-review
   ```

## Usage

```bash
# Print a structured review to stdout
claude-review --pr https://github.com/owner/repo/pull/123

# Save the review to a file
claude-review --pr https://github.com/owner/repo/pull/123 --output review.md

# Generate the review and post it as a PR comment
claude-review --pr https://github.com/owner/repo/pull/123 --post

# Use a specific Claude model
claude-review --pr https://github.com/owner/repo/pull/123 --model claude-opus-4-6
```

## Output format

Every review follows this exact structure:

```markdown
## Summary
<2-3 sentence description of the change>

## Identified Risks
- <risk 1>
- <risk 2>

## Improvement Suggestions
- <suggestion 1>
- <suggestion 2>

## Confidence Score
<Low | Medium | High> - <justification>
```

## Sample outputs

See [`samples/sample-output-1.md`](samples/sample-output-1.md) and
[`samples/sample-output-2.md`](samples/sample-output-2.md) for example runs
against real, publicly available GitHub pull requests.

## Notes

- The tool only reads PR diffs and metadata; it never pushes commits or
  modifies repository content beyond optionally posting a single comment.
- `--post` requires `gh` to be authenticated with comment permissions on the
  target repository.
