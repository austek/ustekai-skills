# Section Definitions

## Mockito (mockito)
**Impact:** HIGH

Mock only architectural boundaries, with strict, verifiable stubbing.

**Rules:**
- `mockito-argument-captor` - Use ArgumentCaptor to inspect call arguments
- `mockito-avoid-mocking-value-objects` - Never mock value objects
- `mockito-mock-boundaries-only` - Mock only architectural boundaries
- `mockito-spy-sparingly` - Use @Spy sparingly
- `mockito-strict-stubbing` - Rely on Mockito's strict stubbing
- `mockito-verify-behavior-not-implementation` - Verify behavior, not implementation

## JUnit 5 Structure (junit5-structure)
**Impact:** HIGH

Structure JUnit 5 tests for clarity: one behavior per test, explicit lifecycle, readable names.

**Rules:**
- `junit5-structure-aaa-pattern` - Structure tests with arrange-act-assert
- `junit5-structure-display-name` - Use @DisplayName for human-readable test names
- `junit5-structure-lifecycle-annotations` - Use lifecycle annotations for shared setup and teardown
- `junit5-structure-nested-test-classes` - Group related tests with @Nested
- `junit5-structure-one-assertion-concept` - Assert one behavioral concept per test

## AssertJ Assertions (assertj)
**Impact:** HIGH

Write fluent, complete AssertJ assertions instead of terse JUnit asserts.

**Rules:**
- `assertj-assertthatthrownby` - Assert exceptions with assertThatThrownBy
- `assertj-extracting-for-collections` - Use extracting to assert on collection elements' fields
- `assertj-fluent-over-junit-asserts` - Prefer AssertJ's fluent assertions over JUnit's assertEquals
- `assertj-soft-assertions` - Use SoftAssertions to report every failure in one run

## Fixtures (fixtures)
**Impact:** HIGH

Build and share test data and setup without hidden shared mutable state.

**Rules:**
- `fixtures-avoid-shared-mutable-fixtures` - Avoid shared mutable fixtures
- `fixtures-builder-for-test-data` - Use a test-data builder instead of telescoping constructors
- `fixtures-extension-for-shared-setup` - Extract cross-cutting setup into a JUnit extension
- `fixtures-test-instance-per-method-default` - Leave test instance lifecycle at per-method default

## Parameterized Tests (parametrized)
**Impact:** MEDIUM

Replace duplicated test methods with parameterized sources and readable case names.

**Rules:**
- `parametrized-csv-source` - Use @CsvSource for compact scalar argument tables
- `parametrized-enum-source` - Use @EnumSource to cover a whole enum's cases
- `parametrized-method-source` - Use @MethodSource for complex parameterized arguments
- `parametrized-readable-display-names` - Give parameterized tests readable display names

## Test Doubles (test-doubles)
**Impact:** MEDIUM

Choose the right test double for the job and avoid mocking types you don't own.

**Rules:**
- `test-doubles-dummy-stub-mock-distinction` - Know the difference between dummy, stub, and mock
- `test-doubles-fake-over-mock` - Prefer a fake over a mock for stateful collaborators
- `test-doubles-no-mocking-what-you-dont-own` - Don't mock types you don't own
