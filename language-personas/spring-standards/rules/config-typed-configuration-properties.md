---
title: Bind Configuration to Typed, Validated @ConfigurationProperties
impact: HIGH
impactDescription: misconfiguration fails at startup with a clear message instead of at first use
tags: [spring, configuration, validation]
---

# Bind Configuration to Typed, Validated @ConfigurationProperties [HIGH]

## Description
Targets Spring Boot 4.x (Spring Framework 7). Scattered `@Value("${...}")` strings are untyped, unvalidated and unfindable. Group related settings in one immutable `@ConfigurationProperties` record (Java) or data class (Kotlin) with bean-validation annotations. Boot then fails the context at startup when a value is missing or malformed.

## Bad Example
```java
@Value("${payments.timeout}") private String timeout;
@Value("${payments.url:}") private String url;
```

## Good Example
```java
import jakarta.validation.constraints.NotNull;
import java.net.URI;
import java.time.Duration;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;
import org.springframework.validation.annotation.Validated;

@ConfigurationProperties("payments")
@Validated
public record PaymentsProperties(
    @NotNull URI url,
    @DefaultValue("5s") Duration timeout
) {}
```
```kotlin
import java.net.URI
import java.time.Duration
import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.validation.annotation.Validated

@ConfigurationProperties("payments")
@Validated
data class PaymentsProperties(
    val url: URI,
    val timeout: Duration = Duration.ofSeconds(5),
)
```

## Notes
- Enable with `@ConfigurationPropertiesScan` or `@EnableConfigurationProperties`.
- Secrets come from the environment or a secret manager, never from committed `application.yml`.
- Add `spring-boot-configuration-processor` for IDE metadata.

## References
- [Externalized Configuration](https://docs.spring.io/spring-boot/reference/features/external-config.html)
