---
name: jvm-coding-standards
description: Language-neutral JVM coding standards shared by Java, Kotlin and Scala covering virtual threads, thread safety, immutability of shared state, Jackson configuration, serialization, connection pools, boxing in hot paths, and structured JSON logging. Use alongside java-coding-standards, kotlin-coding-standards or scala-coding-standards when writing or reviewing any JVM code, or when the user asks about JVM runtime, concurrency or logging practices.
paths:
  - "**/*.java"
  - "**/*.kt"
  - "**/*.kts"
  - "**/*.scala"
---

# JVM Coding Standards

Rules that hold for every JVM language. Load this skill together with the language skill (`java-`, `kotlin-` or `scala-coding-standards`); the language skill holds syntax-level rules, this one holds runtime-level rules. Examples are Java; the rule applies equally to Kotlin and Scala.

## Categories

### Concurrency [HIGH]
| Rule | Description |
|------|-------------|
| [concurrency-avoid-double-checked-locking](rules/concurrency-avoid-double-checked-locking.md) | Avoid double-checked locking — use the holder idiom or computeIfAbsent |
| [concurrency-immutable-shared-state](rules/concurrency-immutable-shared-state.md) | Prefer immutability over synchronization for shared state |
| [concurrency-thread-safety-documentation](rules/concurrency-thread-safety-documentation.md) | Document a class's thread-safety contract explicitly |
| [concurrency-virtual-threads](rules/concurrency-virtual-threads.md) | Use virtual threads for blocking I/O-bound work (JDK 21+; skip on older targets) |

### Logging [HIGH]
| Rule | Description |
|------|-------------|
| [logging-structured-json](rules/logging-structured-json.md) | Emit one JSON object per log line with stable field names |
| [logging-no-sensitive-data](rules/logging-no-sensitive-data.md) | Never log secrets, tokens or personal data |
| [logging-parameterized-messages](rules/logging-parameterized-messages.md) | Log constant messages with structured fields, not string concatenation |

### Resource Management [CRITICAL]
| Rule | Description |
|------|-------------|
| [resource-management-connection-pool-not-raw](rules/resource-management-connection-pool-not-raw.md) | Acquire database connections from a pool, never raw per call |

### Reflection & Serialization [HIGH]
| Rule | Description |
|------|-------------|
| [reflection-serialization-jackson-explicit-config](rules/reflection-serialization-jackson-explicit-config.md) | Configure Jackson's ObjectMapper explicitly, never rely on defaults |
| [reflection-serialization-no-default-java-serialization](rules/reflection-serialization-no-default-java-serialization.md) | Never use Java's built-in serialization for new code |

### Performance [MEDIUM]
| Rule | Description |
|------|-------------|
| [performance-avoid-autoboxing-hot-paths](rules/performance-avoid-autoboxing-hot-paths.md) | Avoid autoboxing in hot paths |

## See Also
- [java-coding-standards](../java-coding-standards/SKILL.md), [kotlin-coding-standards](../kotlin-coding-standards/SKILL.md), [scala-coding-standards](../scala-coding-standards/SKILL.md)
- [jvm-testing](../jvm-testing/SKILL.md), [jvm-tooling](../jvm-tooling/SKILL.md)
