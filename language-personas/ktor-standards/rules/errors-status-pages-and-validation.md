---
title: Map Errors Centrally With StatusPages and Validate Bodies With RequestValidation
impact: HIGH
impactDescription: one consistent error shape; no stack traces or unvalidated input reaching handlers
tags: [ktor, errors, validation]
---

# Map Errors Centrally With StatusPages and Validate Bodies With RequestValidation [HIGH]

## Description
Install `StatusPages` once and map domain and framework exceptions to status codes and a stable error body. Install `RequestValidation` so a request body is checked when the handler calls `call.receive<T>()`; failures raise `RequestValidationException` there, so validation runs only for bodies the handler actually receives. Handlers then contain only the happy path. Log the exception once, server-side, and return a generic body for unexpected errors.

## Bad Example
```kotlin
import io.ktor.http.HttpStatusCode
import io.ktor.server.request.receive
import io.ktor.server.response.respond
import io.ktor.server.response.respondText
import io.ktor.server.routing.Route
import io.ktor.server.routing.post
import kotlinx.serialization.Serializable

@Serializable
data class NewOrder(val items: List<String>)

fun interface OrderPlacer { fun place(order: NewOrder): String }

fun Route.orders(service: OrderPlacer) {
    post("/orders") {
        try {
            val body = call.receive<NewOrder>()
            call.respond(service.place(body))
        } catch (e: Exception) {
            call.respondText(e.stackTraceToString(), status = HttpStatusCode.InternalServerError)
        }
    }
}
```

## Good Example
```kotlin
import io.ktor.http.HttpStatusCode
import io.ktor.server.application.Application
import io.ktor.server.application.install
import io.ktor.server.application.log
import io.ktor.server.plugins.BadRequestException
import io.ktor.server.plugins.NotFoundException
import io.ktor.server.plugins.PayloadTooLargeException
import io.ktor.server.plugins.UnsupportedMediaTypeException
import io.ktor.server.plugins.requestvalidation.RequestValidation
import io.ktor.server.plugins.requestvalidation.RequestValidationException
import io.ktor.server.plugins.requestvalidation.ValidationResult
import io.ktor.server.plugins.statuspages.StatusPages
import io.ktor.server.response.respond
import kotlin.coroutines.cancellation.CancellationException
import kotlinx.serialization.Serializable

@Serializable
data class NewOrder(val items: List<String>)

@Serializable
data class ErrorBody(val type: String, val title: String, val detail: String = "")

class OrderNotFound(val id: String) : RuntimeException("order not found")

fun Application.errorHandling() {
    install(RequestValidation) {
        validate<NewOrder> { if (it.items.isEmpty()) ValidationResult.Invalid("items must not be empty") else ValidationResult.Valid }
    }
    install(StatusPages) {
        exception<RequestValidationException> { call, e ->
            call.respond(HttpStatusCode.BadRequest, ErrorBody("invalid_request", "Invalid request", e.reasons.joinToString("; ")))
        }
        exception<BadRequestException> { call, _ -> call.respond(HttpStatusCode.BadRequest, ErrorBody("bad_request", "Bad request")) }
        exception<UnsupportedMediaTypeException> { call, _ ->
            call.respond(HttpStatusCode.UnsupportedMediaType, ErrorBody("unsupported_media_type", "Unsupported media type"))
        }
        exception<PayloadTooLargeException> { call, _ ->
            call.respond(HttpStatusCode.PayloadTooLarge, ErrorBody("payload_too_large", "Payload too large"))
        }
        exception<NotFoundException> { call, _ -> call.respond(HttpStatusCode.NotFound, ErrorBody("not_found", "Not found")) }
        exception<OrderNotFound> { call, _ -> call.respond(HttpStatusCode.NotFound, ErrorBody("not_found", "Not found")) }
        exception<Throwable> { call, e ->
            if (e is CancellationException) throw e
            call.application.log.error("unhandled", e)
            call.respond(HttpStatusCode.InternalServerError, ErrorBody("internal_error", "Internal error"))
        }
    }
}
```

## Notes
- `StatusPages` `exception<Throwable>` must rethrow `CancellationException`, otherwise cancelled requests turn into 500s (see `coroutines-rethrow-cancellation`).
- Register handlers for framework client errors such as `BadRequestException` so a malformed request returns 4xx. `StatusPages` picks the closest exception class, so they win over the `Throwable` fallback in any order; without them a malformed request is reported as a 500. `UnsupportedMediaTypeException` does not extend `BadRequestException`, so it needs its own 415 handler; register a handler for each other framework client-error exception you expect the same way.
- `ErrorBody` uses the RFC 9457 field names (`type`, `title`, `detail`) for consistency with other services.
- The example assumes the application also installs `ContentNegotiation` with JSON (see `serialization-content-negotiation-explicit-json`); without it `call.receive<NewOrder>()` and `call.respond(ErrorBody(...))` cannot (de)serialize.

## References
- [Status pages](https://ktor.io/docs/server-status-pages.html)
- [Request validation](https://ktor.io/docs/server-request-validation.html)
