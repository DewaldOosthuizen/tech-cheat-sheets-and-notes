# SPRING BOOT

Quick-reference cheat sheet for Spring Boot, targeting Spring Boot 3.x and Java 17+.
Covers auto-configuration, externalised configuration, profiles, dependency injection,
validation, actuator, observability, configuration properties, MVC vs WebFlux, native images,
and component stereotype selection. Comparison-oriented — decision tables, Mermaid flows,
and production-practice guidance.

## Auto-Configuration & Starters

Spring Boot auto-configuration uses conditional `@Configuration` beans assembled automatically
based on classpath contents, existing bean definitions, and property settings. Starters are
opinionated dependency descriptors that pull in the right transitive dependencies for a given
use case, eliminating manual dependency selection and version coordination.

### Starter Selection

|| Use Case | Starter | Key Dependencies |
|| --- | --- | --- |
|| Traditional servlet-based web app (REST, MVC, templates) | `spring-boot-starter-web` | Spring MVC, Tomcat, Jackson, validation |
|| Reactive web service (non-blocking, streaming) | `spring-boot-starter-webflux` | Spring WebFlux, Reactor Netty, reactive codecs |
|| Relational database access with JPA/Hibernate | `spring-boot-starter-data-jpa` | Spring Data JPA, Hibernate, connection pool (HikariCP) |
|| Batch processing (scheduled jobs, large-volume ETL) | `spring-boot-starter-batch` | Spring Batch, job repository, chunk-oriented processing |
|| Production-ready monitoring and management endpoints | `spring-boot-starter-actuator` | Actuator endpoints, Micrometer, health indicators |
|| Declarative REST client (HTTP calls to other services) | `spring-boot-starter-web` + `spring-boot-starter-webflux` or RestClient | Jackson, HTTP client, server-sent events support |
|| Security (auth, OAuth2, resource server, method security) | `spring-boot-starter-security` | Spring Security, authentication providers, password encoding |
|| Testing (unit, slice, integration) | `spring-boot-starter-test` | JUnit 5, Mockito, AssertJ, Spring Test, JSON assertions |
|| YAML configuration support | `spring-boot-starter` (included by all) | SnakeYAML, no separate starter needed |
|| Mail / email sending | `spring-boot-starter-mail` | Jakarta Mail, JavaMail sender |
|| Caching abstraction | `spring-boot-starter-cache` | Spring Cache, cache provider (Caffeine, Ehcache, Redis) |
|| Discovery client (service registry integration) | `spring-cloud-starter-netflix-eureka-client` or similar | Eureka client, load balancer, circuit breaker (Resilience4j) |

> **Exam tip:** Auto-configuration is triggered by `@SpringBootApplication` (which combines
> `@Configuration`, `@EnableAutoConfiguration`, and `@ComponentScan`). The `@EnableAutoConfiguration`
> annotation imports `AutoConfigurationImportSelector`, which reads `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`
> to discover and conditionally register candidate configurations. A starter's
> `spring.factories` (Spring Boot 2) or `AutoConfiguration.imports` (Spring Boot 3) lists the
> auto-configuration classes that are candidates — each class uses `@ConditionalOnClass`,
> `@ConditionalOnMissingBean`, `@ConditionalOnProperty`, and similar annotations to decide whether
> to apply.

## Externalised Configuration

Spring Boot externalises configuration so the same artefact runs in different environments.
Property sources are loaded in a defined order — later sources override earlier ones.

### Property Source Order (lowest to highest precedence)

1. Default properties (set via `SpringApplication.setDefaultProperties` or `System.getProperty`)
2. `application.properties` / `application.yml` on classpath (inside the jar)
3. `application.properties` / `application.yml` in the current directory
4. Profile-specific variants: `application-{profile}.properties` / `application-{profile}.yml`
   (combined with the above — profile-specific overrides if the profile is active)
5. `@PropertySource` annotations on `@Configuration` classes
6. OS environment variables (e.g. `SERVER_PORT=8080`)
7. Java system properties (`-D` flags)
8. `SPRING_APPLICATION_JSON` embedded in environment or command line
9. Command-line arguments (`--server.port=9090`)

### Formats

|| Aspect | `application.properties` | `application.yml` |
|| --- | --- | --- |
|| Syntax | `key=value`, dot notation for nesting (`server.port=8080`) | Indentation-based hierarchy, native list/map support |
|| Nested structures | `myapp.name=MyApp`, `myapp.database.url=...` (flat keys) | `myapp:\n  name: MyApp\n  database:\n    url: jdbc:...` (hierarchical) |
|| Lists / arrays | Comma-separated values or repeated keys with `[0]`, `[1]` notation | Native YAML list syntax (`- item`) |
|| Comments | `# comment` | `# comment` (YAML standard) |
|| Tooling support | Universal text-editor friendly | Better rendered by YAML-aware editors with schema validation |

### `@Value` vs `@ConfigurationProperties`

|| Decision Point | `@Value` | `@ConfigurationProperties` |
|| --- | --- | --- |
|| Scope | Inject a single property value into a field | Bind a group of related properties to a typed bean |
|| Type safety | String-only from property source; manual conversion required | Full type conversion (int, boolean, list, map, custom converters) |
|| Validation | None built-in | `@Validated` on the class enables Bean Validation constraints |
|| Relaxed binding | Not applicable (exact key match) | Supports kebab-case, snake_case, camelCase, and dot notation interchangeably |
|| Metadata generation | None | `spring-boot-configuration-processor` generates metadata for IDE autocompletion |
|| Use when | Occasional, one-off property injection in a non-config bean | Structured configuration with multiple related properties, validation, and IDE support |
|| Prefix | Not used | `@ConfigurationProperties(prefix = "myapp")` binds all `myapp.*` properties |

```java
// @Value — single, ad-hoc injection
@Value("${app.max-retries:3}")
private int maxRetries;

// @ConfigurationProperties — type-safe, validated, IDE-friendly
@ConfigurationProperties(prefix = "app.database")
@Validated
public class DatabaseProperties {
    @NotBlank
    private String url;
    @NotBlank
    private String username;
    private int poolSize = 10;
    // getters/setters or record
}
```

### `@PropertySource`

Use `@PropertySource("classpath:custom.properties")` to load additional property files beyond
the standard `application.properties`. Place on a `@Configuration` class. Does not support
profile-specific variants automatically (unlike `application-{profile}.properties`) — you must
implement profile logic yourself or combine with `@Profile`.

## Profiles

Spring profiles logically group bean definitions and configuration properties that apply only
in specific environments.

### Activation

- `spring.profiles.active` property (in any property source, highest precedence in its tier)
- `spring.profiles.include` for unconditionally adding profiles alongside active ones
- Command-line: `--spring.profiles.active=dev,postgres`
- Environment variable: `SPRING_PROFILES_ACTIVE=dev`
- `@ActiveProfiles("test")` in JUnit 5 tests (via `@SpringBootTest` or `@DataJpaTest`)

### Profile-specific Property Files

`application-dev.properties`, `application-prod.properties`, `application-test.properties`.
When a profile is active, its file is loaded alongside the base `application.properties` (with
higher precedence for matching keys). Use for environment-specific URLs, credentials, feature
toggles, and logging levels.

### `@Profile`

```java
@Configuration
@Profile("prod")
public class ProdDataSourceConfig {
    @Bean
    public DataSource prodDataSource(...) { ... }
}
```

Beans annotated with `@Profile` are registered only when the named profile(s) are active.
Negation: `@Profile("!test")` registers when the `test` profile is **not** active.

### When to Use Profiles vs Alternatives

|| Approach | Best For | Trade-off |
|| --- | --- | --- |
|| Spring Profiles | Same artefact, different environments (dev/staging/prod), configuration variation | Artifacts remain identical — good for immutable infrastructure; but large profile matrices become hard to reason about |
|| Feature flags (Togglz, LaunchDarkly, FF4J) | Runtime, per-user or per-tenant toggles without redeployment | Requires external flag service or database store; adds runtime dependency and latency |
|| Separate deployable artefacts (different jars, docker images per env) | Large structural differences, conflicting dependencies, compliance isolation | Higher build and deploy cost; loses the "same artefact promoted through environments" benefit |
|| `@ConditionalOnProperty` / `@ConditionalOnExpression` | Low-level bean selection based on a single property | Fine-grained, code-level; harder to see the full picture than profile-level config |

> **Exam tip:** `@ActiveProfiles` in tests replaces the need for `spring.profiles.active` in test
> configuration — it activates the named profiles for the `ApplicationContext` loaded by the test.
> Profile-specific property files (`application-{profile}.properties`) are loaded after the base file
> and override matching keys.

## Dependency Injection

Spring's IoC container manages bean lifecycles and wiring. Component scanning discovers
stereotype-annotated classes and registers them as beans. Constructor injection is the
recommended style for mandatory dependencies; field injection (`@Autowired` on fields) is
discouraged because it hides dependencies, makes testing harder, and couples the class to the
container.

### Component Scanning

`@ComponentScan` (implicit in `@SpringBootApplication`) scans the package of the annotated class
and its sub-packages for `@Component`, `@Service`, `@Repository`, `@Controller`, `@RestController`,
and custom stereotype annotations.

### Stereotype Annotations

|| Annotation | Semantic Intent | AOP / Infrastructure Effect | When It Matters |
|| --- | --- | --- | --- |
|| `@Component` | Generic managed component | None by default | Catch-all when no more specific stereotype fits |
|| `@Service` | Business/service-layer logic | None by default (semantic marker only) | Communicates intent; some teams apply service-layer AOP (transactions, auditing) via this marker |
| `@Repository` | Data-access layer (DAO) | Triggers Spring's `PersistenceExceptionTranslationPostProcessor` — translates database exceptions to Spring's `DataAccessException` hierarchy | Matters when using Spring's exception translation; without it, raw `SQLException`/vendor exceptions propagate |
| `@Controller` | Spring MVC controller (servlet stack) | Marked as a web controller; resolved by `RequestMappingHandlerMapping` | Matters for MVC routing, view resolution, and handler detection |
| `@RestController` | `@Controller` + `@ResponseBody` | Every method return value written directly to the response body (JSON/XML via HttpMessageConverter) | Matters for REST APIs — eliminates the need for `@ResponseBody` on every method |

### `@Configuration` and `@Bean`

`@Configuration` marks a class as a source of bean definitions. `@Bean` methods inside define
explicit bean instances, giving full control over construction, dependencies, and scope.

```java
@Configuration
public class ExternalServiceConfig {

    @Bean
    public RestClient externalRestClient(
            @Value("${app.external-service.base-url}") String baseUrl) {
        return RestClient.builder()
                .baseUrl(baseUrl)
                .build();
    }
}
```

### Constructor Injection

```java
@Service
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    // Preferred: single constructor, no @Autowired needed
    public UserService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }
}
```

- Preferred over field injection: dependencies are visible, the class is container-agnostic,
  and the compiler enforces initialisation.
- Use `final` fields for mandatory dependencies — constructor injection guarantees they are set.
- Linters (and Spring Boot's own inspection) flag field injection as a code smell.

## Validation

Spring Boot integrates Jakarta Bean Validation (formerly Hibernate Validator) for validating
input at method parameters, request bodies, and configuration properties.

### Setup

Add `spring-boot-starter-validation` (or `spring-boot-starter-web` which includes it transitively).
The auto-configuration registers a `LocalValidatorFactoryBean` as the default validator.

### Request Body Validation

```java
@PostMapping("/users")
public ResponseEntity<UserDto> createUser(@Valid @RequestBody CreateUserRequest request) {
    // request validated before method body executes
}
```

- `@Valid` on a `@RequestBody` argument triggers validation of the whole object graph.
- If validation fails, Spring returns a `400 Bad Request` with a `MethodArgumentNotValidException`
  — handled by the default `DefaultHandlerExceptionResolver` or a custom `@ControllerAdvice`.

### Method-Level Validation

```java
@Service
@Validated
public class UserService {

    @NotNull
    public User findUser(@NotNull Long id) {
        // parameter validated before invocation
    }
}
```

- `@Validated` on the class enables Spring's method-level validation proxy (JSR-303 restrictions:
  only public methods on Spring-managed beans are validated).
- Constraint violations throw `ConstraintViolationException`.

### Custom Constraint Validators

```java
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = StrongPasswordValidator.class)
public @interface StrongPassword {
    String message() default "Password must contain uppercase, lowercase, digit, and be 8+ chars";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

public class StrongPasswordValidator implements ConstraintValidator<StrongPassword, String> {
    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        if (value == null) return true; // let @NotNull handle nulls
        return value.matches(".*[A-Z].*") && value.matches(".*[a-z].*")
                && value.matches(".*\\d.*") && value.length() >= 8;
    }
}
```

### Validation Groups

```java
public interface CreateGroup {}
public interface UpdateGroup {}

public class UserDto {

    @NotBlank(groups = CreateGroup.class)
    private String email;

    @NotNull(groups = UpdateGroup.class)
    private Long id;
}

// Validate against a specific group:
@PostMapping
public ResponseEntity<?> create(@Validated(CreateGroup.class) @RequestBody UserDto dto) { ... }
```

Use groups to apply different constraints for create vs update operations without duplicating
DTOs. Default group (no group specified) is `javax.validation.groups.Default`.

> **Exam tip:** `@Valid` triggers validation of the argument it annotates (e.g. a request body
> or a nested object). `@Validated` is a Spring-specific annotation that enables method-level
> validation on the class it marks and can also specify validation groups.

## Actuator & Observability

Spring Boot Actuator exposes operational endpoints for health, metrics, logging, and debugging.
Endpoints are sensitive by default — they must be explicitly exposed and secured in production.

### Key Endpoints

|| Endpoint | Purpose | Typical Exposure |
|| --- | --- | --- |
|| `/actuator/health` | Liveness and readiness probes; aggregates `HealthIndicator` beans | Public (liveness/readiness) or internal only, depending on security posture |
|| `/actuator/info` | Application info from `InfoProperties` (build info, Git commit, custom info) | Public, low sensitivity |
|| `/actuator/metrics` | Micrometer metrics registry overview; `/actuator/metrics/{metricName}` for details | Internal / protected |
|| `/actuator/loggers` | View and dynamically change logger levels at runtime | Internal / protected |
|| `/actuator/heapdump` | Returns a heap dump (HPROF) | Internal / protected — sensitive, can disclose memory contents |
|| `/actuator/traces` | Recent request traces (Servlet, WebFlux, or reactive) | Internal / protected |
|| `/actuator/env` | Environment properties (filtered by `PropertySource` include/exclude) | Internal / protected — exposes configuration |
|| `/actuator/beans` | All Spring beans in the context | Internal / protected |
|| `/actuator/conditions` | Auto-configuration conditions that matched or did not match | Internal / protected |
|| `/actuator/threaddump` | Thread dump (JMX or kernel-level, depending on platform) | Internal / protected |

### Exposure Decision Table

|| Decision | Configuration | When to Use |
|| --- | --- | --- |
|| No exposure | `management.endpoints.web.exposure.include=` (empty) | Maximum security — no actuator endpoints on the network; rely on JMX, logs, or internal diagnostics |
|| Selective exposure | `management.endpoints.web.exposure.include=health,info` | Typical production — expose health for load balancer / Kubernetes probes and info for a status page; keep metrics/env/beans internal |
|| Full exposure | `management.endpoints.web.exposure.include=*` | Development and staging only; never in production without additional network-level protection (firewall, auth proxy) |

```properties
# Example: selective exposure, custom health endpoint path
management.endpoints.web.exposure.include=health,info,metrics
management.endpoint.health.show-details=when-authorized
management.endpoint.health.probes.enabled=true
management.server.port=9090   # optional: run actuator on a separate port
```

### Micrometer Metrics

Actuator uses Micrometer as the metrics facade. Bindings are auto-configured for:

- JvmMemory, JvmGcMetrics, JvmThreadMetrics
- Uptime, SystemMetrics
- Spring MVC request metrics (`http.server.requests`)
- WebFlux metrics
- DataSource pool metrics (HikariCP, etc.)
- Cache metrics
- Custom metrics via `MeterRegistry`

```java
@Service
public class OrderService {
    private final MeterRegistry meterRegistry;

    public OrderService(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }

    public Order createOrder(OrderRequest request) {
        Timer.Sample sample = Timer.start(meterRegistry);
        try {
            Order order = process(request);
            sample.stop(Timer.builder("order.create.success")
                    .tag("status", "ok")
                    .register(meterRegistry));
            return order;
        } catch (Exception e) {
            sample.stop(Timer.builder("order.create.failure")
                    .tag("status", "error")
                    .register(meterRegistry));
            throw e;
        }
    }
}
```

### Structured Logging

Use a structured logging format (JSON) for machine-parseable log aggregation. Spring Boot's
default console output can be switched to JSON via Logback's `logback-spring.xml` or by adding
a structured layout dependency (e.g. `logstash-logback-encoder` or `ecs-logging-java`).

```xml
<!-- logback-spring.xml -->
<appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
    <encoder class="net.logstash.logback.encoder.LogstashEncoder"/>
</appender>
```

Set logging levels per profile: `logging.level.root=INFO`, `logging.level.com.example=DEBUG`
in `application-dev.properties`.

### OpenTelemetry Integration

Spring Boot 3 supports OpenTelemetry via the `micrometer-tracing` bridge:

- `spring-boot-starter-actuator` + `micrometer-tracing-bridge-otel` provides tracing context
  propagation and metric linkage.
- Auto-configuration sets up an `OtterTracer` that bridges Micrometer metrics to OpenTelemetry.
- For full distributed tracing, add the OpenTelemetry Java agent (`-javaagent:path/to/opentelemetry-javaagent.jar`)
  or use the `opentelemetry-spring-boot-starter` for richer instrumentation.
- Trace IDs and span IDs are automatically populated in structured logs when the lineage is
  configured (B3, W3C Trace Context, or Jaeger propagation).

```properties
# Enable tracing with OpenTelemetry bridge
management.tracing.enabled=true
management.tracing.propagation.type=W3C
management.metrics.export.otlp.tracing.endpoint=http://otel-collector:4318/v1/traces
```

### `/actuator` Security Considerations

- Never expose all endpoints (`*`) on a publicly reachable port without authentication.
- Prefer a dedicated management port (`management.server.port=9090`) bound to localhost or a
  protected network segment.
- Use Spring Security to restrict access: `requestMatchers("/actuator/**").hasRole("ACTUATOR")`.
- `health` with `show-details=never` (default) reveals only `UP`/`DOWN` — safe for probes.
- `health.show-details=when-authorized` exposes detail only to authenticated users with the
  required role.

## Configuration Properties

### `@ConfigurationProperties` vs `@Value`

|| Decision | `@ConfigurationProperties` | `@Value` |
|| --- | --- | --- |
|| Bulk binding | Binds a whole group of properties to a typed object in one annotation | One field at a time; no grouping |
|| Type conversion | Automatic (int, boolean, List, Map, Duration, DataSize, etc.) | Manual — inject as String and convert, or use conversion service |
|| Validation | `@Validated` on the class triggers Bean Validation; failures at startup | No built-in validation |
|| IDE support | `spring-boot-configuration-processor` generates `spring-configuration-metadata.json` for autocompletion and documentation | No metadata; IDE sees only the raw property key |
|| Relaxed binding | `my-app.database-url` matches `myApp.databaseUrl` matches `MY_APP_DATABASE_URL` | Exact match only (with some support for bracket notation) |
|| Use for | Structured, related configuration with validation and documentation | One-off, ad-hoc property access where type-safe binding is overkill |
|| When to avoid | When you need only a single property in a non-configuration class and want minimal ceremony | When binding a group of properties — leads to repetitive boilerplate |

### Type-Safe Binding Example

```java
@ConfigurationProperties(prefix = "app.notification")
@Validated
public class NotificationProperties {

    @NotBlank
    private String smtpHost;

    @Min(1)
    @Max(65535)
    private int smtpPort = 25;

    private boolean tlsEnabled = false;

    private final Templates templates = new Templates();

    public static class Templates {
        private String welcomeEmailTemplate;
        private String passwordResetTemplate;
        // getters/setters
    }

    // getters/setters for all fields
}
```

```properties
# application.properties
app.notification.smtp-host=smtp.example.com
app.notification.smtp-port=587
app.notification.tls-enabled=true
app.notification.templates.welcome-email-template=welcome-v2.html
app.notification.templates.password-reset-template=reset-v3.html
```

- Relaxed binding lets you use kebab-case in properties (`smtp-host`) and camelCase in Java
  (`smtpHost`) — they bind automatically.
- Nested properties (`templates.welcome-email-template`) map to the inner `Templates` class.

### Metadata Generation

Add the configuration processor to generate IDE metadata:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-configuration-processor</artifactId>
    <optional>true</optional>
</dependency>
```

- The processor scans `@ConfigurationProperties` classes at compile time and produces
  `META-INF/spring-configuration-metadata.json`.
- IDEs (IntelliJ, VS Code with Spring Boot Extension Pack) use this for autocompletion,
  hover documentation, and validation of property keys.
- Add Javadoc comments to fields to populate the metadata description field.

```java
/**
 * SMTP host name for outbound notifications.
 */
private String smtpHost;
```

## MVC vs WebFlux

Spring MVC (servlet stack) and Spring WebFlux (reactive stack) are the two web stacks in
Spring Boot. The choice depends on workload characteristics, team familiarity, and library
ecosystem needs.

### Side-by-Side Comparison

|| Aspect | Spring MVC | Spring WebFlux |
|| --- | --- | --- |
|| Stack | Servlet stack (Jakarta Servlet API), blocking I/O by default | Reactive stack (Reactor Netty by default, or servlet 3.1+ with async), non-blocking I/O |
| Programming model | Imperative — request/response in a single thread per request; return values written after processing completes | Functional or annotated `@RestController` with reactive return types (`Mono<T>`, `Flux<T>`); backpressure-aware |
| Concurrency model | One thread per request (thread pool bound); thread holds during blocking calls (DB, HTTP client, file I/O) | Few threads (event-loop) handle many concurrent connections; no thread is held during I/O waits |
| Maturity / ecosystem | Mature — vast library support, every Spring module integrates, easy debugging (thread dumps, step-through debugging) | Newer — some integrations are reactive-aware (Spring Data R2DBC, reactive Redis), others block and negate the benefit |
| Blocking I/O in the call chain | Acceptable but thread-consumption scales with concurrent requests — can exhaust the thread pool under load | Problematic — a single blocking call in the chain blocks the event-loop thread; use reactive clients or off-load to a bounded elastic scheduler |
| Streaming / SSE / backpressure | Possible (SSE with `SseEmitter`, file download with `ResourceHttpMessageConverter`) but not built into the core model | Native — `Flux<T>` supports backpressure, server-sent events, and infinite streaming naturally |
| Debugging | Thread-local access, stack traces map directly to request threads, familiar tooling (profiler, debugger, thread dumps) | Reactive stack traces can be deep and harder to read; timeline debugging and checkpointing help but require learning |
| When to choose | Most traditional web applications, REST APIs with moderate concurrency, teams familiar with Spring MVC, projects with blocking dependencies (JDBC, blocking HTTP clients) | High-concurrency streaming workloads, SSE with many concurrent subscribers, scenarios where thread efficiency matters, reactive end-to-end chains |
| When NOT to use WebFlux | When the workload is request/response with a few hundred to low-thousands concurrent requests and blocking dependencies dominate; when the team has no reactive experience and the project timeline is tight; when key dependencies (ORM, HTTP client, messaging client) have no reactive variant — a single blocking call in the chain undermines the reactive model | When you would end up calling `.block()` or wrapping blocking calls in a scheduler for the majority of the call chain — you pay the reactive learning cost without the concurrency benefit |

> **Exam tip:** WebFlux is not "faster MVC" — it trades thread-per-request for an event-loop
> model. If the workload is I/O-heavy and the reactive chain is end-to-end, fewer threads serve
> more connections. If the workload is CPU-heavy or uses blocking libraries throughout, MVC is
> simpler and equally performant for the concurrency levels most services encounter.

## Decision Flow

```mermaid
--8<-- "programming/java/diagrams/spring-boot/processing-model-selection.mmd"
```

## Native Images

Spring Boot 3 supports GraalVM native image compilation via Spring Native (integrated into the
core framework as of Spring Boot 3). Native images Ahead-of-Time (AOT) compile the application
to a standalone native executable, trading build complexity and flexibility for fast startup and
low memory footprint.

### Build-Time vs Startup-Time Trade-Offs

|| Dimension | JVM (traditional) | Native Image (GraalVM) |
|| --- | --- | --- |
|| Startup time | Seconds (JVM warm-up, class loading, JIT compilation) | Milliseconds to low hundreds of milliseconds (no class loading at runtime, no JIT warm-up) |
|| Memory footprint | Higher — JVM overhead, JIT code cache, heap | Lower — no JVM, smaller runtime footprint, suitable for tight-memory containers and serverless |
|| Build / deploy | Fast build (javac + jar); deploy anywhere with a JRE | Slower build (AOT compilation can take minutes); executable tied to the OS/CPU architecture it was compiled for |
|| Runtime performance | JIT optimisation over time — peak performance improves after warm-up | Ahead-of-time compiled — starts at peak, no warm-up curve, but JIT optimisations unavailable |
|| Reflection / dynamic classloading | Full support | Limited — reflection must be registered at build time via `reflection-config.json` or Spring's AOT processing; dynamic classloading (e.g. classpathear, some surrogate CLs) limited or unavailable |
|| Proxies (CGLIB, JDK dynamic proxies) | Full support at runtime | Proxies must be resolved at build time — Spring's AOT processor generates proxy configuration; some proxy patterns may not be representable in a native image |
|| Resource bundles | On-demand from classpath | Resources must be registered for inclusion in the native image; Spring's `ResourceHints` and `spring.aot.info` properties help, but some resources may be missed without explicit configuration |

### When Native Images Are Worth the Complexity

- **Serverless / Function-as-a-Service** (AWS Lambda, Azure Functions with custom runtime): fast
  cold-start is critical; native images dramatically reduce cold-start latency and memory.
- **Tight-memory containers** (small container limits, high-density deployments): lower RSS
  footprint reduces memory pressure and cost.
- **Embedded / edge devices** where a full JVM is too heavy.

### When to Stick with a JVM

- Complex applications with heavy reflection, dynamic proxies, or runtime bytecode generation
  (Hibernate without static metamodel, sophisticated AOP, scripting engines).
- Teams without GraalVM build infrastructure or expertise.
- Applications where build time matters (frequent builds, CI time-sensitive pipelines) and the
  startup/memory benefit is marginal for the deployment target.

### Reflection and Resource Registration

Spring Boot 3's AOT processing auto-generates much of the reflection and resource configuration
during the build, but some cases still require manual hints:

```properties
# spring-aot.properties or application.properties
spring.aot.info.binary=lite   # or full
spring.native.register-objects-for-reflection=com.example.MyDto\,com.example.AnotherDto
```

```xml
<!-- pom.xml: enable native profile -->
<profile>
    <id>native</id>
    <build>
        <plugins>
            <plugin>
                <groupId>org.graalvm.buildtools</groupId>
                <artifactId>native-maven-plugin</artifactId>
                <configuration>
                    <classpath>...</classpath>
                </configuration>
            </plugin>
        </plugins>
    </build>
</profile>
```

```bash
# Build the native image
./mvnw -Pnative native:compile
# Run
./target/myapp
```

> **Exam tip:** Native image support in Spring Boot 3 requires GraalVM 22.3+ (or the GraalVM
> JDK build) and the `org.graalvm.buildtools.native` plugin. The Spring AOT processor performs
  a build-time analysis pass to generate the proxy, reflection, and resource hints automatically
  for most Spring-authored code; third-party libraries without AOT support may still require
  manual `reflection-config.json` entries.

## Component Stereotype Decision Table

|| Stereotype | Semantic Intent | Infrastructure / AOP Effect | Use When |
|| --- | --- | --- | --- |
|| `@Component` | Generic Spring-managed component — any class that should be a bean but does not fit a more specific role | No automatic infrastructure behaviour | Utility beans, custom components, classes that are neither service, repository, nor web controller |
|| `@Service` | Service-layer business logic | No automatic behaviour by default (purely semantic); commonly used as the target for `@Transactional` and service-layer AOP (auditing, logging, security) | Business logic orchestrating repositories and other services; communicates intent to readers |
|| `@Repository` | Data-access object (DAO), repository | `PersistenceExceptionTranslationPostProcessor` intercepts and translates database exceptions to Spring's `DataAccessException` hierarchy (unchecked). Also a marker for Spring Data repository proxies. | Classes that directly access persistence (JDBC, JPA, Spring Data repositories); exception translation matters when you want vendor-agnostic data access exceptions |
|| `@Controller` | Spring MVC controller (servlet stack) | Handler mapping detects it; resolves request mappings; integrates with view resolution if returning view names | MVC applications serving views or handling requests that return `ModelAndView` / view names |
|| `@RestController` | `@Controller` + `@ResponseBody` — every method return value written to the HTTP response body | Same as `@Controller`, plus automatic body conversion (JSON/XML via `HttpMessageConverter`); no view resolution | REST APIs where every handler writes JSON, XML, or other content directly to the response; eliminates repetitive `@ResponseBody` |

### When the Distinction Actually Matters

- **`@Repository` exception translation**: If you annotate a class with `@Repository` and have
  `Spring Boot Starter Data JPA` or `spring-boot-starter-jdbc` on the classpath, Spring's
  `PersistenceExceptionTranslationPostProcessor` automatically applies exception translation.
  Without `@Repository`, raw `SQLException` or `PersistenceException` propagates — losing the
  abstraction. This is the one stereotype with a meaningful runtime effect beyond semantics.
- **`@RestController` vs `@Controller`**: The distinction matters at the HTTP response level —
  `@RestController` skips view resolution entirely. Using `@Controller` for a REST endpoint means
  every handler method needs `@ResponseBody`; forgetting it results in a view-resolution attempt
  and a runtime error.
- **`@Service` as a semantic anchor**: While `@Service` has no automatic Spring behaviour, it is
  the conventional target for `@Transactional` services and for service-layer AOP (security
  checks, audit logging). Using `@Component` instead does not break functionality, but it
  obscures intent and can confuse readers and tooling.
- **`@Component` catch-all**: Prefer the most specific stereotype available. A class that clearly
  belongs to the service layer should be `@Service`; a data-access class should be `@Repository`.
  Reserve `@Component` for cases where no better fit exists — this maximises readability and
  makes the role of each bean immediately clear from its annotation.
