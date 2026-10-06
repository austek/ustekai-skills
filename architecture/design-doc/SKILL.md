---
name: design-doc
description: >-
  Use when asked to write an ADR, architecture decision, design doc, or technical proposal, to choose between architectural options, or to draw C4, container, component, or sequence diagrams for a proposed change.
---

# Design Doc / ADR

One decision per page. A design doc is the ADR block plus the design sections the decision needs.

## Conventions to resolve

Look these up in the user's `CLAUDE.md` or any installed house-conventions skill. Ask once if neither answers.

- **Title and location:** default `docs/decisions/YYYY-MM-DD-<decision>.md` in the repo.
- **Diagram syntax:** use what the target renders. Mermaid for repo markdown and GitHub. PlantUML (C4-PlantUML) for wikis that have a PlantUML macro.
- **Architecture model:** an existing model (Structurizr, a C4 workspace) to link instead of redrawing.
- **Stakeholder roles and names:** who signs off.
- **Ticket skill:** how follow-up tickets are created.

## Page contract

Sections in this order, each required:

| Section | Content |
|---|---|
| Header | Authors, Stakeholders as an unchecked checklist, Date, Status (Proposed/Accepted/Superseded), Goal in one sentence, Related documents |
| Context | Current system and the problem, as cited facts |
| Decision | One sentence, stated before the options |
| Options | At least two, one being "do nothing" or the current state. Table scored against the stated constraints. |
| Consequences | Gains, costs, follow-up tickets |
| Diagrams | See below |
| Risks and mitigations | Risk, impact, mitigation |
| Open questions | Question, owner, due before build or before release |

Stakeholders are roles first: the architect for the area, a security reviewer (add whenever credentials, auth, tenant data, or network paths change), and the owning engineering manager. Look names up in the house conventions; never invent them.

Length: aim for 450 words plus diagrams. Detail beyond that goes in a linked child page.

## Diagrams

- **Always:** one C4 container diagram of the proposed state.
- **Add** a sequence diagram when three or more actors exchange messages.
- Skip the context level when an architecture model already shows it; link instead.

## Evidence

Every statement about the existing system cites a repo path, ticket, or page. A statement without a source is prefixed `Assumption:` and lands in Open questions. Never state a convention, API, or module as existing without checking it.

## Publish

Save the draft to the resolved location. Publishing is outward-facing: show the draft, wait for a yes, and leave stakeholder boxes unchecked. Create follow-up tickets with the resolved ticket skill.

## Common mistakes

- Options first, decision buried at the end.
- A diagram of the current state when the page proposes a change.
- Treating the engineer's preference as the decision before the unknowns are closed. Status stays Proposed.
- Describing implementation details (queues, page sizes) that the decision does not depend on.
