---
title: Use Virtual Threads for Blocking I/O-Bound Work
impact: HIGH
impactDescription: thousands of concurrent blocking tasks instead of hundreds, with no reactive rewrite
tags: [concurrency, virtual-threads, io, scalability]
---

# Use Virtual Threads for Blocking I/O-Bound Work [HIGH]

## Description
Virtual threads (Java 21+, JEP 444) are cheap, JVM-scheduled threads designed for code that spends most of its time blocked on I/O — HTTP calls, JDBC queries, file access. Unlike platform threads, a blocked virtual thread unmounts from its carrier platform thread, so thousands can be blocked at once without exhausting OS threads. This makes ordinary blocking, sequential code scale like a reactive pipeline without the callback or `Mono`/`Flux` rewrite. Create one virtual thread per task and never pool them — pooling defeats the point, since creation is the cheap part and the platform-thread pool is what virtual threads exist to avoid. Reserve platform threads (sized near `Runtime.availableProcessors()`) for CPU-bound work, where virtual threads add scheduling overhead with no benefit.

## Bad Example
```java
// Fixed platform-thread pool throttles concurrent blocking I/O
ExecutorService pool = Executors.newFixedThreadPool(200);
for (Request request : requests) {
    pool.submit(() -> handle(request)); // blocks a scarce OS thread per call
}

// Pooling virtual threads defeats their purpose
ExecutorService vtPool = Executors.newFixedThreadPool(200, Thread.ofVirtual().factory());
```

## Good Example
```java
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (Request request : requests) {
        executor.submit(() -> handle(request)); // one virtual thread per task, unmounts while blocked
    }
} // close() awaits completion of submitted tasks
```

## Notes
- Never pool virtual threads; create a new one per task via `Thread.ofVirtual()` or `newVirtualThreadPerTaskExecutor()`.
- CPU-bound work gets no benefit from virtual threads — use a bounded platform-thread pool instead.
- On Java 24+ (JEP 491) a `synchronized` block no longer pins the virtual thread, so do not rewrite `synchronized` to `ReentrantLock` for that reason. Pinning remains during native frames and class initialization.
- On Java 21–23 a `synchronized` block performing a blocking call pins the carrier thread; prefer `ReentrantLock` there.
- Virtual threads are always daemon threads and cannot be prioritized like platform threads.

## References
- [JEP 444: Virtual Threads](https://openjdk.org/jeps/444)
- [JEP 491: Synchronize Virtual Threads without Pinning](https://openjdk.org/jeps/491)
