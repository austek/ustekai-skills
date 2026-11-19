---
title: Pin the JDK With a Gradle Toolchain and Release Target
impact: HIGH
impactDescription: every developer and CI agent compiles and tests on the same JDK, whatever is installed locally
tags: [gradle, toolchain, jdk, java25]
---

# Pin the JDK With a Gradle Toolchain and Release Target [HIGH]

## Description
Declare the JDK in the build, not in each developer's `JAVA_HOME`. A Gradle toolchain downloads and selects the requested JDK, and `release` fixes the bytecode level and the visible API surface. Target JDK 25 (LTS) for new projects, JDK 21 where a platform still requires it. Never enable preview features in the shared configuration.

## Bad Example
```kotlin
// relies on whatever JAVA_HOME happens to be
java {
    sourceCompatibility = JavaVersion.VERSION_21
}
```

## Good Example
```kotlin
java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(25)
        vendor = JvmVendorSpec.ADOPTIUM
    }
}
tasks.withType<JavaCompile>().configureEach {
    options.release = 25
}
```
```kotlin
// Kotlin
kotlin { jvmToolchain(25) }
```

## Notes
- Add `org.gradle.toolchains.foojay-resolver-convention` in `settings.gradle.kts` so CI can fetch the JDK.
- Maven: set `<maven.compiler.release>25</maven.compiler.release>` and enforce the JDK with `maven-enforcer-plugin` `requireJavaVersion`.
- Compact object headers: `-XX:+UseCompactObjectHeaders` is a product flag in JDK 25 (JEP 519) and the default in JDK 27 (JEP 534). On 25 and 26, measure before enabling it.
- AOT cache for startup: JDK 24 added AOT class loading (JEP 483), 25 added ergonomics (JEP 514), and 26 lets the AOT object cache work with any GC (JEP 516).
- G1 is the default collector on all JDK 27 environments (JEP 523).
- JDK 26 and 27 are non-LTS. Pin 25 unless the team upgrades every six months.

## References
- [Gradle Java toolchains](https://docs.gradle.org/current/userguide/toolchains.html)
- [JEP 519: Compact Object Headers](https://openjdk.org/jeps/519)
- [JEP 534: Compact Object Headers by Default](https://openjdk.org/jeps/534)
- [JEP 516: Ahead-of-Time Object Caching with Any GC](https://openjdk.org/jeps/516)
