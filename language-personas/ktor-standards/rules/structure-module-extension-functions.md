---
title: Structure a Ktor App as Application.module Extensions per Feature
impact: MEDIUM
impactDescription: features are testable in isolation and wiring stays in one readable place
tags: [ktor, structure, routing]
---

# Structure a Ktor App as Application.module Extensions per Feature [MEDIUM]

## Description
Declare each feature as an `Application.xyzModule()` extension that installs its plugins and routes, and list the modules in `application.conf` or compose them in one `module()`. Put route handlers in `Route.xyzRoutes(service)` functions that take their dependencies as parameters. Handlers stay thin and delegate to a service that knows nothing about Ktor.

## Bad Example
```kotlin
fun main() = embeddedServer(Netty, port = 8080) {
    routing {
        get("/orders/{id}") { /* SQL, mapping and HTTP all inline */ }
    }
}.start(wait = true)
```

## Good Example
```kotlin
import io.ktor.http.HttpStatusCode
import io.ktor.server.application.Application
import io.ktor.server.application.call
import io.ktor.server.application.install
import io.ktor.server.config.ApplicationConfig
import io.ktor.server.plugins.contentnegotiation.ContentNegotiation
import io.ktor.server.response.respond
import io.ktor.server.routing.Route
import io.ktor.server.routing.get
import io.ktor.server.routing.routing
import io.ktor.server.util.getOrFail
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.Serializable

@JvmInline value class OrderId(val value: String)
data class Order(val id: OrderId, val total: Long)

@Serializable
data class OrderView(val id: String, val total: Long)

fun Order.toView() = OrderView(id.value, total)

interface OrderService { suspend fun find(id: OrderId): Order? }

class AppDeps(val orderService: OrderService) {
    companion object {
        fun from(config: ApplicationConfig): AppDeps =
            AppDeps(object : OrderService { override suspend fun find(id: OrderId): Order? = null })
    }
}

fun Application.installPlugins() {
    install(ContentNegotiation) { json() }
}

fun Application.module() {
    val deps = AppDeps.from(environment.config)
    installPlugins()
    orderModule(deps.orderService)
}

fun Application.orderModule(service: OrderService) {
    routing { orderRoutes(service) }
}

fun Route.orderRoutes(service: OrderService) {
    get("/orders/{id}") {
        val id = call.parameters.getOrFail("id")
        service.find(OrderId(id))?.let { call.respond(it.toView()) }
            ?: call.respond(HttpStatusCode.NotFound)
    }
}
```

## Notes
- `getOrFail` throws a `MissingRequestParameterException`, which StatusPages maps to 400.
- Use `EngineMain` with `application.conf` in production for config-driven modules.

## References
- [Ktor modules](https://ktor.io/docs/server-modules.html)
