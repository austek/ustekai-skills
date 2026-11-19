---
title: Validate Arguments Before super() With Flexible Constructor Bodies
impact: MEDIUM
impactDescription: removes static-helper workarounds and half-built objects on invalid input
tags: [constructors, validation, inheritance, java25]
---

# Validate Arguments Before super() With Flexible Constructor Bodies [MEDIUM]

## Description
Java 25 (JEP 513) lets a constructor run statements before `super(...)` or `this(...)`, as long as they do not touch `this`. Validate and normalize arguments there instead of through `private static` helper methods called inside the `super(...)` expression.

## Bad Example
```java
class Range {
    final int low;
    final int high;

    Range(int low, int high) {
        this.low = low;
        this.high = high;
    }
}

class PositiveRange extends Range {
    PositiveRange(int low, int high) {
        super(requirePositive(low), requirePositive(high)); // helper exists only to run before super
    }

    private static int requirePositive(int value) {
        if (value <= 0) throw new IllegalArgumentException("must be positive: " + value);
        return value;
    }
}
```

## Good Example
```java
class Range {
    final int low;
    final int high;

    Range(int low, int high) {
        this.low = low;
        this.high = high;
    }
}

class PositiveRange extends Range {
    PositiveRange(int low, int high) {
        if (low <= 0 || high <= 0) {
            throw new IllegalArgumentException("must be positive: " + low + ", " + high);
        }
        super(low, high);
    }
}
```

## Notes
- Code before `super(...)` cannot read instance fields or call instance methods.
- Prefer records and composition where possible. This rule only removes the workaround where inheritance remains.

## References
- [JEP 513: Flexible Constructor Bodies](https://openjdk.org/jeps/513)
