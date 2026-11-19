---
title: Test Routes With testApplication and the Real Module
impact: HIGH
impactDescription: tests exercise real plugins, routing and serialization without opening a port
tags: [ktor, testing]
---

# Test Routes With testApplication and the Real Module [HIGH]

## Description
`testApplication { }` boots the application in memory and gives a `client` that calls routes directly. Load the real module so tests cover the installed plugins (StatusPages, ContentNegotiation, validation), and replace only outward dependencies with fakes. The application starts on the first client call (or `startApplication()`), uses an in-memory engine from `ktor-server-test-host`, and needs no `runBlocking` wrapper.

## Bad Example
```kotlin
@Test
fun createsOrder() = runBlocking {
    val server = embeddedServer(Netty, port = 8080) { module() }.start() // real port, flaky parallel runs
}
```

## Good Example
```kotlin
@Test
fun `returns 404 for an unknown order`() = testApplication {
    application { module(orderService = FakeOrderService()) } // the production module; it installs the plugins
    val client = createClient { install(ContentNegotiation) { json() } }

    val response = client.get("/orders/missing")

    assertEquals(HttpStatusCode.NotFound, response.status)
}
```

## Notes
- Use `environment { config = MapApplicationConfig("payments.url" to "http://localhost") }` to inject test config.
- For database tests combine with Testcontainers (see `jvm-testing`).

## References
- [Ktor testing](https://ktor.io/docs/server-testing.html)
