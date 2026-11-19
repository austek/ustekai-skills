---
title: Declare Nullability Explicitly on Values From Java
impact: CRITICAL
impactDescription: stops platform types (T!) from leaking unchecked nulls into Kotlin code
tags: [null-safety, java-interop]
---

# Declare Nullability Explicitly on Values From Java [CRITICAL]

## Description
A Java method without nullability annotations returns a platform type `T!`, which the compiler lets you use as either `T` or `T?` without checks. Assign the result to an explicitly typed `val` at the boundary so the null decision is made once, in one place.

## Bad Example
```java
public class JavaApi {
    public String findName(String id) { return null; }
}
```
```kotlin
fun show(javaApi: JavaApi, id: String) {
    val name = javaApi.findName(id) // String!, NPE later far from here
    println(name.length)
}
```

## Good Example
```java
public class JavaApi {
    public String findName(String id) { return null; }
}
```
```kotlin
fun show(javaApi: JavaApi, id: String) {
    val name: String = javaApi.findName(id) ?: error("no name for $id")
    val maybe: String? = javaApi.findName(id)
    println(name.length + (maybe?.length ?: 0))
}
```

## Notes
- Public Kotlin functions must declare their return type explicitly so a platform type never escapes.
- Java APIs annotated with JSpecify `@Nullable`/`@NullMarked` (Spring Framework uses them) are read as real Kotlin types and enforced strictly. Unannotated APIs still produce platform types.

## References
- [Calling Java from Kotlin: nullability](https://kotlinlang.org/docs/java-interop.html#null-safety-and-platform-types)
