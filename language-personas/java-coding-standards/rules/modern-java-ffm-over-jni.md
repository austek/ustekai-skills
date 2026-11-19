---
title: Use the Foreign Function and Memory API Instead of JNI
impact: MEDIUM
impactDescription: memory-safe native calls without C glue code
tags: [native, interop, ffm, java22]
---

# Use the Foreign Function and Memory API Instead of JNI [MEDIUM]

## Description
The Foreign Function and Memory API (final in Java 22, JEP 454) calls native libraries and manages off-heap memory from plain Java, with deterministic `Arena` lifetimes. Use it for new native interop instead of JNI headers and C stubs, and instead of `sun.misc.Unsafe`.

## Bad Example
```java
public class Native {
    static { System.loadLibrary("strlen_jni"); }
    public static native long strlen(String s); // needs generated header, C stub and a build per platform
}
```

## Good Example
```java
Linker linker = Linker.nativeLinker();
MethodHandle strlen = linker.downcallHandle(
    linker.defaultLookup().find("strlen").orElseThrow(),
    FunctionDescriptor.of(ValueLayout.JAVA_LONG, ValueLayout.ADDRESS));

try (Arena arena = Arena.ofConfined()) {
    MemorySegment text = arena.allocateFrom("hello"); // freed when the arena closes
    long length = (long) strlen.invokeExact(text);
}
```

## Notes
- Run with `--enable-native-access=ALL-UNNAMED` (or the module name) to avoid the warning on restricted methods.
- Wrap handles in a typed Java facade so callers never see `MethodHandle`.
- `jextract` generates bindings from C headers.

## References
- [JEP 454: Foreign Function & Memory API](https://openjdk.org/jeps/454)
