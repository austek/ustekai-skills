---
title: Configure Javadoc Linters to Match the Documentation Rules
impact: MEDIUM
impactDescription: default linters demand filler tags and 100% Javadoc, which pushes code toward signature narration
tags: [javadoc, checkstyle, doclint, error-prone]
---

# Configure Javadoc Linters to Match the Documentation Rules [MEDIUM]

## Description
Default settings of common tools require a `@param` for every parameter, a `@return` for every non-void method, and a comment on every public method. That conflicts with `javadoc-no-signature-narration` and `javadoc-param-return-tags-only-when-non-obvious`. Tune the tools once, in the build, so they enforce correct syntax and a summary but not filler. Do not suppress the checks wholesale.

## Bad Example
```xml
<module name="JavadocMethod"/> <!-- allowMissingParamTags=false, allowMissingReturnTag=false by default -->
<module name="MissingJavadocMethod"/>
```
```kotlin
options.compilerArgs.add("-Xdoclint:all") // includes the 'missing' group
```

## Good Example
```xml
<module name="JavadocMethod">
  <property name="allowMissingParamTags" value="true"/>
  <property name="allowMissingReturnTag" value="true"/>
  <property name="validateThrows" value="true"/>
</module>
<module name="SummaryJavadoc"/>
<module name="MissingJavadocMethod">
  <property name="scope" value="public"/>
  <property name="allowMissingPropertyJavadoc" value="true"/>
  <property name="minLineCount" value="3"/>
</module>
```
```kotlin
tasks.withType<JavaCompile>().configureEach {
    options.compilerArgs.add("-Xdoclint:all,-missing")
}
```

## Notes
- `-Xdoclint` is off by default and is not part of `-Xlint:all`; enable it deliberately.
- Sonar's "public methods should be documented" rule (S1176) is also coverage-driven; limit it to the public API module with its scope and exclusion settings, or disable it for internal modules.
- Verify option names against your Checkstyle version; `allowMissingParamTags` and `allowMissingReturnTag` exist since 3.1, `validateThrows` since 6.0.

## References
- [Checkstyle JavadocMethod](https://checkstyle.org/checks/javadoc/javadocmethod.html)
- [javac -Xdoclint](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html)
