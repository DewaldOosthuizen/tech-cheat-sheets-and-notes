# JAVA

Quick-reference cheat sheet for Java, targeting the latest LTS release (**Java 21**).
Comparison-oriented — covers language fundamentals, core OOP concepts, functional features,
string idioms, and the JDBC/JPA/Lombok stack used in typical enterprise applications.

## Language Basics & Keywords

| Category | Keywords / Types | Key Feature |
| --- | --- | --- |
| Primitive types | `byte`, `short`, `int`, `long`, `float`, `double`, `char`, `boolean` | Stack-allocated, no autoboxing overhead unless used in generics/collections |
| Access modifiers | `public`, `protected`, `private`, (package-private, no keyword) | Control visibility across package and inheritance boundaries |
| Non-access modifiers | `static`, `final`, `abstract`, `synchronized`, `transient`, `volatile` | `final` = immutable reference/no override; `static` = class-level, not instance-level |
| Control flow | `if/else`, `switch`, `for`, `while`, `do-while`, `for-each` | `switch` supports pattern matching and arrow syntax (`->`) since Java 14+ |
| Exception handling | `try`, `catch`, `finally`, `throw`, `throws` | `try-with-resources` auto-closes `AutoCloseable` resources |
| Records (Java 16+) | `record` | Immutable data carrier — auto-generates constructor, accessors, `equals`/`hashCode`/`toString` |
| Sealed types (Java 17+) | `sealed`, `non-sealed`, `permits` | Restricts which classes/interfaces may extend/implement a type |
| Text blocks (Java 15+) | `"""` | Multi-line string literals without escape-heavy concatenation |

> **Exam tip:** `var` (Java 10+) is local-variable type inference only — it cannot be used for
> fields, method parameters, or return types. The compiler still enforces static typing; `var`
> is sugar, not dynamic typing.

## Core OOP Concepts

| Concept | Description | Key Feature |
| --- | --- | --- |
| **Encapsulation** | Bundling state and behaviour, exposing only what's needed via access modifiers | Private fields + public getters/setters (or records for immutable data) |
| **Inheritance** | A class (`extends`) reuses and specialises another class's members | Single inheritance for classes; `super` accesses parent members |
| **Polymorphism** | Same method signature, different runtime behaviour | Method overriding (runtime) vs overloading (compile-time) |
| **Abstraction** | Expose behaviour contracts without exposing implementation details | Abstract classes and interfaces |

### Interface vs Abstract Class

| Aspect | Interface | Abstract Class |
| --- | --- | --- |
| Multiple inheritance | Yes — a class can implement several interfaces | No — a class extends only one abstract class |
| State (instance fields) | No instance fields (only `static final` constants) | Can hold instance fields |
| Constructors | Not allowed | Allowed |
| Method bodies | `default` and `static` methods can have bodies (Java 8+) | Any method can have a body |
| When to choose | Define a capability/contract shared across unrelated types | Share common state and partial implementation among closely related types |

> **Exam tip:** Prefer interfaces for defining a contract implementable by unrelated classes;
> prefer an abstract class when subclasses share common state or a partial implementation.

## Lambda & Functional Interfaces

| Interface | Method | Use Case |
| --- | --- | --- |
| `Function<T, R>` | `R apply(T t)` | Transform an input into an output |
| `Predicate<T>` | `boolean test(T t)` | Boolean-valued condition, e.g. filtering |
| `Consumer<T>` | `void accept(T t)` | Perform an action, no return value |
| `Supplier<T>` | `T get()` | Provide/produce a value, no input |
| `BiFunction<T, U, R>` | `R apply(T t, U u)` | Transform two inputs into an output |
| `UnaryOperator<T>` | `T apply(T t)` | `Function<T, T>` specialisation |

### Method References

| Form | Example | Equivalent Lambda |
| --- | --- | --- |
| Static method | `Integer::parseInt` | `s -> Integer.parseInt(s)` |
| Instance method (particular object) | `list::add` | `x -> list.add(x)` |
| Instance method (arbitrary object of a type) | `String::toUpperCase` | `s -> s.toUpperCase()` |
| Constructor | `ArrayList::new` | `() -> new ArrayList<>()` |

### Streams Basics

```java
List<String> names = List.of("Bilbo", "Frodo", "Gandalf", "Aragorn");

List<String> longNames = names.stream()
    .filter(n -> n.length() > 5)
    .map(String::toUpperCase)
    .sorted()
    .toList(); // Java 16+ terminal shortcut for Collectors.toList()
```

> **Exam tip:** Streams are lazily evaluated — intermediate operations (`filter`, `map`) only
> execute once a terminal operation (`collect`, `toList`, `forEach`, `reduce`) is invoked.

## String Manipulation

Strings are **immutable** in Java — every "modifying" operation returns a new `String`.
For heavy in-loop concatenation, prefer `StringBuilder` to avoid quadratic allocation cost.

### String Reversal

```java
// StringBuilder — idiomatic, O(n)
String reversed = new StringBuilder("Gandalf").reverse().toString();

// char array swap — no intermediate object allocation per step
char[] chars = "Gandalf".toCharArray();
for (int i = 0, j = chars.length - 1; i < j; i++, j--) {
    char tmp = chars[i];
    chars[i] = chars[j];
    chars[j] = tmp;
}
String reversedManual = new String(chars);
```

### Common Idioms

| Task | Idiom |
| --- | --- |
| Join strings | `String.join(", ", list)` |
| Check blank/empty | `str.isBlank()` (Java 11+) vs `str.isEmpty()` |
| Repeat | `"ab".repeat(3)` → `"ababab"` (Java 11+) |
| Format | `"%s is %d".formatted(name, age)` (Java 15+) |
| Compare ignoring case | `str.equalsIgnoreCase(other)` |

> **Exam tip:** `StringBuilder` is not thread-safe; `StringBuffer` is the synchronized
> equivalent. Choose `StringBuilder` unless multiple threads mutate the same buffer.

## JDBC

JDBC (Java Database Connectivity) is the low-level API for direct SQL access.

```java
String url = "jdbc:postgresql://localhost:5432/mydb";
try (Connection conn = DriverManager.getConnection(url, user, password);
     PreparedStatement stmt = conn.prepareStatement(
         "SELECT id, name FROM users WHERE id = ?")) {
    stmt.setLong(1, userId);
    try (ResultSet rs = stmt.executeQuery()) {
        while (rs.next()) {
            System.out.println(rs.getString("name"));
        }
    }
}
```

| Statement Type | Use Case | Key Feature |
| --- | --- | --- |
| `Statement` | Static SQL with no parameters | No parameter binding — vulnerable to SQL injection if concatenating input |
| `PreparedStatement` | Parameterised, repeatable queries | Pre-compiled; safe parameter binding; better performance for repeated execution |
| `CallableStatement` | Invoking stored procedures | Supports IN/OUT/INOUT parameters |

> **Exam tip:** Always use `PreparedStatement` (or higher) when any part of the SQL includes
> user input — parameter binding prevents SQL injection that string concatenation invites.

## JPA

JPA (Jakarta Persistence API) is the ORM specification implemented by providers such as
Hibernate and EclipseLink, mapping Java objects to relational rows declaratively.

```java
@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    // getters/setters omitted
}
```

```java
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByName(String name);

    @Query("SELECT u FROM User u WHERE u.name LIKE %:term%")
    List<User> searchByName(@Param("term") String term);
}
```

### JDBC vs JPA

| Aspect | JDBC | JPA |
| --- | --- | --- |
| Abstraction level | Low-level SQL execution | Object-relational mapping |
| Boilerplate | High — manual result-set mapping | Low — entities mapped via annotations |
| Query language | Raw SQL | JPQL (object-graph aware) or native SQL |
| Caching | None built-in | First-level (session) and optional second-level cache |
| Performance control | Full manual control | Abstracted — requires care to avoid N+1 queries |
| When to choose | Fine-grained performance tuning, simple scripts, no ORM overhead desired | Rich domain models, rapid development, relationship-heavy schemas |

> **Exam tip:** JPQL queries operate on entity object graphs, not table/column names directly —
> `SELECT u FROM User u` refers to the `User` entity class, not the `users` table.

## Lombok

Lombok is an annotation processor that generates boilerplate (getters, setters, constructors,
`equals`/`hashCode`, builders) at compile time, reducing repetitive code in POJOs and entities.

| Annotation | Key Feature |
| --- | --- |
| `@Getter` / `@Setter` | Generates accessor/mutator methods for all (or annotated) fields |
| `@ToString` | Generates a `toString()` implementation |
| `@EqualsAndHashCode` | Generates `equals()`/`hashCode()` based on fields |
| `@NoArgsConstructor` | Generates a no-argument constructor |
| `@AllArgsConstructor` | Generates a constructor with all fields as parameters |
| `@RequiredArgsConstructor` | Generates a constructor for `final`/`@NonNull` fields only |
| `@Data` | Bundles `@Getter`, `@Setter`, `@ToString`, `@EqualsAndHashCode`, `@RequiredArgsConstructor` |
| `@Builder` | Generates a fluent builder for object construction |
| `@Slf4j` | Injects a preconfigured `Logger` field named `log` |

```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserDto {
    private Long id;
    private String name;
}
```

> **Exam tip:** `@Data` is a convenience bundle, not a silver bullet — avoid it on JPA `@Entity`
> classes where `equals`/`hashCode` based on all mutable fields (rather than the identifier) can
> break collection semantics once an entity is persisted and its ID is assigned.

## Collection Type Selection

```mermaid
--8<-- "programming/diagrams/java/collection-selection-decision-flow.mmd"
```

> **Exam tip:** `ArrayList` gives O(1) indexed access but O(n) insert/remove in the middle;
> `LinkedList` gives O(1) insert/remove at known positions but O(n) indexed access. Choose based
> on whether the workload is index-lookup-heavy or mutation-heavy.
