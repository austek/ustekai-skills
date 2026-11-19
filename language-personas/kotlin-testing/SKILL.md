---
name: kotlin-testing
description: Kotlin test-writing practices covering runTest and virtual time for coroutines, Turbine for Flow, MockK and fakes, and JUnit 5 or Kotest structure. Use when writing, reviewing, or refactoring Kotlin tests, adding coverage for suspend functions or Flow, or working under src/test.
paths:
  - "src/test/**/*.kt"
  - "**/*Test.kt"
  - "**/*Spec.kt"
---

# Kotlin Testing

Test rules for Kotlin and coroutines. Load with [jvm-testing](../jvm-testing/SKILL.md) for Testcontainers rules and [java-testing](../java-testing/SKILL.md) for JUnit 5, AssertJ and parameterized-test rules, which apply unchanged.

## Categories

### Coroutines & Flow [HIGH]
| Rule | Description |
|------|-------------|
| [coroutines-testing-runtest](rules/coroutines-testing-runtest.md) | Test suspend code with runTest and virtual time |
| [flow-testing-turbine](rules/flow-testing-turbine.md) | Assert Flow emissions with Turbine |

### Test Doubles & Structure [MEDIUM]
| Rule | Description |
|------|-------------|
| [mocking-prefer-fakes-over-mockk](rules/mocking-prefer-fakes-over-mockk.md) | Prefer fakes over MockK; avoid relaxed mocks |
| [structure-backtick-names-and-one-framework](rules/structure-backtick-names-and-one-framework.md) | Use one test framework and behavior-describing backtick names |

## See Also
- [kotlin-coding-standards](../kotlin-coding-standards/SKILL.md), [kotlin-tooling](../kotlin-tooling/SKILL.md)
