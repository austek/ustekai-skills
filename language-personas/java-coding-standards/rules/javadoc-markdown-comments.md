---
title: Use Markdown Doc Comments for New Code on JDK 23+
impact: LOW
impactDescription: removes HTML tags and {@code} noise from source docs without changing the generated output
tags: [javadoc, markdown, java23]
---

# Use Markdown Doc Comments for New Code on JDK 23+ [LOW]

## Description
JEP 467 (final in JDK 23) lets doc comments be written in Markdown on lines that start with `///`. Markdown replaces `<p>`, `<ul>`, `<pre>` and `{@code ...}` with plain syntax, and block tags such as `@param`, `@return` and `@throws` work unchanged. The content rules in this skill still apply: summary first, no signature narration, tags only when they add information. Markdown changes the syntax, not what a comment should say.

## Bad Example
```java
/**
 * Returns the sum of {@code a} and {@code b}.
 * <p>
 * Overflow wraps silently, as with the {@code +} operator.
 */
static int add(int a, int b) { return a + b; }
```

## Good Example
```java
/// Returns the sum of `a` and `b`.
///
/// Overflow wraps silently, as with the `+` operator.
static int add(int a, int b) { return a + b; }
```

## Notes
- Use one style per file. Do not convert existing `/** */` comments in a mechanical-cleanup commit.
- Requires the project's `release` to be 23 or later, and a Javadoc tool and IDE that support it. Check formatters (google-java-format) and Checkstyle versions before adopting.
- Reference members with `[Foo#bar()]`; use fenced code blocks instead of `<pre>`.

## References
- [JEP 467: Markdown Documentation Comments](https://openjdk.org/jeps/467)
