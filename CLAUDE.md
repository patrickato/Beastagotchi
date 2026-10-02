# CLAUDE.md — Beastagotchi

@AGENTS.md

The shared rules live in `AGENTS.md` (imported above), and they win over anything in this file.
This file only adds notes for Claude Code.

## Claude Code specifics

- **You act as Patrick on GitHub.** The GitHub MCP tools and the git proxy authenticate as
  `patrickato`.
  - The tools will let you merge, approve, close and change settings. AGENTS.md §4 forbids all
    of it.
  - Never call merge, review approve/request-changes, or settings endpoints.
- **Branch names.** A cloud session may assign you a branch, such as `claude/<random-words>`. Use
  it, and put the issue number in the PR header block rather than in the branch name.
- **Trailers.** Keep the harness's `Co-Authored-By:` and `Claude-Session:` lines, and add
  `AI-Agent: claude-code`.
- **As lead** (AGENTS.md §3):
  - Read the Beast Board at the start of each session and update it at the end.
  - Trigger Codex only as AGENTS.md §9 allows.
- **Scheduled runs (Routine).** Work in this order:
  1. Review `[openai]` PRs that are ready for review.
  2. Answer open review threads on `[claude]` PRs.
  3. Take at most one issue labelled `owner:claude` + `status:ready`.
  4. Update the Beast Board, including the merge digest and the interruption log.
- **Sibling repos** (`patrickato/plugins-wip`, `patrickato/test-plugins`,
  `patrickato/complete-plugins`) have their own CLAUDE.md files.
