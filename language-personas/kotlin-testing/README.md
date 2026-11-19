# Kotlin Testing

Test-writing practices for Kotlin and coroutines, designed for AI agents and LLMs. JUnit 5, AssertJ and parameterized-test rules from [java-testing](../java-testing/SKILL.md) apply unchanged; Testcontainers rules are in [jvm-testing](../jvm-testing/SKILL.md).

## Overview

This skill provides 4 rules across 4 categories:

| Category | Prefix | Impact | Rules |
|----------|--------|--------|-------|
| Coroutines Testing | `coroutines-testing-` | HIGH | 1 |
| Flow Testing | `flow-testing-` | HIGH | 1 |
| Mocking | `mocking-` | MEDIUM | 1 |
| Structure | `structure-` | MEDIUM | 1 |

## Rules

### Coroutines & Flow (HIGH)
- `coroutines-testing-runtest` - Test suspend code with runTest and virtual time
- `flow-testing-turbine` - Assert Flow emissions with Turbine

### Test Doubles & Structure (MEDIUM)
- `mocking-prefer-fakes-over-mockk` - Prefer fakes over MockK; avoid relaxed mocks
- `structure-backtick-names-and-one-framework` - Use one test framework and behavior-describing backtick names

## Structure

```
kotlin-testing/
├── SKILL.md
├── metadata.json
├── README.md
└── rules/
    ├── _sections.md
    ├── _template.md
    └── <prefix>-<name>.md
```

## Related

- [kotlin-coding-standards](../kotlin-coding-standards/SKILL.md), [kotlin-tooling](../kotlin-tooling/SKILL.md)
