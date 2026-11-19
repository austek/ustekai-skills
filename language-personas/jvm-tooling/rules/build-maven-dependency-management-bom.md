---
title: Import a BOM in dependencyManagement Instead of Pinning Every Version
impact: HIGH
impactDescription: removes per-module version pins that drift and conflict across a multi-module reactor
tags: [maven, bom, dependency-management, build-configuration]
---

# Import a BOM in dependencyManagement Instead of Pinning Every Version [HIGH]

## Description
Maven's `<dependencyManagement>` section declares default versions, scopes, and exclusions for coordinates without adding them to any module's classpath — a `<dependency>` elsewhere in the reactor that matches on `groupId`/`artifactId` inherits the managed version and can omit `<version>` entirely. A Bill of Materials (BOM) is a `pom`-packaged artifact whose entire content is a curated `dependencyManagement` block of mutually-compatible versions (`jackson-bom`, `spring-boot-dependencies`); importing it with `<scope>import</scope>` and `<type>pom</type>` inside your own `dependencyManagement` merges that curated set into your build, so every module gets a consistent, tested combination instead of whatever versions each module's author happened to pick.

Pinning versions per module instead means the same library ends up at different versions in different modules of one reactor, and nothing catches the drift until a runtime `NoSuchMethodError` surfaces a binary incompatibility that Maven's nearest-wins conflict resolution silently papered over. Centralizing in the parent POM's `dependencyManagement` — either hand-maintained or via BOM import — makes that drift a single-file diff instead of a hunt across every module's POM.

BOM import order matters: when two imported BOMs manage the same coordinate, the one imported last wins, so combining BOMs from different ecosystems (e.g. a cloud SDK BOM and a JSON library BOM) requires checking for overlapping coordinates rather than importing blindly.

## Bad Example
```xml
<!-- module-a/pom.xml -->
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.17.0</version>
</dependency>

<!-- module-b/pom.xml, edited by someone else six months later -->
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.15.2</version>
</dependency>
```

## Good Example
```xml
<!-- parent pom.xml -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.fasterxml.jackson</groupId>
            <artifactId>jackson-bom</artifactId>
            <version>2.17.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<!-- module-a/pom.xml and module-b/pom.xml -->
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>
```

## Notes
- `dependencyManagement` alone never adds a dependency to any classpath — a module still needs its own `<dependency>` entry; the import only supplies the default version/scope/exclusions when that entry omits them.
- Run `mvn dependency:tree -Dverbose` to spot places where a module's explicit version overrides the managed one, and confirm that override is intentional.
- A managed version still loses to an explicit `<version>` declared directly in a module's own POM — management only fills in what's left unset.

## References
- [Maven — Introduction to the Dependency Mechanism, Dependency Management](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html#dependency-management)
- [Maven POM Reference — dependencyManagement](https://maven.apache.org/pom.html#dependency-management)
