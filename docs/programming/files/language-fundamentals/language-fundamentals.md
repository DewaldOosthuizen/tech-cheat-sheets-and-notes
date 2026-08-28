# LANGUAGE FUNDAMENTALS

Quick-reference cheat sheet for Java, targeting the latest LTS release (**Java 21**).
Comparison-oriented — covers language fundamentals and string idioms.

## Language Basics & Keywords

|| Category | Keywords / Types | Key Feature | Since | Status |
|| --- | --- | --- | --- | --- |
|| Primitive types | `byte`, `short`, `int`, `long`, `float`, `double`, `char`, `boolean` | Stack-allocated, no autoboxing overhead unless used in generics/collections | Java 1 | Final |
|| Access modifiers | `public`, `protected`, `private`, (package-private, no keyword) | Control visibility across package and inheritance boundaries | Java 1 | Final |
|| Non-access modifiers | `static`, `final`, `abstract`, `synchronized`, `transient`, `volatile` | `final` = immutable reference/no override; `static` = class-level, not instance-level | Java 1 | Final |
|| Control flow | `if/else`, `switch`, `for`, `while`, `do-while`, `for-each` | `switch` supports pattern matching and arrow syntax (`->`) since Java 14+ | Java 1 | Final |
|| Exception handling | `try`, `catch`, `finally`, `throw`, `throws` | `try-with-resources` auto-closes `AutoCloseable` resources | Java 1 | Final |
|| Records | `record` | Immutable data carrier — auto-generates constructor, accessors, `equals`/`hashCode`/`toString` | Java 16 | Final |
|| Sealed types | `sealed`, `non-sealed`, `permits` | Restricts which classes/interfaces may extend/implement a type | Java 17 | Final |
|| Text blocks | `"""` | Multi-line string literals without escape-heavy concatenation | Java 15 | Final |
|| Switch pattern matching | `case L ->` with patterns | Pattern matching in switch labels; guarded patterns with `when` | Java 21 | Final |
|| Record patterns | Nested record decomposition in `instanceof` and `switch` | Decompose record values directly in pattern matching | Java 21 | Final |
|| Sequenced collections | `SequencedCollection`, `SequencedSet`, `SequencedMap` | `getFirst`/`getLast`, `addFirst`/`addLast`, `reversed()` view | Java 21 | Final |

> **Exam tip:** `var` (Java 10+) is local-variable type inference only — it cannot be used for
> fields, method parameters, or return types. The compiler still enforces static typing; `var`
> is sugar, not dynamic typing.

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

|| Task | Idiom |
|| --- | --- |
|| Join strings | `String.join(", ", list)` |
|| Check blank/empty | `str.isBlank()` (Java 11+) vs `str.isEmpty()` |
|| Repeat | `"ab".repeat(3)` → `"ababab"` (Java 11+) |
|| Format | `"%s is %d".formatted(name, age)` (Java 15+) |
|| Compare ignoring case | `str.equalsIgnoreCase(other)` |

> **Exam tip:** `StringBuilder` is not thread-safe; `StringBuffer` is the synchronized
> equivalent. Choose `StringBuilder` unless multiple threads mutate the same buffer.

## Java 21 LTS — New in this Release

### Virtual threads

Virtual threads are the headline feature of Java 21. They are lightweight, JVM-managed threads
that let a single carrier (platform) thread multiplex millions of virtual threads, making
high-throughput blocking I/O achievable without the complexity of reactive or callback-based code.

**Creating virtual threads:**

```java
// One-shot virtual thread
Thread.startVirtualThread(() -> {
    System.out.println("Running on a virtual thread: " + Thread.currentThread());
});

// Executor service backed by virtual threads
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 1000; i++) {
        executor.submit(() -> doBlockingIo());
    }
}
```

Virtual threads shine when each task spends most of its time blocked on I/O — reading from a
socket, waiting on a JDBC call, or sleeping. The JVM parks the virtual thread and frees the carrier
thread to run other work. In contrast, a fixed pool of platform threads (e.g. `Executors.newFixedThreadPool`)
would starve under the same load because each blocked platform thread is an expensive, OS-level resource.

**Pinning — what defeats the model:**

A virtual thread becomes *pinned* to its carrier thread when it enters a `synchronized` block or
method, or when it calls a native method. While pinned, the carrier thread cannot be reused for other
virtual threads. Avoid `synchronized` in hot paths on virtual threads; prefer `ReentrantLock` or
other `java.util.concurrent` synchronizers, which do not pin. Refactor legacy `synchronized` blocks
that wrap long-running I/O first — do not blanket-replace all `synchronized` usage without measuring.

**Connection pools are still required:**

Virtual threads do **not** remove database connection-pool limits. A connection pool (HikariCP,
etc.) bounds the number of concurrent physical connections to the database — an external, expensive
resource that does not scale with the number of threads. If 100,000 virtual threads each tried to
open a dedicated connection, the database would collapse long before the application did. Virtual
threads change the thread-scaling model, not the resource-scaling model. Size the pool for the
database, not for the thread pool, and let virtual threads queue transparently when all connections
are in use.

Stability: **Final — Java 21**

### Record patterns

Record patterns let you decompose record values directly in `instanceof` and `switch`, eliminating
the manual extraction boilerplate that preceded Java 21.

**Before Java 21 — manual extraction:**

```java
record Point(int x, int y) {}
record Circle(Point centre, double radius) {}

void oldWay(Object obj) {
    if (obj instanceof Circle) {
        Circle c = (Circle) obj;
        Point centre = c.centre();
        int x = centre.x();
        int y = centre.y();
        double r = c.radius();
        System.out.printf("Circle at (%d,%d) radius %f%n", x, y, r);
    }
}
```

**Java 21 — record pattern decomposition:**

```java
void newWay(Object obj) {
    if (obj instanceof Circle(Point(int x, int y), double r)) {
        System.out.printf("Circle at (%d,%d) radius %f%n", x, y, r);
    }
}
```

Nested records decompose in a single pattern — `Point(int x, int y)` inside `Circle(...)` extracts
both the centre and its coordinates without intermediate variables.

Stability: **Final — Java 21**

### Pattern matching for `switch`

Pattern matching for `switch` (final in Java 21) extends the switch block with type patterns,
guarded patterns (`when`), and null handling. It replaces chains of `if-else` and casting with
declarative dispatch.

**Before Java 21 — if-else chain:**

```java
String describe(Object obj) {
    if (obj instanceof Circle) {
        Circle c = (Circle) obj;
        return "Circle radius " + c.radius();
    } else if (obj instanceof Rectangle) {
        Rectangle r = (Rectangle) obj;
        return "Rectangle " + r.width() + "x" + r.height();
    } else if (obj instanceof Point p && p.x() == 0 && p.y() == 0) {
        return "Origin";
    }
    return "Unknown shape";
}
```

**Java 21 — pattern-matching switch:**

```java
String describe(Object obj) {
    return switch (obj) {
        case Circle(Point(int x, int y), double r) ->
            "Circle at (%d,%d) radius %f".formatted(x, y, r);
        case Rectangle(double w, double h) ->
            "Rectangle %fx%f".formatted(w, h);
        case Point(int x, int y) when x == 0 && y == 0 ->
            "Origin";
        case Point(int x, int y) ->
            "Point at (%d,%d)".formatted(x, y);
        case null -> "Null";
        default -> "Unknown shape";
    };
}
```

**Dominance and totality:**

A switch block must be *total* — every possible value of the selector must match some case.
Adding a `default` label satisfies totality for reference types; for `sealed` hierarchies the
compiler can verify completeness without `default`. A *dominance* error occurs when an earlier
case matches all the values a later case would match — the compiler rejects the unreachable case.
Order specific patterns (e.g. `Point(0, 0)`) before general ones (e.g. `Point(int x, int y)`) to
avoid dominance errors.

Stability: **Final — Java 21**

### Sequenced collections

Java 21 introduces the SequencedCollection, SequencedSet, and SequencedMap interfaces, which
give every ordered collection a uniform API for accessing first and last elements, adding to either
end, and obtaining a reversed view — without depending on whether the collection is a List, Deque,
or LinkedHashMap.

```java
// SequencedCollection — works with List, Deque, etc.
SequencedCollection<String> col = new ArrayList<>(List.of("one", "two", "three"));
String first = col.getFirst();   // "one"
String last  = col.getLast();    // "three"
col.addFirst("zero");
col.addLast("four");
SequencedCollection<String> reversed = col.reversed(); // view, O(1)

// SequencedSet — unique sequenced elements
SequencedSet<String> set = new LinkedHashSet<>(Set.of("a", "b", "c"));
set.addFirst("z");
set.addLast("d");

// SequencedMap — ordered map with first/last entry access
SequencedMap<String, Integer> map = new LinkedHashMap<>(Map.of("x", 1, "y", 2));
map.putFirst("w", 0);
map.putLast("z", 3);
Map.Entry<String, Integer> firstEntry = map.firstEntry();
Map.Entry<String, Integer> lastEntry  = map.lastEntry();
```

The reversed() view is a live, O(1) view — mutations to the original are reflected in the reversed
view and vice versa (where the operation makes sense for the underlying collection type).

Stability: **Final — Java 21**

### Scoped values (Preview — Java 21)

Scoped values (Incubator in Java 20, Preview in Java 21) provide a way to share data within a
thread and its child threads without resorting to ThreadLocal. A scoped value is written once,
bound for the duration of a ScopedValue.where(...).run(...) call, and visible to all code in that
thread — including virtual threads spawned inside the scope.

```java
static final ScopedValue<String> CURRENT_USER = ScopedValue.newInstance();

void handleRequest() {
    ScopedValue.where(CURRENT_USER, "gandalf").run(() -> {
        // CURRENT_USER.get() returns "gandalf" in this thread and any child threads
        process();
    });
}
```

Scoped values are a preview API at Java 21. Preview APIs can change between releases — do not rely
on them in production until they are final.

Stability: Preview — Java 21
