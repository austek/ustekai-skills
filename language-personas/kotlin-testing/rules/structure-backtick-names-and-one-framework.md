---
title: Use One Test Framework and Behavior-Describing Backtick Names
impact: MEDIUM
impactDescription: consistent, readable tests; one runner and one assertion style per module
tags: [junit5, kotest, naming, structure]
---

# Use One Test Framework and Behavior-Describing Backtick Names [MEDIUM]

## Description
Pick JUnit 5 with `kotlin.test` or AssertJ, or Kotest, per module, and do not mix assertion libraries in one file. Name tests as a sentence in backticks that states the behavior and condition. Keep one behavior per test.

## Bad Example
```kotlin
@Test fun test1() { assertTrue(parse("x") == null) }
```

## Good Example
```kotlin
class PriceParserTest {
    @Test
    fun `returns null when the input is not a number`() {
        assertNull(PriceParser.parse("x"))
    }

    @ParameterizedTest
    @CsvSource("1.5,150", "0.01,1")
    fun `converts decimal to minor units`(input: String, expected: Long) {
        assertEquals(expected, PriceParser.parse(input)?.minorUnits)
    }
}
```

## Notes
- Android instrumented tests (`androidTest`) cannot use backtick names with spaces on API levels below 30; use camelCase there.
- Kotest `FunSpec` or `BehaviorSpec` is fine; do not mix it with JUnit `@Test` in the same module.
- Use `@Nested inner class` in JUnit for grouping.

## References
- [Test code using JUnit in JVM](https://kotlinlang.org/docs/jvm-test-using-junit.html)
