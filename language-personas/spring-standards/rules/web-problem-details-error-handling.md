---
title: Return RFC 9457 Problem Details From a Central @RestControllerAdvice
impact: MEDIUM
impactDescription: clients get one consistent error shape and stack traces never reach them
tags: [spring, web, errors]
---

# Return RFC 9457 Problem Details From a Central @RestControllerAdvice [MEDIUM]

## Description
Handle exceptions in one `@RestControllerAdvice` and return `ProblemDetail` (RFC 9457). Map domain exceptions to a status, a stable `type`, and a short `detail`. Log the full exception once, server-side. Never return `e.getMessage()` for unexpected errors or expose stack traces.

## Bad Example
```java
@ExceptionHandler(Exception.class)
ResponseEntity<String> handle(Exception e) {
    return ResponseEntity.status(500).body(e.toString()); // leaks internals
}
```

## Good Example
```java
@RestControllerAdvice
class ApiErrors extends ResponseEntityExceptionHandler {
    @ExceptionHandler(OrderNotFound.class)
    ProblemDetail notFound(OrderNotFound e) {
        ProblemDetail p = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, "order not found");
        p.setType(URI.create("https://errors.example.com/order-not-found"));
        p.setProperty("orderId", e.id());
        return p;
    }
}
```

## Notes
- Set `spring.mvc.problemdetails.enabled=true` to get Problem Details for Spring's own exceptions.
- Keep the unexpected-error handler generic: status 500 and a correlation id.

## References
- [Error responses](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-rest-exceptions.html)
