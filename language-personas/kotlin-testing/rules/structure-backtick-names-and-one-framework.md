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
import kotlin.test.Test
import kotlin.test.assertTrue

fun parse(input: String): Long? = input.toLongOrNull()

class ParseTest {
    @Test fun test1() { assertTrue(parse("x") == null) }
}
```

## Good Example
```kotlin
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import kotlin.test.assertEquals
import kotlin.test.assertNull

data class Price(val minorUnits: Long)

object PriceParser {
    fun parse(input: String): Price? =
        input.toBigDecimalOrNull()?.movePointRight(2)?.toLong()?.let(::Price)
}

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
