---
name: retro
description: "Curate the lesson ledger: merge the lessons that sessions recorded, propose toolkit fixes as one PR, and check whether merged fixes stopped the mistake. Use for /retro, the daily retro routine, or 'what do agents keep getting wrong'."
---

# Retro

This is the curator of the toolkit's self-improvement loop. The roles are separate:

- **Record:** each session adds a lesson to the ledger when the user corrects it (`AGENTS.md`, Memory). `reflect` does the same for one conversation on request.
- **Curate:** retro reads the ledger, merges duplicates, proposes fixes, and checks the result of each fix.
- **Judge:** the user reviews and merges each PR. Retro never merges.

The rules:

- Every change to the toolkit goes through a PR that the user merges. Never push `main`.
- Memory needs no review. Save and update lessons without asking.
- You cannot edit the Agent Ensemble environment instructions. For a rule that belongs there, put the exact text in the report.

## The lesson ledger

Each lesson is one memory in the service that `AGENTS.md` names, with `shared` scope.

- The text starts with `[rsi-lesson:<key>]`. `<key>` is a short kebab-case name for the class of mistake, for example `push-without-asking`. Use the same key each time the same mistake occurs.
- Then: the rule in one sentence, the status, the occurrences, and the fix.
- Status is one of:
  - `open`: seen, no fix yet.
  - `proposed`: the fix is on the retro branch. Give the PR or compare link.
  - `fixed`: the fix PR is merged. Give the PR and the merge date.
  - `verified`: fixed, and not seen again for 14 days after the merge.
  - `regressed`: seen again in a session that started after the fix was merged.
  - `rejected`: the user closed the fix PR. Record the reason. Do not propose the same fix again.
- Occurrences: one line each, `<date> <session id>: <what the agent did> → <what the user wanted>`. Keep the last 10. Do not quote secrets or personal data. A one-time slip that the agent fixed at once is not a lesson.
- Tags: `rsi: lesson`, `key: <key>`, `status: <status>`.

To find a lesson, search memory for `rsi-lesson` plus the topic. Read the memory before you update it.

## 1. Read the ledger

Search memory for `rsi-lesson` (several queries, and `limit` 50). This is the main input. Note the occurrences added since the previous run. The routine prompt gives the previous run; with no previous run, use the last 24 hours.

## 2. Spot-check the sessions

Sessions can miss a lesson, so check a sample. Keep it small: the ledger is the record, not the transcripts.

- Take the user's sessions with activity since the previous run (`list_agents`, `owner` set to the user, sorted by `activity`). Skip the runs of this routine. Take at most 10.
- Read only the part after the previous run. `after` and `before` of `peek_agent` are event sequence numbers, not times: a time returns an empty page with no error. Use `budget` 4000 and at most 2 pages for each session.
  - If the previous report has a cursor for the session, read with `after` set to it.
  - Otherwise read the newest page (no `after` or `before`), then one more page with `before` set to the `older` value of that page.
- Look only at the user's messages and the agent's reply to each. Note each session's `last_seq` as its cursor for the report.
- Look for a correction, a rejected action, or a stated rule that is not in the ledger. Add each one as an occurrence.
- Use subagents for this, about five sessions each. Wait for all of them in the foreground before you continue. Do not end the turn while a subagent runs: the first final message of the run is its report.
- If you did not read all of a session's new part, write that in the report.

## 3. Curate the ledger

- Merge lessons that are the same class of mistake under different keys. Keep one key, move the occurrences to it, and archive the other memory.
- Check the PR of each `proposed` lesson: `gh api "repos/spinsirr/toolkit/pulls?state=all&head=corespeed-io:retro/next"`. Merged: set `fixed` with the merge date. Closed without a merge: set `rejected` with the reason, if the PR says.
- Set `regressed` for a `fixed` or `verified` lesson with an occurrence in a session that started after the merge.
- Set `verified` for a `fixed` lesson with no occurrence in the 14 days after the merge.

## 4. Choose what to fix

Propose a fix for a lesson when one of these is true:

- It has two or more occurrences.
- The user stated it as a rule.
- Its status is `regressed`.

For a `regressed` lesson, more text did not work. Use the **encode-lessons-in-structure** principle skill: a check in `tests/check.py`, or a change to the skill's steps. Do not add another sentence.

The toolkit has no hooks (user decision, 2026-11-07). Do not propose a hook, a `bin/` script or an MCP server in `plugin/`: `tests/check.py` fails on them, and the user closed PR #10 for this reason.

Route each fix to one place:

- A rule for one skill: that skill in `plugin/skills/`. A large edit goes through the **skill-creator** skill.
- A rule for all places: `AGENTS.md`. Keep `AGENTS.md` short: add one bullet, or merge into an existing one. Do not rewrite a section.
- A rule only for Agent Ensemble: the report, as exact text for the environment instructions.
- A fact that is not a rule: memory only. No PR.

Each fix states what must happen next: "`<key>` does not occur again in the 14 days after the merge." Put this line in the commit message. Step 3 of a later run checks it.

## 5. Update the retro branch

All fixes go on one branch, `retro/next`, on the fork `corespeed-io/toolkit`. Follow `add-to-toolkit` (when this session's repo is the fork, work in the workspace).

- If `retro/next` has an open PR, rebase it on `spinsirr/toolkit` main and add commits to it.
- Otherwise (no branch, or its PR is merged or closed), reset `retro/next` to `spinsirr/toolkit` main.
- Push with `--force-with-lease`. The Fork PRs workflow in `spinsirr/toolkit` opens the PR within about 15 minutes. Do not wait for it: give the PR link if it exists, or the compare link `https://github.com/spinsirr/toolkit/compare/main...corespeed-io:toolkit:retro/next?expand=1`.

## 6. Report

The final message, with no introduction:

1. **Regressed**: each `regressed` lesson, with the session that shows it.
2. **Proposed**: the PR link, and one line for each new fix with its lesson key.
3. **For the environment instructions**: exact text, if there is any.
4. **Verified**: lessons that changed to `verified` in this run.
5. **Ledger**: counts by status, the occurrences added since the previous run (by sessions, and by this run's spot-check), and the sessions that were not fully read.
6. **Cursors**: one line, `<session id>=<last_seq>` for each session that you read. The next run reads it from the continuity header.

If nothing changed, say so in one line.
