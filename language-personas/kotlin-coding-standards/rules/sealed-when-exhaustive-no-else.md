---
title: Use Exhaustive when Over Sealed Types With No else Branch
impact: HIGH
impactDescription: adding a variant becomes a compile error at every unhandled site
tags: [sealed, when, type-safety]
---

# Use Exhaustive when Over Sealed Types With No else Branch [HIGH]

## Description
A `when` used as an expression over a `sealed` class, interface or `enum` must cover every case. An `else` branch hides new variants. Omit it so the compiler flags every site when a direct subtype is added. The guarantee covers only subtypes the compiler can tell apart: an `is A` branch for an open or non-sealed subtype `A` also matches any future subtype of `A`, so adding one raises no error.

## Bad Example
```kotlin
fun label(state: UiState): String = when (state) {
    is UiState.Loading -> "loading"
    else -> "other" // new variants silently land here
}
```

## Good Example
```kotlin
sealed interface UiState {
    data object Loading : UiState
    data class Success(val data: String) : UiState
    data class Failure(val error: Throwable) : UiState
}

fun label(state: UiState): String = when (state) {
    UiState.Loading -> "loading"
    is UiState.Success -> "ready"
    is UiState.Failure -> "failed"
}
```

## Notes
- Use `data object` for stateless variants.
- Use `when` as an expression (assign or return it) so exhaustiveness is enforced for non-sealed subjects too.

## References
- [Sealed classes and interfaces](https://kotlinlang.org/docs/sealed-classes.html)
