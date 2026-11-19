# JVM Coding Standards

Runtime-level coding rules shared by Java, Kotlin and Scala, designed for AI agents and LLMs. Load together with the language skill; examples are Java.

## Overview

This skill provides 11 rules across 5 categories:

| Category | Prefix | Impact | Rules |
|----------|--------|--------|-------|
| Resource Management | `resource-management-` | CRITICAL | 1 |
| Concurrency | `concurrency-` | HIGH | 4 |
| Logging | `logging-` | HIGH | 3 |
| Reflection & Serialization | `reflection-serialization-` | HIGH | 2 |
| Performance | `performance-` | MEDIUM | 1 |

## Rules

### Resource Management (CRITICAL)
- `resource-management-connection-pool-not-raw` - Acquire database connections from a pool, never raw per call

### Concurrency (HIGH)
- `concurrency-avoid-double-checked-locking` - Avoid double-checked locking — use the holder idiom or computeIfAbsent
- `concurrency-immutable-shared-state` - Prefer immutability over synchronization for shared state
- `concurrency-thread-safety-documentation` - Document a class's thread-safety contract explicitly
- `concurrency-virtual-threads` - Use virtual threads for blocking I/O-bound work

### Logging (HIGH)
- `logging-no-sensitive-data` - Never log secrets, tokens or personal data
- `logging-parameterized-messages` - Log constant messages with structured fields, not string concatenation
- `logging-structured-json` - Emit one JSON object per log line with stable field names

### Reflection & Serialization (HIGH)
- `reflection-serialization-jackson-explicit-config` - Configure Jackson's ObjectMapper explicitly, never rely on defaults
- `reflection-serialization-no-default-java-serialization` - Never use Java's built-in serialization for new code

### Performance (MEDIUM)
- `performance-avoid-autoboxing-hot-paths` - Avoid autoboxing in hot paths

## Structure

```
jvm-coding-standards/
├── SKILL.md              # Skill entry point and rule index
├── metadata.json         # Counts and sections
├── README.md             # This file
└── rules/
    ├── _sections.md      # Section definitions
    ├── _template.md      # Rule template
    └── <prefix>-<name>.md
```

## Applicability

- Java and Kotlin: all rules.
- Scala: all rules except Jackson-specific guidance if the project uses circe or another codec.

## Rule File Format

See `rules/_template.md`: front matter (`title`, `impact`, `impactDescription`, `tags`), then Description, Bad Example, Good Example, Notes, References.

## Related

- [java-coding-standards](../java-coding-standards/SKILL.md), [kotlin-coding-standards](../kotlin-coding-standards/SKILL.md), [scala-coding-standards](../scala-coding-standards/SKILL.md)
