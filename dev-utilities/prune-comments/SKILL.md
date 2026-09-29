---
name: prune-comments
description: >-
   Zero-tolerance comment eradication and structural refactoring. Enforces a strict
   "code speaks for itself" paradigm. Deletes ALL inline comments. If a comment 
   explains complex logic, a platform quirk, or a constraint, you MUST refactor the 
   code (extract methods, add runtime assertions, use custom exception messages, or rename 
   types) to make that reality executable or structurally obvious. 
   Takes an optional argument scoping the pass: a file or directory path, a PR 
   number/URL, a branch name, or "full repo"/"repo".
argument-hint: "[path|branch|#PR|full repo] (optional; defaults to uncommitted changes)"
---

# Prune Comments (Strict Zero-Tolerance)

Reviews every existing non-doc comment and deletes or refactors it. The codebase must
adhere strictly to clean code principles where executable architecture replaces narration.

## Scope

Resolve `$ARGUMENTS` to a target in this order — stop at the first match:

1. **No argument** → run `git status --porcelain`. Scope to uncommitted changes.
2. **A filesystem path** → scope to that path.
3. **A PR reference** → scope to files in that PR's branch.
4. **A branch name** → diff against merge base with `origin/HEAD` and scope to touched files.
5. **Whole-repo request** → the entire repo is in scope.

Regardless of scope, skip: `.git`, build/output dirs (`target`, `dist`), and vendored/generated code.

## The Bar: Total Deletion & Executable Refactoring

**ALL inline comments (`//`, `#`, `--`) fail the bar and MUST be deleted, except those listed under "What never gets touched".**

Instead of leaving comments, you must apply these transformations:

* **Restatements & Design Defenses:** Delete silently. Identifier names are the documentation.
* **Commented-out code:** Delete silently. Git history holds it.
* **Complex Logic:** You MUST refactor the code (extract methods, rename variables, simplify branching) to make the intent obvious.
* **Platform Quirks / Safety Constraints / Cross-file Facts:** You MUST encode these into the architecture. Translate the warning into a runtime assertion (`assert`, `require`), a highly descriptive custom exception message, or a dedicated, explicitly named wrapper method that isolates the quirk.
* **Comment-only bodies:** If deleting the comment leaves a body empty (`catch`/`except` block, no-op method, empty `else`/`match` arm, stub), never leave it empty or syntactically invalid. Apply the first that fits:
  1. Remove the construct if it is dead (empty `else`, empty override that only calls nothing).
  2. Give a swallowed error real handling: log, rethrow, or return an error value. Never turn a documented "ignore" into a silent swallow.
  3. Name the intent: extract a no-op helper (`ignoreShutdownFailure()`, `noOp()`), or rename the method/type so the emptiness is expected.
  4. Use the language's explicit empty form (`pass`, `...`, `()`, `{}`, `todo!()`/`unimplemented!()` for stubs) only when 1-3 do not apply.

## What never gets touched

- License/copyright headers.
- `SAFETY:` / `# Safety` comments strictly required above `unsafe` blocks.
- Formal doc comments (`///`, `/** */`, docstrings) — these define API contracts and are out of scope.
- Test-structure markers: `Given`, `When`, `Then` (also `Arrange`/`Act`/`Assert`) comments in test files, including forms like `// given`, `# When: ...`, `// then - ...`. Keep them in place and do not rewrite them.

## Process

1. Resolve scope from `$ARGUMENTS`.
2. For each file in scope, find every inline comment.
3. Edit in place: **Delete all inline comments.** Refactor code, extract methods, or add descriptive exception/assertion messages to absorb any critical constraints previously hidden in the comments. Do not add any new comments.
4. After editing a file, verify it still parses/compiles/lints cheaply.
5. Re-scan to ensure zero inline non-doc comments remain, other than the preserved ones.

## Reporting

Summarize per file: lines of comments eradicated, and list every structural refactor (method extractions, assertions added, exceptions renamed) performed to absorb load-bearing rationale.
