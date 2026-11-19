---
title: Enable Virtual Threads With the Boot Property on JDK 21+
impact: MEDIUM
impactDescription: blocking MVC code scales on I/O without a reactive rewrite
tags: [spring, virtual-threads, concurrency]
---

# Enable Virtual Threads With the Boot Property on JDK 21+ [MEDIUM]

## Description
Spring Boot 3.2+ runs request handling, `@Async`, scheduling and messaging listeners on virtual threads when `spring.threads.virtual.enabled=true` and the JDK is 21+. Use it for blocking, I/O-bound services (JDBC, REST clients) instead of moving to WebFlux. Keep connection pools sized for the database: virtual threads remove the thread limit, not the connection limit.

## Bad Example
```yaml
server:
  tomcat:
    threads:
      max: 2000 # compensating for blocking I/O with platform threads
```

## Good Example
```yaml
spring:
  threads:
    virtual:
      enabled: true
  datasource:
    hikari:
      maximum-pool-size: 20
```

## Notes
- With the property on, the auto-configured `AsyncTaskExecutor` and scheduler become `SimpleAsyncTask*` types that start a virtual thread per task and ignore the `spring.task.*.pool.*` settings, so bound concurrency yourself.
- On JDK 24+ `synchronized` no longer pins virtual threads; on 21–23, avoid blocking inside `synchronized`.
- `ThreadLocal` context (security, MDC) works on the request thread as before but does not cross into `@Async` tasks unless a `TaskDecorator` propagates it; do not add new `ThreadLocal`s.
- Bound outbound concurrency with a `Semaphore` or the client's own limit.

## References
- [Spring Boot virtual threads](https://docs.spring.io/spring-boot/reference/features/task-execution-and-scheduling.html#features.task-execution-and-scheduling)
