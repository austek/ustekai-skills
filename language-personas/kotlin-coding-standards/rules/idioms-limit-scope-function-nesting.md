---
title: Do Not Nest or Chain Scope Functions
impact: MEDIUM
impactDescription: nested let/run/apply make it unclear which receiver or `it` is in use
tags: [idioms, readability, scope-functions]
---

# Do Not Nest or Chain Scope Functions [MEDIUM]

## Description
`let`, `run`, `with`, `apply` and `also` are for one short, obvious step: `apply` to configure an object, `let` to map a nullable, `also` for a side effect. Nesting them shadows `it` and `this`. Replace nested scopes with named local values or a small function.

## Bad Example
```kotlin
class City(val name: String)
class Address(val city: City?)
class User(val address: Address?)

fun log(city: City) = println(city.name)
fun send(city: City) = println("sending ${city.name}")

fun notify(user: User?) {
    user?.let { u ->
        u.address?.let { a ->
            a.city?.let { c -> send(c.also { log(it) }) }
        }
    }
}
```

## Good Example
```kotlin
class City(val name: String)
class Address(val city: City?)
class User(val address: Address?)

fun log(city: City) = println(city.name)
fun send(city: City) = println("sending ${city.name}")

fun notify(user: User?) {
    val city = user?.address?.city ?: return
    log(city)
    send(city)
}
```

## Notes
- Use `apply` for builders and `also` for logging; do not use either to return a different value.
- Extension functions beat a scope function for a repeated pattern.

## References
- [Scope functions](https://kotlinlang.org/docs/scope-functions.html)
