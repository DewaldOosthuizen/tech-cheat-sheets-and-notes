# LANGUAGE FUNDAMENTALS

Quick-reference cheat sheet for Java, targeting the latest LTS release (**Java 21**).
Comparison-oriented — covers language fundamentals and string idioms.

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
