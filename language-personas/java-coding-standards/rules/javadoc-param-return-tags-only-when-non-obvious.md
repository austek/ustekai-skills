---
title: Write @param/@return Tags Only When They Add Information
impact: LOW
impactDescription: keeps Javadoc signal-to-noise high enough that readers actually read it
tags: [javadoc, documentation, readability]
---

# Write @param/@return Tags Only When They Add Information [LOW]

## Description
An `@param` or `@return` tag is worth writing only when it tells the reader something the parameter's name and type don't already say. `@param name the name` and `@return the result` are noise that trains readers to skip Javadoc entirely, because most of what they'll find restates the signature. A tag earns its place by giving a unit, a valid range, a default when omitted, a relationship between parameters, or what a boundary value means — information that lives nowhere else in the signature.

This is a narrower case of the general rule against signature narration (`javadoc-no-signature-narration`): where that rule covers the whole comment, this one covers the common failure mode where the summary sentence is fine but every `@param`/`@return` underneath it is filler added only to satisfy a "must have tags" checklist. Omitting a tag entirely is preferable to writing a filler one — a missing `@param` on an otherwise well-named parameter loses nothing; a filler one adds a line a reader has to read and dismiss.

## Bad Example
```java
/**
 * Creates a new user.
 *
 * @param name the name
 * @param email the email
 * @return the user
 */
public User createUser(String name, String email) { ... }
```

## Good Example
```java
/**
 * Creates a new, unverified user. Sends a verification email to {@code email} as a side effect.
 *
 * @param email must be a syntactically valid address; delivery is not confirmed
 * @return the created user, with {@link User#verified()} always {@code false}
 */
public User createUser(String name, String email) { ... }
```

## Notes
- `name` above has no `@param` because there is nothing to add beyond what the parameter name already says — that's a deliberate omission, not an oversight.
- A generic type parameter (`@param <T> ...`) is more often worth documenting than a concrete one, since its constraint or role usually isn't obvious from a single letter.
- Checkstyle's `JavadocMethod` defaults `allowMissingParamTags` and `allowMissingReturnTag` to `false`, so a default Checkstyle run flags every omitted tag. Set both to `true` in the project config, scoped to this rule, instead of writing filler tags or suppressing the check; see `lint-format-javadoc-tool-alignment` in java-tooling.
- `javac -Xdoclint` is off by default. Enabling `-Xdoclint:all` includes the `missing` group, which also reports omitted tags; use `-Xdoclint:all,-missing` to keep the syntax, HTML and reference checks.
- Google Java Style agrees: Javadoc may be omitted on simple, obvious members, tags never have an empty description, and every block starts with a summary fragment (`javadoc-summary-first`). Kotlin's coding conventions go further and say to avoid `@param`/`@return` in KDoc.

## References
- [How to Write Doc Comments for the Javadoc Tool (Oracle)](https://www.oracle.com/technical-resources/articles/java/javadoc-tool.html)
- [Effective Java, 3rd Edition — Item 56: Write doc comments for all exposed API elements](https://www.oreilly.com/library/view/effective-java-3rd/9780134686097/)
