---
title: Add CallId, CallLogging With MDC and JSON Output
impact: HIGH
impactDescription: every request log line carries a correlation id and is machine-parseable
tags: [ktor, logging, observability]
---

# Add CallId, CallLogging With MDC and JSON Output [HIGH]

## Description
Install `CallId` to read or generate a request id, `CallLogging` with `callIdMdc("call-id")` to put it in the MDC, and a Logback JSON encoder so each line is structured (see `logging-structured-json`). Filter noisy paths like health checks and never log request bodies or authorization headers.

## Bad Example
```kotlin
install(CallLogging) // plain text lines, no correlation id
```

## Good Example
```kotlin
install(CallId) {
    header(HttpHeaders.XRequestId)
    generate { UUID.randomUUID().toString() }
    verify { it.isNotBlank() }
}
install(CallLogging) {
    level = Level.INFO
    callIdMdc("call-id")
    filter { call -> !call.request.path().startsWith("/health") }
}
```
```xml
<appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
  <encoder class="net.logstash.logback.encoder.LogstashEncoder"/>
</appender>
```

## Notes
- Add the `ktor-server-call-id` and `ktor-server-call-logging` artifacts. The default `verify` accepts only lowercase letters, digits and `+/=-`; set your own `verify` if clients send other characters.
- MDC is thread-local; coroutines need `MDCContext()` from `kotlinx-coroutines-slf4j` when they hop threads.
- Return the call id in the `X-Request-Id` response header so clients can quote it.

## References
- [Ktor CallLogging](https://ktor.io/docs/server-call-logging.html)
- [Ktor CallId](https://ktor.io/docs/server-call-id.html)
