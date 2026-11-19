---
title: Write KDoc as Prose and Avoid @param and @return Tags
impact: LOW
impactDescription: matches Kotlin's coding conventions and keeps docs readable in source
tags: [kdoc, documentation, conventions]
---

# Write KDoc as Prose and Avoid @param and @return Tags [LOW]

## Description
Kotlin's coding conventions say to avoid `@param` and `@return` in KDoc: describe parameters and results in the text and link to parameters with `[name]`. Keep a tag only when the description is too long to fit the flow of the text. Document every public member of a library, except overrides that add nothing. This agrees with the Java rules `javadoc-no-signature-narration` and `javadoc-param-return-tags-only-when-non-obvious`.

## Bad Example
```kotlin
/**
 * Returns the absolute value of the given number.
 * @param number The number to return the absolute value for.
 * @return The absolute value.
 */
fun abs(number: Int): Int
```

## Good Example
```kotlin
/** Returns the absolute value of the given [number]; `Int.MIN_VALUE` is returned unchanged. */
fun abs(number: Int): Int
```

## Notes
- Put the contract first: preconditions, side effects, thrown exceptions (`@throws` stays useful, since Kotlin has no checked exceptions).
- Use one-line `/** ... */` for short comments.
- `explicitApi()` requires visibility and types on public declarations, not KDoc; enforce KDoc coverage with detekt's `UndocumentedPublicClass` and `UndocumentedPublicFunction` on library modules only.

## References
- [Kotlin coding conventions: documentation comments](https://kotlinlang.org/docs/coding-conventions.html#documentation-comments)
