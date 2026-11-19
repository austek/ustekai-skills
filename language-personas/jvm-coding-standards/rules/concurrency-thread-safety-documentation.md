---
title: Document a Class's Thread-Safety Contract Explicitly
impact: MEDIUM
impactDescription: callers know whether external synchronization is required without reading the implementation
tags: [concurrency, documentation, api-design, thread-safety]
---

# Document a Class's Thread-Safety Contract Explicitly [MEDIUM]

## Description
Whether a class is safe to share across threads is part of its contract, not an implementation detail — a caller cannot tell from the method signatures alone whether concurrent calls need external locking, whether the class is immutable and inherently safe, or whether it is thread-safe internally but exposes no atomicity across multiple calls. Leaving this undocumented forces every caller to either read the implementation (which can silently change) or guess, and guessing in either direction is a bug: over-synchronizing costs performance, under-synchronizing corrupts state. State the contract in the class-level Javadoc using one of a small set of standard terms, and call out any known gap explicitly — most commonly, that individual methods are thread-safe but a sequence of calls (check-then-act) is not.

## Bad Example
```java
/**
 * Tracks in-flight requests per client.
 */
public class RequestTracker {
    private final Map<String, Integer> counts = new ConcurrentHashMap<>();

    public int increment(String clientId) {
        return counts.merge(clientId, 1, Integer::sum);
    }

    public boolean isUnderLimit(String clientId, int limit) {
        return counts.getOrDefault(clientId, 0) < limit;
        // A caller checking isUnderLimit then calling increment has no idea
        // this is a non-atomic sequence — nothing here says so.
    }
}
```

## Good Example
```java
/**
 * Tracks in-flight requests per client.
 *
 * <p>Thread-safe: individual methods may be called concurrently from multiple
 * threads without external synchronization. {@code isUnderLimit} followed by
 * {@code increment} is <b>not</b> atomic as a pair — callers needing a combined
 * check-and-increment should synchronize externally or use
 * {@link #incrementIfUnderLimit}.
 */
public class RequestTracker {
    private final Map<String, Integer> counts = new ConcurrentHashMap<>();

    public synchronized boolean incrementIfUnderLimit(String clientId, int limit) {
        int current = counts.getOrDefault(clientId, 0);
        if (current >= limit) {
            return false;
        }
        counts.put(clientId, current + 1);
        return true;
    }
}
```

## Notes
- Standard terms to choose from: immutable, unconditionally thread-safe, conditionally thread-safe (state the condition), and not thread-safe.
- Document composite operations explicitly (as above) whenever individually safe methods do not compose into a safe sequence.
- For a class that is deliberately not thread-safe, say so — silence reads as "unspecified," which callers should not assume means safe.

## References
- [Java Concurrency in Practice — Ch. 4.5: Documenting Synchronization Policies](https://jcip.net/)
