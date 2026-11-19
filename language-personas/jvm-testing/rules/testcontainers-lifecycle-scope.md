---
title: Match Container Lifecycle Scope to What the Container Represents
impact: HIGH
impactDescription: prevents both wasted per-test restarts and cross-test state leaks through a shared container
tags: [testcontainers, lifecycle, scope, container]
---

# Match Container Lifecycle Scope to What the Container Represents [HIGH]

## Description
`@Testcontainers` plus `@Container` gives a container either per-test or per-class lifecycle depending on how the field is declared: an instance field (non-`static`) restarts the container before every `@Test` method, matching JUnit's default per-method test instance lifecycle (`fixtures-test-instance-per-method-default`); a `static` field starts the container once and shares it across every test method in the class, stopping it after the last one. Choosing between them is a question of what the container represents, not a performance knob to tune blindly.

A container that models genuinely per-test infrastructure — one test needs the database in a broken state to test a retry path, another needs it healthy — wants instance scope so each test starts clean. A container that models shared, always-available infrastructure a whole class's tests all read and write against different keys of — the common case for a database or message broker — wants class scope (`static`) so tests don't each pay full container startup cost, combined with the reuse pattern in `testcontainers-container-reuse` extended across classes. Getting this backwards in either direction causes a real problem: instance-scoped when it should be class-scoped wastes minutes restarting the same database for every test method; class-scoped when tests actually need isolation lets one test's leftover data corrupt another's assertions, the container equivalent of `fixtures-avoid-shared-mutable-fixtures`.

When a container is class-scoped, each test still must manage its own data isolation explicitly — a schema per test, a transaction rolled back in `@AfterEach`, or an explicit cleanup step — since the container being shared does not mean the data can be.

## Bad Example
```java
@Testcontainers
class OrderRepositoryTest {
    @Container
    PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16"); // instance field: restarts before every @Test
    // suite has 40 tests in this class — 40 container startups for infrastructure none of them mutate destructively
}
```

## Good Example
```java
@Testcontainers
class OrderRepositoryTest {
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16"); // static: one startup for the whole class

    @AfterEach
    void cleanUp() {
        jdbcTemplate.execute("TRUNCATE orders CASCADE"); // explicit per-test isolation, container itself is shared
    }
}
```

## Notes
- `@Testcontainers` wires the `@Container` fields into JUnit's lifecycle automatically — no manual `start()`/`stop()` calls needed for the common case, unlike the manual singleton pattern in `testcontainers-container-reuse` used to share a container across multiple classes.
- A non-`static` `@Container` field is the right default for a container that's cheap to start (a lightweight fake service) or where true per-test isolation at the infrastructure level is the point of the test.
- Combine class-scoped containers with an explicit wait strategy (`testcontainers-wait-strategy-explicit`) — a shared container's single startup is exactly where flaky readiness checks are most costly to get wrong, since every test in the class depends on it.

## References
- [Testcontainers — JUnit 5 Lifecycle](https://java.testcontainers.org/test_framework_integration/junit_5/)
