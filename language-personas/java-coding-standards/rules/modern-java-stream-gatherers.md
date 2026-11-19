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
List<List<Order>> batches = new ArrayList<>();
for (int i = 0; i < orders.size(); i += 100) {
    batches.add(orders.subList(i, Math.min(i + 100, orders.size())));
}
```

## Good Example
```java
List<List<Order>> batches = orders.stream()
    .gather(Gatherers.windowFixed(100))
    .toList();

List<Money> runningTotal = payments.stream()
    .gather(Gatherers.scan(() -> Money.ZERO, Money::add))
    .toList();
```

## Notes
- A custom `Gatherer` must keep its state inside the gatherer, never in captured variables.
- Do not write a gatherer for a one-off step a plain `map` or `filter` already covers.

## References
- [JEP 485: Stream Gatherers](https://openjdk.org/jeps/485)
