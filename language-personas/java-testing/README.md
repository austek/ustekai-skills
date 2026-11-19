# Java Testing

Test-writing best practices for JUnit 5, AssertJ, Mockito, and Testcontainers, designed for AI agents and LLMs to write readable, maintainable, and trustworthy tests.

## Overview

This skill provides 26 rules across 6 categories (Testcontainers rules live in `jvm-testing`):

| Category | Prefix | Impact | Rules |
|----------|--------|--------|-------|
| Mockito | `mockito-` | HIGH | 6 |
| JUnit 5 Structure | `junit5-structure-` | HIGH | 5 |
| AssertJ Assertions | `assertj-` | HIGH | 4 |
| Fixtures | `fixtures-` | HIGH | 4 |
| Parameterized Tests | `parametrized-` | MEDIUM | 4 |
| Test Doubles | `test-doubles-` | MEDIUM | 3 |

## Structure

```
skills/java-testing/
├── SKILL.md              # Skill overview with all rule summaries
├── metadata.json         # Metadata (version, description)
├── README.md             # This file
└── rules/
    ├── _sections.md      # Section definitions
    ├── _template.md      # Rule template
    ├── mockito-*.md        # Mockito rules
    ├── junit5-structure-*.md # JUnit 5 Structure rules
    ├── assertj-*.md        # AssertJ Assertions rules
    ├── fixtures-*.md       # Fixtures rules
    ├── parametrized-*.md   # Parameterized Tests rules
    └── test-doubles-*.md   # Test Doubles rules
```

## Rules

### Mockito (HIGH)
- `mockito-argument-captor` - Use ArgumentCaptor to inspect call arguments
- `mockito-avoid-mocking-value-objects` - Never mock value objects
- `mockito-mock-boundaries-only` - Mock only architectural boundaries
- `mockito-spy-sparingly` - Use @Spy sparingly
- `mockito-strict-stubbing` - Rely on Mockito's strict stubbing
- `mockito-verify-behavior-not-implementation` - Verify behavior, not implementation

### JUnit 5 Structure (HIGH)
- `junit5-structure-aaa-pattern` - Structure tests with arrange-act-assert
- `junit5-structure-display-name` - Use @DisplayName for human-readable test names
- `junit5-structure-lifecycle-annotations` - Use lifecycle annotations for shared setup and teardown
- `junit5-structure-nested-test-classes` - Group related tests with @Nested
- `junit5-structure-one-assertion-concept` - Assert one behavioral concept per test

### AssertJ Assertions (HIGH)
- `assertj-assertthatthrownby` - Assert exceptions with assertThatThrownBy
- `assertj-extracting-for-collections` - Use extracting to assert on collection elements' fields
- `assertj-fluent-over-junit-asserts` - Prefer AssertJ's fluent assertions over JUnit's assertEquals
- `assertj-soft-assertions` - Use SoftAssertions to report every failure in one run

### Fixtures (HIGH)
- `fixtures-avoid-shared-mutable-fixtures` - Avoid shared mutable fixtures
- `fixtures-builder-for-test-data` - Use a test-data builder instead of telescoping constructors
- `fixtures-extension-for-shared-setup` - Extract cross-cutting setup into a JUnit extension
- `fixtures-test-instance-per-method-default` - Leave test instance lifecycle at per-method default

Testcontainers rules moved to `jvm-testing`.

### Parameterized Tests (MEDIUM)
- `parametrized-csv-source` - Use @CsvSource for compact scalar argument tables
- `parametrized-enum-source` - Use @EnumSource to cover a whole enum's cases
- `parametrized-method-source` - Use @MethodSource for complex parameterized arguments
- `parametrized-readable-display-names` - Give parameterized tests readable display names

### Test Doubles (MEDIUM)
- `test-doubles-dummy-stub-mock-distinction` - Know the difference between dummy, stub, and mock
- `test-doubles-fake-over-mock` - Prefer a fake over a mock for stateful collaborators
- `test-doubles-no-mocking-what-you-dont-own` - Don't mock types you don't own

## Related

- [java-coding-standards](../java-coding-standards/README.md) - General Java coding standards and best practices
- [java-tooling](../java-tooling/README.md) - Build, static analysis, CI quality gate, dependency management, and formatting rules

## Usage

This skill is automatically applied when working with test files (`src/test/**`, `*Test.java`, `*Tests.java`).
