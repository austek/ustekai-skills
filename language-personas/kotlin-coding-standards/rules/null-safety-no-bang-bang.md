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
class User(val id: String, val email: String?)
class Account(val name: String)
class Repository { fun find(id: String): Account? = null }

fun describe(user: User, repository: Repository, id: String): String {
    val email = user.email!!
    return email + repository.find(id)!!.name
}
```

## Good Example
```kotlin
class User(val id: String, val email: String?)
class Account(val name: String)
class Repository { fun find(id: String): Account? = null }
class MissingEmail(val userId: String) : Exception()
class NotFound(message: String) : Exception(message)

fun describe(user: User, repository: Repository, id: String, env: Map<String, String>): Result<String> {
    val email = user.email ?: return Result.failure(MissingEmail(user.id))
    val name = repository.find(id)?.name ?: throw NotFound("user $id")
    val config = requireNotNull(env["API_URL"]) { "API_URL must be set" }
    return Result.success("$email $name $config")
}
```

## Notes
- Allowed in tests only, where a null is itself the failure.
- Prefer returning `Result` or a sealed type over throwing for expected absence.

## References
- [Kotlin null safety](https://kotlinlang.org/docs/null-safety.html)
