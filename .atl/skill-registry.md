# Skill Registry — Neuro Agent

Generated: 2026-05-23 | Source: ~/.config/opencode/skills/

## Project Skills

None yet. Create project-specific skills under `skills/` or `.atl/skills/`.

## User Skills

### branch-pr
- **Trigger**: creating, opening, or preparing PRs for review
- **Path**: `~/.config/opencode/skills/branch-pr/SKILL.md`
- **Rules**:
  - Every PR MUST link an approved issue — no exceptions
  - Every PR MUST have exactly one `type:*` label
  - Automated checks must pass before merge
  - Use `gh` for all GitHub operations
  - Return the PR URL when done

### chained-pr
- **Trigger**: PRs over 400 lines, stacked PRs, review slices
- **Path**: `~/.config/opencode/skills/chained-pr/SKILL.md`
- **Rules**:
  - Split PRs over 400 changed lines unless maintainer accepts `size:exception`
  - Keep each PR reviewable in ≤60 minutes
  - One deliverable work unit per PR; tests/docs with the unit they verify
  - State dependencies, follow-up, and out-of-scope in every chained PR
  - Every child PR must include a dependency diagram marking current PR with `📍`
  - Treat polluted diffs as base bugs: retarget or rebase

### cognitive-doc-design
- **Trigger**: writing guides, READMEs, RFCs, onboarding, architecture, review-facing docs
- **Path**: `~/.config/opencode/skills/cognitive-doc-design/SKILL.md`
- **Rules**:
  - Lead with the answer — decision/action/outcome first, context after
  - Progressive disclosure: happy path → details → edge cases → references
  - Chunking: group related info into small sections
  - Signposting: headings, labels, callouts so readers know where they are
  - Recognition over recall: prefer tables, checklists, templates over dense prose
  - Review empathy: design docs so reviewers can verify intent without reconstructing

### comment-writer
- **Trigger**: PR feedback, issue replies, reviews, Slack messages, GitHub comments
- **Path**: `~/.config/opencode/skills/comment-writer/SKILL.md`
- **Rules**:
  - Start with the actionable point, not a recap
  - Be warm and direct — thoughtful teammate, not corporate bot
  - Prefer 1-3 short paragraphs or a tight bullet list
  - Give technical reason when asking for a change
  - Comment on highest-value issue, not every preference
  - Match thread language: Spanish → Rioplatense (voseo)

### issue-creation
- **Trigger**: creating GitHub issues, bug reports, feature requests
- **Path**: `~/.config/opencode/skills/issue-creation/SKILL.md`
- **Rules**:
  - Blank issues are disabled — MUST use a template
  - Every issue gets `status:needs-review` automatically
  - Maintainer MUST add `status:approved` before any PR
  - Questions go to Discussions, not issues

### judgment-day
- **Trigger**: judgment day, dual review, adversarial review, juzgar
- **Path**: `~/.config/opencode/skills/judgment-day/SKILL.md`
- **Rules**:
  - Resolve project skills before launching agents
  - Launch two blind judges in parallel with identical target and criteria
  - Wait for both judges before synthesis; never accept a partial verdict
  - Classify warnings as WARNING (real) only if normal use triggers them
  - Ask before fixing Round 1 confirmed issues
  - After any fix, immediately re-launch both judges before commit/push
  - Terminal states: JUDGMENT: APPROVED or JUDGMENT: ESCALATED

### skill-creator
- **Trigger**: new skills, agent instructions, documenting AI usage patterns
- **Path**: `~/.config/opencode/skills/skill-creator/SKILL.md`
- **Rules**:
  - Skill is a runtime instruction contract for an LLM, not human documentation
  - References must point to local files
  - Target 180-450 body tokens, recommended max 700, hard max 1000
  - Keep description quoted, one physical line, trigger-first, ≤250 chars
  - Required structure: frontmatter, Activation Contract, Hard Rules, Decision Gates, Execution Steps, Output Contract, References

### work-unit-commits
- **Trigger**: implementation, commit splitting, chained PRs, keeping tests/docs with code
- **Path**: `~/.config/opencode/skills/work-unit-commits/SKILL.md`
- **Rules**:
  - Commit by work unit — a commit represents a deliverable behavior, fix, migration, or docs unit
  - Do not commit by file type (models → services → tests)
  - Keep tests with code — same commit as behavior they verify
  - Keep docs with the user-visible change they explain
  - Tell a story — reviewer should understand why each commit exists
