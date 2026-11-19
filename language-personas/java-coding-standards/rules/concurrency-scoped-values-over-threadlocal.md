---
title: Use ScopedValue Instead of ThreadLocal for Per-Request Context
impact: HIGH
impactDescription: immutable, bounded-lifetime context with no leak across pooled or virtual threads
tags: [concurrency, scoped-values, virtual-threads, java25]
---

# Use ScopedValue Instead of ThreadLocal for Per-Request Context [HIGH]

## Description
`ScopedValue` (final in Java 25, JEP 506) binds an immutable value for the dynamic extent of a call. The binding ends when the `run`/`call` returns, so it cannot leak into the next request on a reused thread, and child threads forked inside a `StructuredTaskScope` inherit it without copying. A `ThreadLocal` is mutable, lives until removed, and costs per-thread memory that adds up with millions of virtual threads.

## Bad Example
```java
private static final ThreadLocal<RequestContext> CTX = new ThreadLocal<>();

void handle(Request request) {
    CTX.set(RequestContext.from(request));
    try {
        service.process();
    } finally {
        CTX.remove(); // forgotten removal leaks context to the next request
    }
}
```

## Good Example
```java
private static final ScopedValue<RequestContext> CTX = ScopedValue.newInstance();

void handle(Request request) {
    ScopedValue.where(CTX, RequestContext.from(request))
        .run(service::process); // binding ends when run returns
}

// anywhere below service.process():
RequestContext ctx = CTX.get();
```

## Notes
- Requires JDK 25 or later. On JDK 21–24 it is a preview API; keep `ThreadLocal` there.
- Values are immutable. Rebind in a nested `where(...)` to change a value for an inner scope.
- Frameworks that own thread pools (Spring MVC filters, MDC) may still require `ThreadLocal`. Bridge at the boundary and keep application code on `ScopedValue`.

## References
- [JEP 506: Scoped Values](https://openjdk.org/jeps/506)
