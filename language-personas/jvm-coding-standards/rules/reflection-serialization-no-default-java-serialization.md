---
title: Never Use Java's Built-In Serialization for New Code
impact: CRITICAL
impactDescription: closes a well-documented remote-code-execution vector and a brittle binary format at once
tags: [reflection, serialization, security]
---

# Never Use Java's Built-In Serialization for New Code [CRITICAL]

## Description
`java.io.Serializable` plus `ObjectInputStream` deserializes a byte stream by reflectively instantiating whatever class the stream names, running that class's `readObject` and any constructors, finalizers, or field initializers it triggers along the way — before application code gets any chance to validate the data. Any class reachable on the classpath with a "gadget chain" from `readObject` to a dangerous operation (file access, command execution) turns a deserialization call into arbitrary code execution; this is not a theoretical risk, it's the mechanism behind a long, ongoing series of real CVEs across widely used libraries, and the Java architects themselves have described the feature as a mistake with no way to fully close given its history and the impossibility of enumerating every unsafe class reachable transitively. Beyond security, the binary format is JVM-specific, brittle across class version changes (`serialVersionUID` mismatches break deserialization silently or loudly depending on `strictness`), and unreadable without Java tooling.

For any new code — inter-process messages, cache entries, persisted state, wire formats — use a text or schema-based format instead: JSON via Jackson, Protocol Buffers, Avro, or a hand-rolled format, none of which reflectively instantiate arbitrary classes from untrusted bytes by default.

## Bad Example
```java
public class SessionStore {
    public byte[] save(UserSession session) throws IOException {
        var bytes = new ByteArrayOutputStream();
        try (var out = new ObjectOutputStream(bytes)) {
            out.writeObject(session); // requires session (and its whole graph) to implement Serializable
        }
        return bytes.toByteArray();
    }

    public UserSession load(byte[] data) throws IOException, ClassNotFoundException {
        try (var in = new ObjectInputStream(new ByteArrayInputStream(data))) {
            return (UserSession) in.readObject(); // deserializes whatever class name is embedded in data
        }
    }
}
```

## Good Example
```java
public class SessionStore {
    private final ObjectMapper mapper; // configured per reflection-serialization-jackson-explicit-config

    public byte[] save(UserSession session) throws JsonProcessingException {
        return mapper.writeValueAsBytes(session);
    }

    public UserSession load(byte[] data) throws IOException {
        return mapper.readValue(data, UserSession.class); // target type fixed by the caller, not the input
    }
}
```

## Notes
- If legacy code deserializes untrusted input with `ObjectInputStream`, `ObjectInputFilter` (Java 9+, `JEP 290`) allow-lists which classes may be deserialized — a mitigation, not a reason to keep writing new code this way.
- `Externalizable` has the same reflective-instantiation risk profile as `Serializable` and is not a safer alternative.
- A record or class only needing to implement `Serializable` because a legacy framework demands it (some caching or clustering libraries) should still keep untrusted-input deserialization behind an `ObjectInputFilter`.

## References
- [JEP 290: Filter Incoming Serialization Data](https://openjdk.org/jeps/290)
- [OWASP — Deserialization of Untrusted Data](https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data)
