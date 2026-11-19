---
title: Use the Foreign Function and Memory API Instead of JNI
impact: MEDIUM
impactDescription: native calls without C glue code; a wrong descriptor can still crash the JVM
tags: [native, interop, ffm, java22]
---

# Use the Foreign Function and Memory API Instead of JNI [MEDIUM]

## Description
The Foreign Function and Memory API (final in Java 22, JEP 454) calls native libraries and manages off-heap memory from plain Java, with deterministic `Arena` lifetimes and bounds-checked segments. Use it for new native interop instead of JNI headers and C stubs, and instead of `sun.misc.Unsafe`. It does not make native code safe: `Linker.downcallHandle` is a restricted method, and a descriptor that does not match the native signature can crash the JVM or corrupt memory.

## Bad Example
```java
class Native {
    static {
        System.loadLibrary("strlen_jni");
    }

    // needs a generated header, a C stub and a build per platform
    static native long strlen(String s);
}
```

## Good Example
```java
import java.lang.foreign.Arena;
import java.lang.foreign.FunctionDescriptor;
import java.lang.foreign.Linker;
import java.lang.foreign.MemorySegment;
import java.lang.foreign.ValueLayout;
import java.lang.invoke.MethodHandle;

class NativeStrlen {
    private static final Linker LINKER = Linker.nativeLinker();
    private static final MethodHandle STRLEN = LINKER.downcallHandle(
        LINKER.defaultLookup().find("strlen").orElseThrow(),
        FunctionDescriptor.of(ValueLayout.JAVA_LONG, ValueLayout.ADDRESS));

    static long strlen(String s) throws Throwable {
        try (Arena arena = Arena.ofConfined()) {
            MemorySegment text = arena.allocateFrom(s); // freed when the arena closes
            return (long) STRLEN.invokeExact(text);
        }
    }
}
```

## Notes
- Run with `--enable-native-access=ALL-UNNAMED` (or the module name) to avoid the warning on restricted methods.
- `invokeExact` declares `Throwable`. Wrap the handle in a typed Java facade that translates it, so callers never see `MethodHandle` or `Throwable`.
- Keep descriptors next to the native header they mirror. `jextract` generates bindings from C headers.

## References
- [JEP 454: Foreign Function & Memory API](https://openjdk.org/jeps/454)
