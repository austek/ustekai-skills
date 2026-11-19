---
title: Avoid Double-Checked Locking — Use the Holder Idiom or computeIfAbsent
impact: MEDIUM
impactDescription: lazy initialization without hand-rolled volatile-and-recheck code
tags: [concurrency, lazy-initialization, thread-safety]
---

# Avoid Double-Checked Locking — Use the Holder Idiom or computeIfAbsent [MEDIUM]

## Description
Double-checked locking (check the field, lock, check again, then initialize) exists to make lazy singleton initialization thread-safe without paying for a lock on every access. It works correctly *only* when the field is `volatile` — a detail easy to omit and, when omitted, a bug that surfaces as intermittent, hard-to-reproduce corruption under the Java Memory Model. Two idioms deliver the same result with no lock-correctness burden: the initialization-on-demand holder idiom relies on the JVM's class-loading guarantees (a class initializes exactly once, on first active use) to lazily and safely initialize a static field. For a keyed cache rather than a singleton, `ConcurrentHashMap.computeIfAbsent` gives the same lazy-once-per-key guarantee directly from the standard library.

## Bad Example
```java
public class ConfigLoader {
    private static Config instance; // missing volatile: broken under the JMM

    public static Config getInstance() {
        if (instance == null) {
            synchronized (ConfigLoader.class) {
                if (instance == null) {
                    instance = loadConfig();
                }
            }
        }
        return instance;
    }
}
```

## Good Example
```java
public class ConfigLoader {
    private static class Holder {
        static final Config INSTANCE = loadConfig(); // JVM guarantees one-time, thread-safe init
    }

    public static Config getInstance() {
        return Holder.INSTANCE;
    }
}

// Keyed lazy cache: no holder class needed
public class ConnectionRegistry {
    private final ConcurrentHashMap<String, Connection> connections = new ConcurrentHashMap<>();

    public Connection get(String host) {
        return connections.computeIfAbsent(host, this::openConnection);
    }
}
```

## Notes
- If double-checked locking is unavoidable for some other reason, the field it guards must be `volatile` — without it, a reader thread can observe a partially constructed object.
- The holder idiom's `Holder` class loads lazily on first access to `Holder.INSTANCE`, not when the outer class loads — this is what makes initialization lazy.
- `computeIfAbsent`'s mapping function must not attempt to modify the same map (including via another `computeIfAbsent` call), which can deadlock or throw `ConcurrentModificationException`.

## References
- [Effective Java, 3rd Edition — Item 83: Use lazy initialization judiciously](https://www.oreilly.com/library/view/effective-java-3rd/9780134686097/)
- [ConcurrentHashMap#computeIfAbsent (Java SE 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html#computeIfAbsent(K,java.util.function.Function))
