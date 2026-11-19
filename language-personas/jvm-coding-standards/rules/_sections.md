# Section Definitions

## Resource Management (resource-management)
**Impact:** CRITICAL

Acquire and release JVM and I/O resources deterministically.

**Rules:**
- `resource-management-connection-pool-not-raw` - Acquire database connections from a pool, never raw per call

## Concurrency (concurrency)
**Impact:** HIGH

Coordinate shared state and background work safely across threads and virtual threads.

**Rules:**
- `concurrency-avoid-double-checked-locking` - Avoid double-checked locking — use the holder idiom or computeIfAbsent
- `concurrency-immutable-shared-state` - Prefer immutability over synchronization for shared state
- `concurrency-thread-safety-documentation` - Document a class's thread-safety contract explicitly
- `concurrency-virtual-threads` - Use virtual threads for blocking I/O-bound work

## Logging (logging)
**Impact:** HIGH

Emit structured, safe, groupable logs.

**Rules:**
- `logging-no-sensitive-data` - Never log secrets, tokens or personal data
- `logging-parameterized-messages` - Log constant messages with structured fields, not string concatenation
- `logging-structured-json` - Emit one JSON object per log line with stable field names

## Reflection & Serialization (reflection-serialization)
**Impact:** HIGH

Configure serialization explicitly and avoid legacy mechanisms.

**Rules:**
- `reflection-serialization-jackson-explicit-config` - Configure Jackson's ObjectMapper explicitly, never rely on defaults
- `reflection-serialization-no-default-java-serialization` - Never use Java's built-in serialization for new code

## Performance (performance)
**Impact:** MEDIUM

**Rules:**
- `performance-avoid-autoboxing-hot-paths` - Avoid autoboxing in hot paths
