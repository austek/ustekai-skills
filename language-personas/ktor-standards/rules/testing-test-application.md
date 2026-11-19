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
import io.ktor.server.application.Application
import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Test

fun Application.module() {}

@Test
fun createsOrder() = runBlocking {
    val server = embeddedServer(Netty, port = 8080) { module() }.start() // real port, flaky parallel runs
    server.stop()
}
```

## Good Example
```kotlin
import io.ktor.client.request.get
import io.ktor.client.statement.bodyAsText
import io.ktor.http.HttpStatusCode
import io.ktor.serialization.kotlinx.json.json
import io.ktor.server.application.Application
import io.ktor.server.application.install
import io.ktor.server.plugins.NotFoundException
import io.ktor.server.plugins.contentnegotiation.ContentNegotiation
import io.ktor.server.plugins.statuspages.StatusPages
import io.ktor.server.response.respond
import io.ktor.server.routing.get
import io.ktor.server.routing.routing
import io.ktor.server.testing.testApplication
import io.ktor.server.util.getOrFail
import kotlin.test.assertEquals
import kotlinx.serialization.Serializable
import org.junit.jupiter.api.Test

@Serializable
data class OrderView(val id: String)

@Serializable
data class ErrorBody(val code: String, val message: String)

interface OrderService { fun find(id: String): OrderView? }

class FakeOrderService(private val orders: Map<String, OrderView> = emptyMap()) : OrderService {
    override fun find(id: String): OrderView? = orders[id]
}

fun Application.module(orderService: OrderService) {
    install(ContentNegotiation) { json() }
    install(StatusPages) {
        exception<NotFoundException> { call, e ->
            call.respond(HttpStatusCode.NotFound, ErrorBody("not_found", e.message.orEmpty()))
        }
    }
    routing {
        get("/orders/{id}") {
            val order = orderService.find(call.parameters.getOrFail("id")) ?: throw NotFoundException("order not found")
            call.respond(order)
        }
    }
}

class OrderRoutesTest {
    @Test
    fun `serializes a known order through ContentNegotiation`() = testApplication {
        application { module(orderService = FakeOrderService(mapOf("42" to OrderView("42")))) }

        val response = client.get("/orders/42")

        assertEquals(HttpStatusCode.OK, response.status)
        assertEquals("""{"id":"42"}""", response.bodyAsText())
    }

    @Test
    fun `maps an unknown order to a 404 body through StatusPages`() = testApplication {
        application { module(orderService = FakeOrderService()) }

        val response = client.get("/orders/missing")

        assertEquals(HttpStatusCode.NotFound, response.status)
        assertEquals("""{"code":"not_found","message":"order not found"}""", response.bodyAsText())
    }
}
```

## Notes
- Use `environment { config = MapApplicationConfig("payments.url" to "http://localhost") }` to inject test config.
- For database tests combine with Testcontainers (see `jvm-testing`).

## References
- [Ktor testing](https://ktor.io/docs/server-testing.html)
