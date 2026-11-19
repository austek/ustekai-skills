---
title: Emit One JSON Object per Log Line With Stable Field Names
impact: HIGH
impactDescription: logs stay queryable in Loki and similar backends without regex parsing
tags: [logging, observability, json]
---

# Emit One JSON Object per Log Line With Stable Field Names [HIGH]

## Description
Production logs are data. Configure the logging backend (Logback with `logstash-logback-encoder`, Log4j2 `JsonTemplateLayout`) to write a single JSON object per line with fixed keys: `timestamp`, `level`, `logger`, `message`, `trace_id`, plus domain fields as separate keys. Multi-line stack traces go inside one `stack_trace` field. Parsing free text with regex breaks on every message change.

## Bad Example
```xml
<encoder>
  <pattern>%d{HH:mm:ss} %-5level %logger - %msg%n</pattern>
</encoder>
```
```java
log.info("Order " + orderId + " placed by " + customerId + " total=" + total);
```

## Good Example
```xml
<appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
  <encoder class="net.logstash.logback.encoder.LogstashEncoder"/>
</appender>
```
```java
log.atInfo()
   .addKeyValue("orderId", orderId)
   .addKeyValue("customerId", customerId)
   .addKeyValue("total", total)
   .log("order placed");
```

## Notes
- Fluent `addKeyValue` pairs reach the JSON only with logstash-logback-encoder 7.4 or later and a Logback version without the key-value bug (fixed in 1.3.12, 1.4.4 and 1.5.0). Spring Boot 3.4+ can emit JSON without an encoder via `logging.structured.format.console`.
- `LogstashEncoder` defaults to `@timestamp`, `logger_name` and `level`; rename them with `<fieldNames>` if the stable keys above are required.
- Write to stdout and let the platform ship it. No file appenders in containers.
- Keep `message` constant per event so it can be grouped and counted.
- Put `trace_id` and `span_id` in via MDC or OpenTelemetry instrumentation.
- Use ISO-8601 UTC timestamps.

## References
- [SLF4J fluent API](https://www.slf4j.org/manual.html#fluent)
- [logstash-logback-encoder](https://github.com/logfellow/logstash-logback-encoder)
