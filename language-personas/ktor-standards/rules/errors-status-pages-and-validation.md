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
post("/orders") {
    try {
        val body = call.receive<NewOrder>()
        call.respond(service.place(body))
    } catch (e: Exception) {
        call.respondText(e.stackTraceToString(), status = HttpStatusCode.InternalServerError)
    }
}
```

## Good Example
```kotlin
install(RequestValidation) {
    validate<NewOrder> { if (it.items.isEmpty()) ValidationResult.Invalid("items must not be empty") else ValidationResult.Valid }
}
install(StatusPages) {
    exception<RequestValidationException> { call, e ->
        call.respond(HttpStatusCode.BadRequest, ErrorBody("invalid_request", e.reasons))
    }
    exception<BadRequestException> { call, _ -> call.respond(HttpStatusCode.BadRequest, ErrorBody("bad_request")) }
    exception<OrderNotFound> { call, _ -> call.respond(HttpStatusCode.NotFound, ErrorBody("not_found")) }
    exception<Throwable> { call, e ->
        call.application.log.error("unhandled", e)
        call.respond(HttpStatusCode.InternalServerError, ErrorBody("internal_error"))
    }
}
```

## Notes
- `StatusPages` `exception<Throwable>` must rethrow `CancellationException`, otherwise cancelled requests turn into 500s (see `coroutines-rethrow-cancellation`).
- Register handlers for framework client errors such as `BadRequestException` so a malformed request returns 4xx. `StatusPages` picks the closest exception class, so they win over the `Throwable` fallback in any order; without them a malformed request is reported as a 500.
- Use RFC 9457 field names (`type`, `title`, `detail`) in `ErrorBody` for consistency with other services.

## References
- [Status pages](https://ktor.io/docs/server-status-pages.html)
- [Request validation](https://ktor.io/docs/server-request-validation.html)
