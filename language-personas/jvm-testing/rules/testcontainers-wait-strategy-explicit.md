---
title: Declare an Explicit Wait Strategy for Every Container
impact: HIGH
impactDescription: removes flaky "connection refused" failures caused by racing a container's real startup
tags: [testcontainers, wait-strategy, flakiness, startup]
---

# Declare an Explicit Wait Strategy for Every Container [HIGH]

## Description
A container process starting does not mean the service inside it is ready to accept connections — Postgres forks a second time during initialization, Kafka needs its broker to finish electing itself before accepting clients, a custom app image might take seconds after its process starts to open its listening port. Testcontainers' purpose-built modules (`PostgreSQLContainer`, `KafkaContainer`, and others) ship a sensible default wait strategy tuned to that image, so using them as-is is usually safe. A `GenericContainer` wrapping an arbitrary image has no such default beyond "the process started," which is not the same as "the service is ready" — tests that connect immediately after `start()` returns race the container's real startup and fail intermittently, exactly the kind of flakiness that's hardest to reproduce locally because local machines are often faster or slower than CI in ways that change whether the race is lost.

`waitingFor(...)` accepts a `WaitStrategy`: `Wait.forListeningPort()` (a port is accepting TCP connections — the weakest signal, since a port can accept connections before the app behind it is functional), `Wait.forHttp(path).forStatusCode(200)` (an HTTP endpoint returns the expected status), `Wait.forLogMessage(regex, times)` (a specific line appears in container logs — often the most reliable signal for an app that logs "started" or "ready"), or a combination via `Wait.forHttp(...).withStartupTimeout(Duration.ofSeconds(60))`.

Set an explicit, generous `startupTimeout` on any wait strategy used in CI — CI runners are frequently slower and more contended than local development machines, and a timeout tuned to local speed becomes a source of CI-only flakiness (`hunt-flaky-it` territory) once the runner is under load.

## Bad Example
```java
GenericContainer<?> app = new GenericContainer<>("my-app:latest")
    .withExposedPorts(8080);
app.start(); // returns once the process starts, not once the app is actually serving
restTemplate.getForEntity("http://localhost:" + app.getMappedPort(8080) + "/health", String.class); // races startup
```

## Good Example
```java
GenericContainer<?> app = new GenericContainer<>("my-app:latest")
    .withExposedPorts(8080)
    .waitingFor(
        Wait.forHttp("/health")
            .forStatusCode(200)
            .withStartupTimeout(Duration.ofSeconds(60))
    );
app.start(); // blocks until /health actually returns 200
```

## Notes
- Purpose-built modules like `PostgreSQLContainer` already wait on the database accepting connections correctly by default; only `GenericContainer` usage reliably needs a hand-specified strategy.
- `Wait.forLogMessage` is often the most precise signal for services that log a distinct "ready" line, since it directly reflects the application's own notion of readiness rather than inferring it from a port or endpoint.
- A missing or too-weak wait strategy is a common root cause behind container-backed integration tests that pass locally but flake in CI — check this first before assuming the flakiness is elsewhere.

## References
- [Testcontainers — Wait Strategies](https://java.testcontainers.org/features/startup_and_waits/)
