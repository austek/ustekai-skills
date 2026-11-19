---
title: Inject Dependencies Through Constructors; Confine Koin to the Composition Root
impact: MEDIUM
impactDescription: services are plain classes, testable without a DI container
tags: [ktor, di, koin]
---

# Inject Dependencies Through Constructors; Confine Koin to the Composition Root [MEDIUM]

## Description
Ktor 3 ships an optional DI plugin (`ktor-server-di`); Koin (`koin-ktor`) is an alternative integration, used in the example below. Either way, declare bindings in one place, or wire dependencies by hand in the module function. Services take their collaborators through constructors and never call `get()` or `inject()` themselves, which is a service locator and hides dependencies. Handlers receive the already-built service as a parameter.

## Bad Example
```kotlin
class OrderService : KoinComponent {
    private val repo: OrderRepository by inject() // hidden dependency
}
```

## Good Example
```kotlin
import io.ktor.server.application.Application
import io.ktor.server.application.install
import io.ktor.server.routing.Route
import io.ktor.server.routing.routing
import org.koin.dsl.module
import org.koin.ktor.ext.inject
import org.koin.ktor.plugin.Koin
import javax.sql.DataSource

class OrderRepository(private val dataSource: DataSource)
class OrderService(private val repo: OrderRepository)

fun Route.orderRoutes(service: OrderService) { /* handlers */ }

fun dataSourceModule(dataSource: DataSource) = module { single { dataSource } }

val appModule = module {
    single { OrderRepository(get()) }
    single { OrderService(get()) }
}

fun Application.module(dataSource: DataSource) {
    install(Koin) { modules(dataSourceModule(dataSource), appModule) }
    val service by inject<OrderService>()
    routing { orderRoutes(service) } // resolved once at the edge
}
```

## Notes
- For small apps, plain constructor calls in `module()` need no library.
- Use `checkModules()` (Koin test) or a startup smoke test to catch missing bindings.

## References
- [Koin for Ktor](https://insert-koin.io/docs/reference/koin-ktor/ktor)
