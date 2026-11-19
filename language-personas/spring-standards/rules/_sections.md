# Section Definitions

## Configuration (config)
**Impact:** HIGH

**Rules:**
- `config-typed-configuration-properties` - Bind configuration to typed, validated @ConfigurationProperties

## Transactions (transactions)
**Impact:** HIGH

**Rules:**
- `transactions-service-boundary` - Put @Transactional on service methods, not controllers or repositories

## Data (data)
**Impact:** HIGH

**Rules:**
- `data-disable-open-in-view` - Disable open session in view and fetch explicitly

## Web (web)
**Impact:** HIGH

**Rules:**
- `web-dto-validation-at-boundary` - Validate request DTOs at the boundary and never expose JPA entities
- `web-problem-details-error-handling` - Return RFC 9457 Problem Details from a central @RestControllerAdvice

## Serialization (serialization)
**Impact:** HIGH

**Rules:**
- `serialization-jackson-3-migration` - Use Jackson 3 packages and customizers on Spring Boot 4

## Concurrency (concurrency)
**Impact:** MEDIUM

**Rules:**
- `concurrency-virtual-threads-property` - Enable virtual threads with the Boot property

## Observability (observability)
**Impact:** HIGH

**Rules:**
- `observability-structured-logging-and-actuator` - Use Boot structured logging and expose only needed actuator endpoints

## Testing (testing)
**Impact:** HIGH

**Rules:**
- `testing-slices-and-service-connection` - Test with slices and @ServiceConnection Testcontainers

## Kotlin (kotlin)
**Impact:** HIGH

**Rules:**
- `kotlin-compiler-plugins-spring-jpa` - Apply the kotlin-spring and kotlin-jpa compiler plugins in Kotlin projects
