---
title: Use Boot Structured Logging and Expose Only Needed Actuator Endpoints
impact: HIGH
impactDescription: JSON logs without custom encoders, and no accidental exposure of env or heap dumps
tags: [spring, logging, actuator, observability]
---

# Use Boot Structured Logging and Expose Only Needed Actuator Endpoints [HIGH]

## Description
Spring Boot has native structured logging: `logging.structured.format.console` accepts `ecs`, `logstash` or `gelf`. Use it so every line is JSON (see `logging-structured-json`). Expose only `health`, `info`, `prometheus` (and `metrics` if needed) over the web, secure the management port separately, and enable liveness/readiness probes for Kubernetes.

## Bad Example
```yaml
management:
  endpoints:
    web:
      exposure:
        include: "*" # env, heapdump, beans, configprops
```

## Good Example
```yaml
logging:
  structured:
    format:
      console: logstash
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus
  endpoint:
    health:
      probes:
        enabled: true
  server:
    port: 9090
```

## Notes
- The `logging.structured.format.*` properties apply to Boot's default logging configuration. A custom `logback-spring.xml` or Log4j2 config must opt in: Logback appenders need `org.springframework.boot.logging.logback.StructuredLogEncoder` with `<format>${CONSOLE_LOG_STRUCTURED_FORMAT}</format>`, and Log4j2 appenders need `<StructuredLogLayout format="${sys:CONSOLE_LOG_STRUCTURED_FORMAT}" charset="${sys:CONSOLE_LOG_CHARSET}"/>` in place of the `PatternLayout`.
- Exposing `prometheus` creates the endpoint only when `io.micrometer:micrometer-registry-prometheus` is on the runtime classpath; add it next to `spring-boot-starter-actuator`.
- Do not publish the management port through the public Service or ingress; restrict it with a NetworkPolicy to the scraper and probes. Bind `management.server.address=127.0.0.1` only when the sole client is a sidecar in the same pod, since a loopback bind refuses other pods and kubelet probes.
- Use Micrometer Tracing to put `traceId` and `spanId` in the MDC; they appear as JSON fields.
- Mask values with `management.endpoint.configprops.show-values=never` if configprops is ever exposed.

## References
- [Structured Logging](https://docs.spring.io/spring-boot/reference/features/logging.html#features.logging.structured)
- [Actuator endpoints](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html)
