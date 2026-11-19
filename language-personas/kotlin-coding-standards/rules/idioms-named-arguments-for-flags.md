---
title: Use Named Arguments for Booleans and Same-Typed Parameters
impact: MEDIUM
impactDescription: removes silent argument-order mistakes and unreadable call sites
tags: [idioms, api-design, readability]
---

# Use Named Arguments for Booleans and Same-Typed Parameters [MEDIUM]

## Description
A call like `send(msg, true, false)` hides intent, and swapped `String` arguments compile fine. Name boolean arguments and any run of same-typed parameters at the call site. Use default values instead of overloads. Replace boolean parameters with an enum when there are two or more.

## Bad Example
```kotlin
export(report, true, false)
transfer(from, to, amount)
```

## Good Example
```kotlin
export(report, includeHeader = true, compress = false)
transfer(from = source, to = target, amount = amount)
```

## Notes
- Default arguments replace Java-style overload sets; add `@JvmOverloads` only when Java callers need them.
- Prefer `value class` wrappers for ids so the compiler catches swaps.

## References
- [Named arguments](https://kotlinlang.org/docs/functions.html#named-arguments)
