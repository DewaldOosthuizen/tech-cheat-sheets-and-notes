# COLLECTIONS

Quick-reference cheat sheet for Java, targeting the latest LTS release (**Java 21**).

```mermaid
--8<-- "programming/diagrams/java/collection-selection-decision-flow.mmd"
```

## Core Concepts

Java's collection framework provides three foundational interfaces: `List` (ordered, indexable, allows duplicates), `Set` (unique elements, no duplicates), and `Map` (key-value pairs, unique keys). The diagram above guides selection based on access pattern and ordering requirements.

## Queue Family

| Type | Interface | Single/double-ended | Ordering | Blocking | Nulls |
| --- | --- | --- | --- | --- | --- |
| `Queue` | `java.util.Queue` | Single-ended (offer/poll at head) | Typically FIFO | No | Depends on implementation |
| `Deque` | `java.util.Deque` | Double-ended (add/remove at both ends) | Typically FIFO or LIFO | No | `ArrayDeque` rejects nulls |
| `PriorityQueue` | `java.util.PriorityQueue` | Single-ended | Heap-ordered (natural or comparator) | No | Rejects nulls |
| `BlockingQueue` | `java.util.concurrent.BlockingQueue` | Single or double-ended | Depends on subtype | Yes — producer/consumer semantics | Depends on subtype |

### Queue vs Deque vs PriorityQueue vs BlockingQueue

- **`Queue`** — A single-ended queue where elements are inserted at the tail and removed from the head. Typical use: FIFO processing pipelines. `LinkedList` and `ArrayDeque` both implement `Queue`.

- **`Deque`** (double-ended queue) — Extends `Queue` to support insertion and removal at both ends. Use when you need LIFO (stack) semantics or efficient operations at both ends. `ArrayDeque` is the preferred implementation: it is array-backed and has lower per-element overhead than a linked implementation.

- **`PriorityQueue`** — Orders elements by natural order or a provided `Comparator` using a binary heap. It is *not* a stable sort — iteration order does not guarantee FIFO among equal-priority elements, and there is no indexed access. Use when you need to repeatedly extract the minimum or maximum element, not when you need sorted iteration.

- **`BlockingQueue`** — Extends `Queue` with blocking `put`/`take` operations that wait if the queue is full/empty. Designed for producer/consumer patterns (e.g. thread pools, work queues). See subtypes below.

### BlockingQueue Subtypes

| Implementation | Backed by | Bounded? | Ordering | Nulls | Notes |
| --- | --- | --- | --- | --- | --- |
| `ArrayBlockingQueue` | Array | Yes (fixed capacity) | FIFO | Rejects nulls | Fast, predictable memory, fair/unfair locking |
| `LinkedBlockingQueue` | Linked nodes | Optional (default: `Integer.MAX_VALUE`) | FIFO | Rejects nulls | Higher per-node memory than array-backed; can grow very large if unbounded |
| `PriorityBlockingQueue` | Binary heap | Unbounded (grows as needed) | Heap-ordered | Rejects nulls | Same ordering caveats as `PriorityQueue`; not stable |
| `DelayQueue` | Priority queue of delayed elements | Unbounded | Elements available only after their delay expires | Rejects nulls | Each element must implement `java.util.concurrent.Delayed` |
| `SynchronousQueue` | No internal storage (handoff) | No capacity (capacity = 0) | Handoff — put blocks until a take is ready, and vice versa | N/A | Useful for direct thread-to-thread handoff; does not hold elements |

## Thread-Safe and Concurrent Collections

### ConcurrentHashMap

- Segmented/locally-locked: updates lock only the affected hash bucket/segment, not the whole map.
- Iterators are **weakly consistent** — they reflect the state of the map at or since the iterator's creation; they do not throw `ConcurrentModificationException` but may or may not see concurrent updates.
- **Rejects null keys and null values** unlike `HashMap`.
- Suitable for high-concurrency key-value workloads where read-heavy access patterns dominate and update contention must be minimised.

### CopyOnWriteArrayList

- On every mutating operation (add, set, remove, etc.), the entire underlying array is copied and replaced.
- Iterators return a **snapshot** of the array at iterator creation time — they never see subsequent mutations and never throw `ConcurrentModificationException`.
- Memory cost on mutation: each write allocates a new array of the current size.
- **Workload assumption:** high read, low write. If writes are frequent, the copy cost dominates and a different synchronisation strategy (e.g. `Collections.synchronizedList` or a concurrent queue) is preferable.
- No null rejection policy — it accepts null elements like `ArrayList`.

### ConcurrentLinkedQueue

- Lock-free, non-blocking FIFO queue implemented with CAS operations on a linked list.
- **Rejects null elements** — attempting to add null throws `NullPointerException`.
- Does not support blocking; use `BlockingQueue` subtypes when producer/consumer blocking semantics are needed.
- Suitable for high-throughput, single-producer/single-consumer or multi-producer/multi-consumer scenarios where wait-free progress is desired.

## Immutable Factory Collections

Java 9+ provides `List.of`, `Set.of`, `Map.of`, and `Map.ofEntries` for creating small, immutable collection instances. These are not just "unmodifiable wrappers" — they are compact, optimised representations for small numbers of elements.

### Characteristics

| Factory | Allows null elements | Allows duplicates | Mutability |
| --- | --- | --- | --- |
| `List.of(...)` | No — throws `NullPointerException` | No — duplicates are stored (List semantics) but the list is unmodifiable | Unmodifiable |
| `Set.of(...)` | No — throws `NullPointerException` | No — duplicate elements cause `IllegalArgumentException` at creation time | Unmodifiable |
| `Map.of(...)` | No — null keys or values throw `NullPointerException` | No — duplicate keys cause `IllegalArgumentException` at creation time | Unmodifiable |

- The resulting collections reject any mutative operation (`add`, `remove`, `put`, etc.) with `UnsupportedOperationException`.
- They do **not** wrap a mutable collection — they are independently immutable. Passing them to a method that mutates a collection reference will not cause accidental mutation *of the factory instance*, but any other live reference to the same mutable backing store would still be at risk if the original was mutable.
- Small-collection optimisation: for very small argument counts (typically ≤ 10 for `List.of`/`Set.of`, ≤ 10 for `Map.of`), the runtime uses specialised compact implementations rather than a general-purpose wrapper.

### When to Use

- Configuration values, constant sets, or API return values that must not be altered by the caller.
- Snapshot semantics: when you need a guaranteed-immutable view of a collection at a point in time.
- Not suitable as a drop-in replacement for every collection — for large or frequently-mutated collections, use mutable implementations and optionally wrap with `Collections.unmodifiableList`/`Set`/`Map` if read-only access must be enforced on a shared reference.

## Null Handling — Quick Reference

| Collection | Null keys | Null values | Null elements |
| --- | --- | --- | --- |
| `HashMap` | Yes | Yes | N/A |
| `HashSet` | N/A | N/A | Yes (one null element allowed) |
| `ArrayList` | N/A | N/A | Yes |
| `LinkedList` | N/A | N/A | Yes |
| `ArrayDeque` | N/A | N/A | **No** — throws `NullPointerException` |
| `ConcurrentHashMap` | **No** | **No** | N/A |
| `ConcurrentLinkedQueue` | N/A | N/A | **No** |
| `ArrayBlockingQueue` | N/A | N/A | **No** |
| `LinkedBlockingQueue` | N/A | N/A | **No** |
| `PriorityBlockingQueue` | N/A | N/A | **No** |
| `DelayQueue` | N/A | N/A | **No** |
| `SynchronousQueue` | N/A | N/A | N/A (no storage) |
| `List.of` / `Set.of` / `Map.of` | N/A | **No** (`Map.of`) | **No** |

## Workload Assumptions — Linked vs Array-Based

Do not assume one implementation is universally faster. Choose based on the actual access pattern:

- **Array-backed (`ArrayList`, `ArrayDeque`):** O(1) indexed access, better cache locality, lower per-element memory overhead. Cost: O(n) insertion/removal in the middle (array shift), and resizing when capacity is exceeded (amortized O(1) add at end).
- **Linked (`LinkedList`):** O(1) insert/remove at a known position (via iterator or list index for `LinkedList`'s positional access is O(n) — find the node first, then splice), no array resizing, but higher per-element memory (node object + prev/next references) and poor cache locality.
- **Use `ArrayList` when:** index lookups dominate, or most mutations are at the end.
- **Use `LinkedList` when:** you have many insertions/removals at positions obtained via a live iterator (not by index), and the overhead of shifting array elements would dominate.
- **Use `ArrayDeque` when:** you need a double-ended queue with fast end operations and want array-backed performance; prefer over `LinkedList` for queue/stack use cases unless you need a deque that is also a `List`.

## Defensive Copying and Shared References

Accidentally mutating a shared collection reference is a common source of bugs, especially when a method returns an internal collection or a caller reuses a reference across threads.

- **Defensive copy:** When accepting a collection from a caller, make a copy (`new ArrayList<>(incoming)`) if you need to mutate it internally without affecting the caller.
- **Unmodifiable wrapper:** When returning a collection that callers should not modify, return `Collections.unmodifiableList(...)` (or `Set`/`Map`). Note: this wraps a live backing collection — if that backing collection is mutated elsewhere, the "unmodifiable" view reflects the changes.
- **Immutable factory collections (`List.of`/`Set.of`/`Map.of`):** Preferred for small, truly constant data because they are independently immutable, not just wrappers.
- **Concurrent access:** If multiple threads will access the same collection, use a concurrent implementation (`ConcurrentHashMap`, `CopyOnWriteArrayList`, `BlockingQueue`) or external synchronisation — do not rely on `Collections.synchronized*` wrappers as the sole protection for compound actions (check-then-act, iterate-and-remove).

> **Exam tip:** `ArrayList` gives O(1) indexed access but O(n) insert/remove in the middle;
> `LinkedList` gives O(1) insert/remove at known positions (when the node is already located) but O(n)
> indexed access. Choose based on whether the workload is index-lookup-heavy or mutation-heavy.
> For queue and deque use cases, prefer `ArrayDeque` over `LinkedList` — it has lower memory overhead
> and better cache locality.

> **Exam tip:** `StringBuilder` is not thread-safe; `StringBuffer` is the synchronised
> equivalent. Choose `StringBuilder` unless multiple threads mutate the same buffer. The same
> synchronisation trade-off applies to collections: prefer single-threaded collections unless
> concurrent access is required, then choose a purpose-built concurrent implementation rather than
> a synchronised wrapper.
