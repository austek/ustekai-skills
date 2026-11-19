---
name: jvm-testing
description: Language-neutral JVM test practices shared by Java, Kotlin and Scala covering Testcontainers lifecycle, container reuse and wait strategies. Use alongside java-testing, kotlin-testing or scala-testing when a test needs a real database, broker or service container, or when the user asks about integration-test infrastructure on the JVM.
paths:
  - "src/test/**"
  - "src/integrationTest/**"
---

# JVM Testing

Integration-test rules shared by every JVM language. Load together with the language testing skill.

## Categories

### Testcontainers [HIGH]
Run real dependencies in tests with correctly scoped container lifecycle and explicit wait strategies.

| Rule | Description |
|------|-------------|
| [testcontainers-container-reuse](rules/testcontainers-container-reuse.md) | Reuse containers across a test run instead of restarting per class |
| [testcontainers-lifecycle-scope](rules/testcontainers-lifecycle-scope.md) | Match container lifecycle scope to what the container represents |
| [testcontainers-wait-strategy-explicit](rules/testcontainers-wait-strategy-explicit.md) | Declare an explicit wait strategy for every container |

## Quick Reference
```java
GenericContainer<?> app = new GenericContainer<>("my-app:latest")
    .withExposedPorts(8080)
    .waitingFor(Wait.forHttp("/health")
        .forStatusCode(200)
        .withStartupTimeout(Duration.ofSeconds(60)));
app.start(); // blocks until /health actually returns 200
```

## See Also
- [java-testing](../java-testing/SKILL.md), [kotlin-testing](../kotlin-testing/SKILL.md), [scala-testing](../scala-testing/SKILL.md)
- [jvm-coding-standards](../jvm-coding-standards/SKILL.md)
