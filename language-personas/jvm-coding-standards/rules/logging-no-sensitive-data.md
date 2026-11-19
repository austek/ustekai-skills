---
title: Never Log Secrets, Tokens or Personal Data
impact: CRITICAL
impactDescription: logs are replicated, retained and widely readable; a leaked secret in a log is a breach
tags: [logging, security, privacy]
---

# Never Log Secrets, Tokens or Personal Data [CRITICAL]

## Description
Log lines outlive the request and reach many readers. Passwords, API keys, bearer tokens, session ids, full card numbers and personal data (email, address, health data) must not appear in any log field, including at DEBUG. Log stable identifiers instead, and give sensitive types a `toString()` that redacts.

## Bad Example
```java
log.info("login request: {}", request); // record toString includes password
log.debug("calling upstream with header Authorization={}", authHeader);
```

## Good Example
```java
record LoginRequest(String username, Secret password) {}

record Secret(String value) {
    @Override public String toString() { return "***"; } // text logging and string formatting

    @JsonValue // Jackson-based JSON encoders, such as logstash-logback-encoder
    String redacted() { return "***"; }
}

log.atInfo().addKeyValue("username", request.username()).log("login attempt");
```

## Notes
- Wrap secrets in a dedicated type. `toString()` redaction covers text output only; a JSON encoder passes the object to Jackson, which serializes record components regardless of `toString()`. The `@JsonValue` accessor above redacts that path.
- The guarantee holds only on paths that enforce it. Other serializers (kotlinx.serialization, Gson) need their own redaction, and the safest field is one you never pass to the logger.
- Log HTTP headers from an allow-list, never a deny-list.
- Treat exception messages that echo input (SQL, URLs with query strings) as sensitive.

## References
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
