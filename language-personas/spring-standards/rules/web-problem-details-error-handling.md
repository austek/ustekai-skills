---
title: Return RFC 9457 Problem Details From a Central @RestControllerAdvice
impact: MEDIUM
impactDescription: clients get one consistent error shape and stack traces never reach them
tags: [spring, web, errors]
---

# Return RFC 9457 Problem Details From a Central @RestControllerAdvice [MEDIUM]

## Description
Targets Spring Boot 4.x (Spring Framework 7). Handle exceptions in one `@RestControllerAdvice` and return `ProblemDetail` (RFC 9457). Java services map domain exceptions to a status, a stable `type`, and a short `detail`. Kotlin services return sealed results for domain failures (see `error-handling-sealed-errors-over-exceptions` in kotlin-coding-standards) and map them to `ProblemDetail` in the controller; the advice then handles only framework exceptions and unexpected faults. Log the full exception once, server-side. Never return `e.getMessage()` for unexpected errors or expose stack traces.

## Bad Example
```java
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
class ApiErrors {
    @ExceptionHandler(Exception.class)
    ResponseEntity<String> handle(Exception e) {
        return ResponseEntity.status(500).body(e.toString()); // leaks internals
    }
}
```

## Good Example
```java
import java.net.URI;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.annotation.AnnotatedElementUtils;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

class OrderNotFound extends RuntimeException {
    private final String id;
    OrderNotFound(String id) { super("order not found"); this.id = id; }
    String id() { return id; }
}

@RestControllerAdvice
class ApiErrors extends ResponseEntityExceptionHandler {
    private static final Logger log = LoggerFactory.getLogger(ApiErrors.class);

    @ExceptionHandler(OrderNotFound.class)
    ProblemDetail notFound(OrderNotFound e) {
        ProblemDetail p = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, "order not found");
        p.setType(URI.create("https://errors.example.com/order-not-found"));
        p.setProperty("orderId", e.id());
        return p;
    }

    @ExceptionHandler(Exception.class)
    ProblemDetail unexpected(Exception e) throws Exception {
        if (AnnotatedElementUtils.hasAnnotation(e.getClass(), ResponseStatus.class)) {
            throw e; // let ResponseStatusExceptionResolver apply the declared status
        }
        String correlationId = UUID.randomUUID().toString();
        log.error("unhandled error {}", correlationId, e);
        ProblemDetail p = ProblemDetail.forStatusAndDetail(HttpStatus.INTERNAL_SERVER_ERROR, "unexpected error");
        p.setProperty("correlationId", correlationId);
        return p;
    }
}
```
```kotlin
import java.net.URI
import org.springframework.http.HttpStatus
import org.springframework.http.ProblemDetail
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RestController

data class OrderView(val id: String)

sealed interface FindOrderResult {
    data class Found(val order: OrderView) : FindOrderResult
    data class NotFound(val id: String) : FindOrderResult
}

fun interface OrderLookup { fun find(id: String): FindOrderResult }

@RestController
class OrderController(private val orders: OrderLookup) {
    @GetMapping("/orders/{id}")
    fun find(@PathVariable id: String): ResponseEntity<Any> =
        when (val result = orders.find(id)) {
            is FindOrderResult.Found -> ResponseEntity.ok(result.order)
            is FindOrderResult.NotFound -> ResponseEntity.status(HttpStatus.NOT_FOUND).body(
                ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, "order not found").apply {
                    type = URI.create("https://errors.example.com/order-not-found")
                    setProperty("orderId", result.id)
                },
            )
        }
```
With Spring Security, method security (`@PreAuthorize`) throws `AccessDeniedException` and `AuthenticationException` from inside the controller, so the catch-all handler would turn them into 500s. Rethrow them so Spring Security's handlers return the 403 or 401:
```java
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.AuthenticationException;

@ExceptionHandler(Exception.class)
ProblemDetail unexpected(Exception e) throws Exception {
    if (e instanceof AccessDeniedException
            || e instanceof AuthenticationException
            || AnnotatedElementUtils.hasAnnotation(e.getClass(), ResponseStatus.class)) {
        throw e; // let Spring Security or ResponseStatusExceptionResolver respond
    }
    // log and return the generic 500 ProblemDetail as in the example above
}
```

## Notes
- Set `spring.mvc.problemdetails.enabled=true` to get Problem Details for Spring's own exceptions.
- Keep the unexpected-error handler generic: status 500 and a correlation id.
- An `Exception.class` handler also catches exceptions annotated with `@ResponseStatus`, so the good example rethrows them for Spring's status resolver. The status is preserved, but the body comes from the container's `/error` handling, not Problem Details; map such exceptions with an explicit handler when clients need RFC 9457 bodies.
- The base example has no Spring Security dependency. Use the Spring Security variant when the application uses method security; the rethrown responses are not Problem Details unless you add explicit 403/401 handlers.

## References
- [Error responses](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-rest-exceptions.html)
