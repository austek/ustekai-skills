---
title: Prefer Immutability Over Synchronization for Shared State
impact: HIGH
impactDescription: eliminates whole classes of race conditions and lock contention instead of managing them
tags: [concurrency, immutability, thread-safety, synchronization]
---

# Prefer Immutability Over Synchronization for Shared State [HIGH]

## Description
An object that cannot change after construction is safe to share across threads with no locking at all: there is no mutable state for a race to corrupt, and safe publication via a `final` field or a properly published reference guarantees every thread sees a fully constructed instance under the Java Memory Model. Synchronization instead makes mutation safe by serializing access to it — which works, but adds lock contention, the risk of forgetting a guard on some access path, and deadlock risk when multiple locks interact. When shared state changes over time, prefer replacing an immutable snapshot behind an `AtomicReference` (compute a new value, swap the reference) over mutating fields under a lock. Reach for `synchronized`/explicit locks only for state whose mutation truly cannot be modeled as a series of atomic replacements, such as coordinating access to an external, inherently mutable resource.

## Bad Example
```java
public class PriceCache {
    private final Map<String, BigDecimal> prices = new HashMap<>();

    public synchronized void update(String symbol, BigDecimal price) {
        prices.put(symbol, price); // every read and write serializes on this lock
    }

    public synchronized BigDecimal get(String symbol) {
        return prices.get(symbol);
    }
}
```

## Good Example
```java
public class PriceCache {
    private final AtomicReference<Map<String, BigDecimal>> prices =
        new AtomicReference<>(Map.of());

    public void update(String symbol, BigDecimal price) {
        prices.updateAndGet(current -> {
            Map<String, BigDecimal> next = new HashMap<>(current);
            next.put(symbol, price);
            return Map.copyOf(next); // immutable snapshot, safe to publish without a lock
        });
    }

    public BigDecimal get(String symbol) {
        return prices.get().get(symbol); // lock-free read of a consistent snapshot
    }
}
```

## Notes
- `final` fields set in the constructor are safely published to other threads without extra synchronization, provided `this` does not escape during construction.
- `AtomicReference.updateAndGet`/`getAndUpdate` retry the update function under contention (compare-and-swap), so the function passed to them must be pure and side-effect-free.
- For high-write-contention caches, a `ConcurrentHashMap` with atomic per-key operations (`computeIfAbsent`, `merge`) can outperform whole-map replacement — measure before choosing.

## References
- [Java Concurrency in Practice — Ch. 3: Sharing Objects](https://jcip.net/)
- [The Java Memory Model — Final Field Semantics](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.5)
