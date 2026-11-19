# Section Definitions

## Build Configuration (build)
**Impact:** HIGH

Configure Gradle and Maven builds for correct dependency scoping and reproducibility.

**Rules:**
- `build-api-vs-implementation-scope` - Treat api vs implementation as a compile-avoidance lever, not just encapsulation
- `build-gradle-version-catalogs` - Centralize dependency versions in a Gradle version catalog
- `build-maven-dependency-management-bom` - Import a BOM in dependencyManagement instead of pinning every version
- `build-reproducible-builds` - Ban dynamic version ranges and non-deterministic archive output

## Toolchain (toolchain)
**Impact:** HIGH

Fix the JDK in the build.

**Rules:**
- `toolchain-pin-jdk` - Pin the JDK with a Gradle toolchain and release target

## Dependency Management (dependency-management)
**Impact:** MEDIUM

Keep dependency versions and transitive exposure under single-source control.

**Rules:**
- `dependency-management-lockfile-or-bom` - Pick one source of truth — dependency lockfile or BOM, not neither
- `dependency-management-minimal-transitive-exposure` - Exclude unneeded transitive dependencies instead of accepting the full graph
- `dependency-management-version-catalog-single-source` - Make the version catalog the only place a version number can appear
- `dependency-management-vulnerability-scanning` - Scan dependencies for known CVEs on every build, not at release time
