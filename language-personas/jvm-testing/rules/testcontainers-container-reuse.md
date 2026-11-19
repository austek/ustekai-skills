---
title: Reuse Containers Across a Test Run Instead of Restarting Per Class
impact: HIGH
impactDescription: cuts integration suite wall time from minutes to seconds by amortizing container startup
tags: [testcontainers, performance, reuse, singleton-container]
---

# Reuse Containers Across a Test Run Instead of Restarting Per Class [HIGH]

## Description
Starting a fresh container (a Postgres, Kafka, or Redis instance) for every test class multiplies the same fixed startup cost — image pull, process boot, readiness wait — by the number of test classes, which dominates suite wall time once there are more than a handful of integration test classes. Two mechanisms address this. First, the "singleton container" pattern: start the container once in a `static` field (or a shared base class other test classes extend), so JUnit's class-level `static` initialization runs it once per JVM regardless of how many test classes use it, and let the JVM shutdown hook Testcontainers registers stop it — don't call `stop()` explicitly, or the next test class in the same JVM finds a dead container. Second, Testcontainers' own reuse feature (`withReuse(true)` plus `testcontainers.reuse.enable=true` in `~/.testcontainers.properties`) keeps a container alive *across separate test runs*, not just within one JVM, trading a small risk of state leaking between runs for a much faster local development loop.

Reuse is safe specifically for stateless-from-the-test's-perspective infrastructure — the container itself persists, but each test still needs to establish its own data state (via migration + per-test cleanup, or transactions rolled back per test) rather than depending on a clean container. Reusing a container is not a substitute for test isolation; it only removes container startup from the critical path, and the tests must still ensure they don't observe leftover data from a previous run.

CI environments typically disable `withReuse` (it's off by default outside explicit opt-in) since a CI job's containers don't survive between runs anyway — the singleton-per-JVM pattern is what actually matters for CI suite time, since a full JVM's worth of test classes still amortizes container cost within that one run.

## Bad Example
```java
class OrderRepositoryTest {
    @Container
    PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16"); // new container per class, no @Testcontainers reuse across suite
}

class CustomerRepositoryTest {
    @Container
    PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16"); // starts its own, duplicating the cost
}
```

## Good Example
```java
abstract class PostgresIntegrationTest {
    static final PostgreSQLContainer<?> POSTGRES = new PostgreSQLContainer<>("postgres:16");

    static {
        POSTGRES.start(); // started once per JVM, stopped by Testcontainers' shutdown hook
    }

    @DynamicPropertySource
    static void registerProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", POSTGRES::getJdbcUrl);
    }
}

class OrderRepositoryTest extends PostgresIntegrationTest { /* reuses POSTGRES */ }
class CustomerRepositoryTest extends PostgresIntegrationTest { /* reuses POSTGRES */ }
```

## Notes
- Each test still needs data isolation (a per-test schema, transaction rollback, or explicit cleanup) — a shared container is not a shared, safely-mutable fixture (`fixtures-avoid-shared-mutable-fixtures` applies to container-backed state too).
- `withReuse(true)` requires `testcontainers.reuse.enable=true` to be set explicitly; without it, the flag is silently ignored and the container stops as normal.
- The singleton pattern via a `static` field composes with `fixtures-test-instance-per-method-default`: the container is `static` deliberately (genuinely expensive, shared, and — given per-test data isolation — safe to share), the exception the rule anticipates.

## References
- [Testcontainers — Singleton Containers](https://java.testcontainers.org/test_framework_integration/manual_lifecycle_control/#singleton-containers)
- [Testcontainers — Reusable Containers](https://java.testcontainers.org/features/reuse/)
