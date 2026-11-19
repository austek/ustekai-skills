---
title: Use Named Arguments for Booleans and Same-Typed Parameters
impact: MEDIUM
impactDescription: removes silent argument-order mistakes and unreadable call sites
tags: [idioms, api-design, readability]
---

# Use Named Arguments for Booleans and Same-Typed Parameters [MEDIUM]

## Description
A call like `send(msg, true, false)` hides intent, and swapped `String` arguments compile fine. Name boolean arguments and any run of same-typed parameters at the call site of Kotlin functions (Kotlin cannot use named arguments when calling Java methods, so wrap those in a Kotlin function). Use default values instead of overloads. Replace boolean parameters with an enum when there are two or more.

## Bad Example
```kotlin
fun export(report: String, includeHeader: Boolean, compress: Boolean) {}
fun transfer(from: String, to: String, amount: Long) {}

fun run(report: String, source: String, target: String, amount: Long) {
    export(report, true, false)
    transfer(source, target, amount)
}
```

## Good Example
```kotlin
fun export(report: String, includeHeader: Boolean, compress: Boolean) {}
fun transfer(from: String, to: String, amount: Long) {}

fun run(report: String, source: String, target: String, amount: Long) {
    export(report, includeHeader = true, compress = false)
    transfer(from = source, to = target, amount = amount)
}
```

## Notes
- Default arguments replace Java-style overload sets; add `@JvmOverloads` only when Java callers need them.
- Prefer `value class` wrappers for ids so the compiler catches swaps.

## References
- [Named arguments](https://kotlinlang.org/docs/functions.html#named-arguments)
