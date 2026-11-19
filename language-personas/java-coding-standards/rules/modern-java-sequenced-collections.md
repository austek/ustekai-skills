---
title: Use Sequenced Collection Methods for First, Last and Reversed Access
impact: LOW
impactDescription: removes index arithmetic and iterator tricks that fail on empty collections
tags: [collections, java21]
---

# Use Sequenced Collection Methods for First, Last and Reversed Access [LOW]

## Description
Java 21 (JEP 431) adds `getFirst()`, `getLast()`, `addFirst()`, `removeLast()` and `reversed()` to `List`, `Deque` and `LinkedHashSet`; `LinkedHashMap` gets `firstEntry()`, `lastEntry()`, `putFirst()` and `reversed()`. Sorted sets (`SortedSet`, `NavigableSet`) are sequenced too, but their position comes from the comparator: `addFirst` and `addLast` throw `UnsupportedOperationException`, so use `add()` there. Use these methods instead of `list.get(list.size() - 1)`, `iterator().next()` or copying into a reversed list.

## Bad Example
```java
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

record Order(String id) {}

class Latest {
    static Order latest(List<Order> orders) {
        return orders.get(orders.size() - 1);
    }

    static List<Order> newestFirst(List<Order> orders) {
        List<Order> copy = new ArrayList<>(orders);
        Collections.reverse(copy);
        return copy;
    }
}
```

## Good Example
```java
import java.util.List;

record Order(String id) {}

class Latest {
    static Order latest(List<Order> orders) {
        return orders.getLast(); // NoSuchElementException on empty, same contract as getFirst
    }

    static List<Order> newestFirstView(List<Order> orders) {
        return orders.reversed(); // live view: later changes to orders show through
    }

    static List<Order> newestFirstSnapshot(List<Order> orders) {
        return List.copyOf(orders.reversed()); // independent copy
    }
}
```

## Notes
- `reversed()` is a view. Use the snapshot form when the caller needs a list that does not change with the source, including across an API boundary.
- `getFirst()` and `getLast()` throw on empty. Check `isEmpty()` or use a stream `findFirst()` when empty is expected.

## References
- [JEP 431: Sequenced Collections](https://openjdk.org/jeps/431)
