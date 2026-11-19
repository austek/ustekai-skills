---
title: Never Use the Non-Null Assertion !!
impact: CRITICAL
impactDescription: removes the NullPointerException path Kotlin's type system otherwise closes
tags: [null-safety, errors]
---

# Never Use the Non-Null Assertion !! [CRITICAL]

## Description
`!!` converts a nullable into a thrown `NullPointerException`, throwing away the compile-time guarantee. Handle absence explicitly with `?.`, `?:`, `let`, `requireNotNull` (for a precondition, with a message) or by changing the type so the value cannot be null.

## Bad Example
```kotlin
val email = user.email!!
repository.find(id)!!.name
```

## Good Example
```kotlin
val email = user.email ?: return Result.failure(MissingEmail(user.id))
val name = repository.find(id)?.name ?: throw NotFound("user $id")
val config = requireNotNull(env["API_URL"]) { "API_URL must be set" }
```

## Notes
- Allowed in tests only, where a null is itself the failure.
- Prefer returning `Result` or a sealed type over throwing for expected absence.

## References
- [Kotlin null safety](https://kotlinlang.org/docs/null-safety.html)
