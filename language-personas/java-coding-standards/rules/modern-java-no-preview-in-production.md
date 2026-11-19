---
title: Do Not Ship Preview Language Features or APIs
impact: HIGH
impactDescription: preview code needs --enable-preview and can change or disappear between JDK releases
tags: [preview, compatibility]
---

# Do Not Ship Preview Language Features or APIs [HIGH]

## Description
Preview features compile only with `--enable-preview`, tie the class files to one exact JDK feature release, and change shape between previews. As of JDK 27 (September 2026) these are still preview: `StructuredTaskScope` (JEP 533, seventh preview; preview since JDK 21), primitive types in patterns (JEP 532, fifth preview) and Lazy Constants (JEP 531, third preview; it replaced `StableValue` from JEP 502). Keep them out of production modules, libraries and anything built into shared artifacts, on every JDK from 21 on.

## Bad Example
```java
// compiled with --enable-preview --release 25; class files refuse to load on any other JDK feature release
class Preview {
    static int plusOne(Object value) {
        if (value instanceof int i) { // primitive pattern (preview)
            return i + 1;
        }
        return 0;
    }
}
```

## Good Example
```java
class Stable {
    static int plusOne(Object value) {
        if (value instanceof Integer i) {
            return i + 1;
        }
        return 0;
    }
}
```

## Notes
- Experiments are fine in a throwaway module or spike. Do not publish its artifacts.
- Do not add `--enable-preview` to the shared compiler configuration. Scope it to the one experimental source set.
- Re-check each preview's JEP before adopting it. Most graduate after two to five previews.

## References
- [JEP 12: Preview Features](https://openjdk.org/jeps/12)
- [JEP 533: Structured Concurrency (Seventh Preview)](https://openjdk.org/jeps/533)
- [JEP 532: Primitive Types in Patterns, instanceof, and switch (Fifth Preview)](https://openjdk.org/jeps/532)
- [JEP 531: Lazy Constants (Third Preview)](https://openjdk.org/jeps/531)
