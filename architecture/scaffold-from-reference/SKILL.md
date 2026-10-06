---
name: scaffold-from-reference
description: >-
  Use when starting a new service, library, or repository, scaffolding a project skeleton, or deciding whether new work needs its own repo or belongs in an existing module.
---

# Scaffold From Reference

Copy a working repo's skeleton. Never rebuild one from memory.

## Conventions to resolve

Look these up in the user's `CLAUDE.md` or any installed house-conventions skill. Ask once if neither answers.

- **Reference repos:** one or two existing repos of the same kind, with local paths.
- **Owning team:** the code-owner handle for the new repo.
- **Review template:** the organisation's pull request template wording.

## 1. Gates

1. **Approved design.** A design doc with Status Accepted. Without one, stop and write it first.
2. **Repo or module?** Work that fits an existing module or service gets no scaffold: follow that codebase's own module conventions and stop here. A standalone repo continues below.

## 2. Copy, never recall

Read the reference repo's current files and copy their values: tool and plugin versions, plugin ids, CI library tags, runtime or toolchain versions, registry URLs, agent labels. Values from memory are wrong or stale.

## 3. Required parts

Match each part to the reference. Skip a part only when the reference lacks it.

| Part | Requirement |
|---|---|
| Versioning | The reference's versioning mechanism. Never hardcode a version. |
| Shared build conventions | A convention plugin or equivalent, not duplicated build logic |
| Dependency management | Version catalog and dependency locking |
| Quality gates | Coverage threshold, static analysis, license and security scans, as in the reference |
| CI pipeline | The reference's stages, copied |
| Runtime pin | The reference's toolchain or version file |
| Ownership | A code-owners file naming the owning team. References list another team; replace it. |
| Repo hygiene | Editor, line-ending, and ignore files |
| Docs | README (purpose, build, run), CONTRIBUTING (ticket, branch, commit rules), and a pull request template using the organisation's wording |
| Publish artefact | Read it from the design doc: library, executable, image, chart, or package. If silent, ask. |

Application code follows the language's standards skill if one is installed.

## 4. Git

Read how the versioning mechanism enforces commit messages before choosing a format. Branch and commit per the user's rules. Never commit or push unless asked.

## 5. Handoff (outward-facing, user confirms each)

Do not create these. List them: remote repository, CI job, code-quality project, security-scan project, publish credentials.

## 6. Done means

The project's build ran and passed. If it cannot resolve internal repositories, report that instead of claiming success, and mark the scaffold unbuilt.

## Common mistakes

- A hardcoded version where the versioning mechanism owns it.
- Inventing repository URLs, CI agent labels, or tool versions.
- Copying the reference's code owners unchanged.
- Choosing the commit format before reading the enforcement settings.
- Scaffolding a new repo when the work fits an existing module.
