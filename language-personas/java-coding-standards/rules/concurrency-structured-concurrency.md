---
title: Use StructuredTaskScope for Fan-Out/Fan-In Tasks
impact: MEDIUM
impactDescription: subtasks cannot outlive their scope, so cancellation and error propagation are automatic
tags: [concurrency, structured-concurrency, virtual-threads, preview]
---

# Use StructuredTaskScope for Fan-Out/Fan-In Tasks [MEDIUM]

## Description
`StructuredTaskScope` treats a group of concurrent subtasks as a single unit of work: they are forked from one scope, and the scope does not exit until every subtask completes, fails, or is cancelled together. This closes the gap that hand-rolled `Future`/`ExecutorService` fan-out leaves open — a sibling task that keeps running after another one fails, or a thread leaked past the method that started it. A `Joiner` policy on the scope (e.g., "fail fast if any subtask fails," "succeed as soon as one does") governs that propagation declaratively instead of via manual bookkeeping.

**Preview status**: StructuredTaskScope is not a stable API. It shipped as a preview feature in Java 21 (JEP 453) and has been revised in every subsequent preview (JEP 462, JEP 480, JEP 499, JEP 505 in Java 25, JEP 525 in Java 26, and JEP 533 in Java 27) — the shape below reflects the JEP 499-and-later `open()`/`Joiner` API, which differs from the `ShutdownOnFailure`/`ShutdownOnSuccess` subclasses of the original JEP 453 preview. It requires `--enable-preview` to compile and run. Check your target JDK's release notes before depending on it in production, and expect the API to still be in motion.

## Bad Example
```java
ExecutorService pool = Executors.newVirtualThreadPerTaskExecutor();
Future<User> userFuture = pool.submit(() -> fetchUser(id));
Future<List<Order>> ordersFuture = pool.submit(() -> fetchOrders(id));
// If fetchOrders fails, fetchUser keeps running unmanaged — no shared cancellation,
// and a thrown exception here leaks both threads past this method.
User user = userFuture.get();
List<Order> orders = ordersFuture.get();
```

## Good Example
```java
try (var scope = StructuredTaskScope.open(Joiner.<Object>awaitAllSuccessfulOrThrow())) {
    Subtask<User> user = scope.fork(() -> fetchUser(id));
    Subtask<List<Order>> orders = scope.fork(() -> fetchOrders(id));
    scope.join(); // waits for both; cancels the sibling if either fails
    return new Profile(user.get(), orders.get());
} // scope guarantees no subtask outlives this block
```

## Notes
- A subtask can only be observed (`Subtask.get()`) after `scope.join()` returns successfully — reading it earlier is a programming error the API rejects.
- Use this for fan-out over independent, related subtasks (parallel lookups composing one result); a single async call needs no scope.
- Pair with virtual threads (`concurrency-virtual-threads`) — the model assumes forking many cheap, blocking subtasks.

## References
- [JEP 533: Structured Concurrency (Seventh Preview)](https://openjdk.org/jeps/533)
- [JEP 525: Structured Concurrency (Sixth Preview)](https://openjdk.org/jeps/525)
- [JEP 505: Structured Concurrency (Fifth Preview)](https://openjdk.org/jeps/505)
- [JEP 499: Structured Concurrency (Fourth Preview)](https://openjdk.org/jeps/499)
- [JEP 453: Structured Concurrency (Preview)](https://openjdk.org/jeps/453)
