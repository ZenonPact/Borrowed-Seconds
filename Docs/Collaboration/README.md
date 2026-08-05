# Collaboration workflow

This folder is the durable handoff between Alfonso and Codex. It keeps future
work sessions useful even when chat history is unavailable or has been
compacted.

## How we work

- Alfonso implements gameplay and Blueprint work hands-on whenever practical.
- Codex mentors with questions and small hints first, then gives exact steps
  when Alfonso is stuck.
- We explain the reason behind architectural choices, not only the node or code
  to add.
- We test one small behavior at a time before moving to the next feature.
- We profile before making performance changes.

## Documentation roles

- `CURRENT_STATE.md` records what is true about the project now: completed
  systems, work in progress, known issues, and the next task.
- `../PROJECT_MENTORING.md` records durable Unreal Engine concepts worth
  remembering. It is not a chronological diary.
- Commit messages and Git history remain the detailed chronological record.

## Before each commit

1. Save and compile the affected Unreal assets.
2. Test the changed behavior in Play mode.
3. Update `CURRENT_STATE.md` if project state or next steps changed.
4. Update `../PROJECT_MENTORING.md` only when a reusable concept was learned.
5. Review `git status` and commit only intentional files.

## Starting a future session

Read this file, then `CURRENT_STATE.md`, then the relevant section of
`../PROJECT_MENTORING.md`. Verify the working tree before changing files.

