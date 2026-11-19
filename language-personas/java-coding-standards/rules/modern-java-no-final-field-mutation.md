---
title: Do Not Mutate Final Fields Through Reflection
impact: HIGH
impactDescription: JDK 26 warns on it and a future release will refuse it by default
tags: [reflection, final, java26]
---

# Do Not Mutate Final Fields Through Reflection [HIGH]

## Description
JEP 500 (JDK 26) warns when deep reflection (`Field.setAccessible(true)` then `set`) mutates a `final` field, and a later release will block it unless enabled at startup. Final fields are what let the JVM trust immutable state, and records already forbid it. Use constructors, `withX` copy methods, builders or records. Libraries that deserialize into final fields (serialization frameworks) keep working through supported paths, but your own code, test helpers and mocking tricks must stop.

## Bad Example
```java
import java.lang.reflect.Field;
import java.time.Duration;

class Config {
    private final Duration timeout = Duration.ofSeconds(5);

    Duration timeout() {
        return timeout;
    }
}

class Tamper {
    static void shorten(Config config) throws ReflectiveOperationException {
        Field f = Config.class.getDeclaredField("timeout");
        f.setAccessible(true);
        f.set(config, Duration.ofSeconds(1)); // JDK 26 warns
    }
}
```

## Good Example
```java
import java.time.Duration;

record Config(Duration timeout) {
    Config withTimeout(Duration timeout) {
        return new Config(timeout);
    }
}

class Tune {
    static Config shorten(Config config) {
        return config.withTimeout(Duration.ofSeconds(1));
    }
}
```

## Notes
- Test code: inject the value through the constructor or a test-only factory, not reflection.
- To find offenders on JDK 26, run with the JVM's final-field-mutation warnings visible and fix what the logs name. Check JEP 500 for the exact flags to enable or restrict mutation per module.
- Dependencies that trigger the warning need an upgrade, not a startup flag.

## References
- [JEP 500: Prepare to Make Final Mean Final](https://openjdk.org/jeps/500)
