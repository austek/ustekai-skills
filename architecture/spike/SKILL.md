---
name: spike
description: >-
  Use when asked "can we...", "is it feasible", "how far can X go", to POC or evaluate an approach, to time-box an investigation, or to write up spike or POC findings for a ticket or wiki page.
---

# Spike

Output is an answer, not code. Anything built is throwaway and labelled so.

## Conventions to resolve

Look these up in the user's `CLAUDE.md` or any installed house-conventions skill. Ask once if neither answers.

- **Draft location:** where the write-up is saved before publishing.
- **Publish target:** the wiki space or tracker the page goes to.
- **Ticket skill:** how follow-up tickets are created.

## 1. Frame (before investigating)

Write four lines and get a nod:

- **Question:** one sentence, answerable yes/no/number.
- **Decision it informs:** what the team does differently per answer.
- **Time-box:** days. Stop at the box and report what is known.
- **Probe:** the cheapest experiment that answers it. Prefer measuring over reading code, and the real system over a model of it.

If no decision hangs on the answer, say so and stop.

## 2. Investigate

Tag every finding as one of:

- **Measured:** observed in this spike, with environment and method.
- **Assumed:** taken from an earlier source; name it.
- **Not examined:** known unknown.

## 3. Write-up contract

Sections in this order. Every section is required; write "None" when empty.

| Section | Content |
|---|---|
| Verdict | Answer plus confidence in the first sentence. Say what would change it. |
| Why | Trigger and the decision it informs. Describe the customer or workload by its size and shape, not by name. |
| What we measured | Table: finding, value, environment, Measured/Assumed. |
| Outcome | **Unblock:** tickets needed now. **Follow-ups:** tickets not needed now. |
| Chose not to do | Option plus the reason it lost. |
| Still open | Not examined, plus who or what would close it. |
| Throwaway | Branch or files, labelled as not a base for production work. |
| Time-box | Planned vs used. |

"Chose not to do" is a decision with a reason. "Still open" is a gap. Never merge them.

## 4. Publish

Save the draft to the resolved draft location. Publishing to a wiki or tracker is outward-facing: show the draft and wait for a yes. Create follow-up tickets with the resolved ticket skill.

## Common mistakes

- Starting the probe before the question and time-box are written.
- Recommending from a gut estimate without saying it is one.
- Reporting local numbers as production numbers.
- Listing an untried option under "Chose not to do".
- Trusting a result without a completeness check: a truncated or empty result looks fast.
