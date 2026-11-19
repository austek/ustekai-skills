---
title: Avoid Autoboxing in Hot Paths
impact: HIGH
impactDescription: removes per-element allocation and unboxing overhead that dominates tight numeric loops
tags: [performance, autoboxing, primitives]
---

# Avoid Autoboxing in Hot Paths [HIGH]

## Description
Autoboxing converts a primitive (`int`, `long`, `double`) to its wrapper type (`Integer`, `Long`, `Double`) automatically wherever a reference type is expected — a generic collection, a method expecting `Object`, an arithmetic expression mixing a primitive with a wrapper. Each boxing operation allocates an object (outside the small cached range the JVM keeps for `Integer.valueOf(-128..127)` and similar), and each use of a boxed value in arithmetic unboxes it back to a primitive first. In a hot path — a loop summing millions of values, a per-request calculation on a high-throughput service — that allocation and unboxing happens on every iteration, adding both CPU overhead and GC pressure that a primitive-only version doesn't pay at all. `Collectors.summingInt` over `Collectors.summingDouble` on a `Stream<Double>`, or an `int` accumulator instead of `Integer`, both avoid the round-trip entirely.

This is a hot-path-specific rule, not a blanket ban on wrapper types — `Integer` is required wherever generics demand a reference type (`List<Integer>`), and the cost is irrelevant outside a loop executed at scale.

## Bad Example
```java
public double totalPrice(List<Double> prices) {
    Double total = 0.0; // boxed accumulator
    for (Double price : prices) {
        total += price; // unbox total, unbox price, add, box the result back — every iteration
    }
    return total;
}
```

## Good Example
```java
public double totalPrice(List<Double> prices) {
    double total = 0.0; // primitive accumulator, no boxing round-trip
    for (double price : prices) { // unboxed once per element by the enhanced for-loop, not per operation
        total += price;
    }
    return total;
}

// equivalently, and often clearer:
public double totalPrice(List<Double> prices) {
    return prices.stream().mapToDouble(Double::doubleValue).sum();
}
```

## Notes
- `IntStream`/`LongStream`/`DoubleStream` and their `mapToInt`/`mapToLong`/`mapToDouble` variants keep a stream pipeline entirely on primitives — reach for them before a `Stream<Integer>` in numeric code.
- `==` on boxed types compares references outside the `Integer` cache range (`-128..127`); a hot-path comparison should unbox explicitly or use `.equals()`/`Objects.equals()`, not rely on the cache's accidental correctness for small values.
- Measure before optimizing — see `performance-avoid-premature-optimization`; this rule applies to code already identified as a hot path, not every numeric field in the codebase.

## References
- [JLS §5.1.7: Boxing Conversion](https://docs.oracle.com/javase/specs/jls/se21/html/jls-5.html#jls-5.1.7)
- [Effective Java, 3rd Edition — Item 6: Avoid creating unnecessary objects](https://www.oreilly.com/library/view/effective-java-3rd/9780134686097/)
