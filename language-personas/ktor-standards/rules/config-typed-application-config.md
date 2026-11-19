---
title: Read Configuration Once Into a Typed Object From ApplicationConfig
impact: HIGH
impactDescription: missing settings fail at startup and the rest of the code never touches raw strings
tags: [ktor, configuration]
---

# Read Configuration Once Into a Typed Object From ApplicationConfig [HIGH]

## Description
Ktor reads `application.conf` (HOCON) or YAML into `ApplicationConfig`, with `${ENV_VAR}` substitution. Parse it once at startup into an immutable data class and pass that object to modules. Scattered `config.property("a.b").getString()` calls in handlers fail late and untyped.

## Bad Example
```kotlin
get("/pay") {
    val url = environment.config.property("payments.url").getString() // read per request
}
```

## Good Example
```kotlin
data class PaymentsConfig(val url: String, val timeout: Duration)

fun ApplicationConfig.payments() = PaymentsConfig(
    url = property("payments.url").getString(),
    timeout = property("payments.timeoutMs").getString().toLong().milliseconds,
)
```
```hocon
payments {
  url = ${PAYMENTS_URL}
  timeoutMs = 5000
}
```

## Notes
- Secrets come from environment variables or a secret manager, never committed config.
- `${?VAR}` makes a variable optional; use it only with a defined default.

## References
- [Ktor configuration](https://ktor.io/docs/server-configuration-file.html)
