---
title: Use Stream Gatherers for Windowing and Stateful Steps
impact: MEDIUM
impactDescription: replaces hand-written collectors and stateful lambdas with tested intermediate operations
tags: [streams, gatherers, java24]
---

# Use Stream Gatherers for Windowing and Stateful Steps [MEDIUM]

## Description
`Stream.gather` (final in Java 24, JEP 485) adds custom intermediate operations. Use the built-in `Gatherers.windowFixed`, `windowSliding`, `scan` and `fold` for batching and running totals instead of collecting to a list and re-streaming, or mutating a captured variable inside `map`.

## Bad Example
```java
import java.util.ArrayList;
import java.util.List;

record Order(String id) {}

class Batching {
    static List<List<Order>> batches(List<Order> orders) {
        List<List<Order>> batches = new ArrayList<>();
        for (int i = 0; i < orders.size(); i += 100) {
            batches.add(orders.subList(i, Math.min(i + 100, orders.size())));
        }
        return batches;
    }
}
```

## Good Example
```java
import java.util.List;
import java.util.stream.Gatherers;

record Order(String id) {}
record Payment(long cents) {}

class Batching {
    static List<List<Order>> batches(List<Order> orders) {
        return orders.stream()
            .gather(Gatherers.windowFixed(100))
            .toList();
    }

    static List<Long> runningTotal(List<Payment> payments) {
        return payments.stream()
            .map(Payment::cents)
            .gather(Gatherers.scan(() -> 0L, Long::sum))
            .toList();
    }
}
```

## Notes
- A custom `Gatherer` must keep its state inside the gatherer, never in captured variables.
- Do not write a gatherer for a one-off step a plain `map` or `filter` already covers.

## References
- [JEP 485: Stream Gatherers](https://openjdk.org/jeps/485)
