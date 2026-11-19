---
title: Use Sequenced Collection Methods for First, Last and Reversed Access
impact: LOW
impactDescription: removes index arithmetic and iterator tricks that fail on empty collections
tags: [collections, java21]
---

# Use Sequenced Collection Methods for First, Last and Reversed Access [LOW]

## Description
Java 21 (JEP 431) adds `getFirst()`, `getLast()`, `addFirst()`, `removeLast()` and `reversed()` to `List`, `Deque`, `LinkedHashSet` and `SortedSet`; `LinkedHashMap` gets `firstEntry()`, `lastEntry()`, `putFirst()` and `reversed()`. Use them instead of `list.get(list.size() - 1)`, `iterator().next()` or copying into a reversed list.

## Bad Example
```java
Order latest = orders.get(orders.size() - 1);
List<Order> newestFirst = new ArrayList<>(orders);
Collections.reverse(newestFirst);
```

## Good Example
```java
Order latest = orders.getLast(); // NoSuchElementException on empty, same contract as getFirst
List<Order> newestFirst = orders.reversed(); // live view, no copy
```

## Notes
- `reversed()` is a view. Copy with `List.copyOf` before handing it across an API boundary.
- `getFirst()` and `getLast()` throw on empty. Check `isEmpty()` or use a stream `findFirst()` when empty is expected.

## References
- [JEP 431: Sequenced Collections](https://openjdk.org/jeps/431)
