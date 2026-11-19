---
title: Name Unused Bindings With the Unnamed Variable _
impact: LOW
impactDescription: makes intentionally unused bindings explicit and silences false unused warnings
tags: [readability, pattern-matching, java22]
---

# Name Unused Bindings With the Unnamed Variable _ [LOW]

## Description
Since Java 22 (JEP 456) `_` declares a binding that is intentionally unused: catch parameters, lambda parameters, loop variables and record-pattern components. It tells the reader and the compiler that the value is ignored on purpose.

## Bad Example
```java
record Point(int x, int y) {}
record Rectangle(Point topLeft, Point bottomRight) {}

class Parsing {
    static int parseOr(String text, int fallback) {
        try {
            return Integer.parseInt(text);
        } catch (NumberFormatException ignored) {
            return fallback;
        }
    }

    static boolean isRectangle(Object shape) {
        return shape instanceof Rectangle(Point topLeft, Point bottomRight); // uses neither
    }
}
```

## Good Example
```java
record Point(int x, int y) {}
record Rectangle(Point topLeft, Point bottomRight) {}

class Parsing {
    static int parseOr(String text, int fallback) {
        try {
            return Integer.parseInt(text);
        } catch (NumberFormatException _) {
            return fallback;
        }
    }

    static boolean isRectangle(Object shape) {
        return shape instanceof Rectangle(_, _);
    }
}
```

## Notes
- Do not swallow exceptions silently. `catch (X _)` still needs a deliberate fallback or a log line.
- Use `case Circle _ ->` in a `switch` when no field is needed.

## References
- [JEP 456: Unnamed Variables & Patterns](https://openjdk.org/jeps/456)
