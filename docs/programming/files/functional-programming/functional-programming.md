# FUNCTIONAL PROGRAMMING

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
