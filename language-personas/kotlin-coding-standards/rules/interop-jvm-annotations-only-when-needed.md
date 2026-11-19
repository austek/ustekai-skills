---
title: Add @Jvm Annotations Only When a Java Caller Needs Them
impact: LOW
impactDescription: keeps Kotlin APIs idiomatic and avoids annotation noise
tags: [interop, java, annotations]
---

# Add @Jvm Annotations Only When a Java Caller Needs Them [LOW]

## Description
`@JvmStatic`, `@JvmOverloads`, `@JvmField` and `@JvmName` shape the bytecode for Java callers. In a Kotlin-only module they add noise. Add them to the public API of a module that Java code consumes, and nowhere else. Use `@Throws` on functions Java must catch as checked exceptions.

## Bad Example
```kotlin
internal object Internals {
    @JvmStatic @JvmOverloads fun parse(text: String, strict: Boolean = false): Doc = TODO()
}
```

## Good Example
```kotlin
public object Parser {
    @JvmStatic
    @JvmOverloads
    @Throws(ParseException::class)
    public fun parse(text: String, strict: Boolean = false): Doc = TODO()
}
```

## Notes
- Prefer top-level functions over `object` members with `@JvmStatic`; Java sees them as static on `FileKt` (rename with `@file:JvmName`).
- `@JvmField` exposes a public field; use only for constants and DTOs Java frameworks populate.

## References
- [Calling Kotlin from Java](https://kotlinlang.org/docs/java-to-kotlin-interop.html)
