# PERSISTENCE

Quick-reference cheat sheet for Java persistence — JDBC, JPA, ORM trade-offs, and the production concerns that most often cause data-layer defects. Targets Java 21 and Spring Boot 3.x.

## JDBC

|| Aspect | Key Feature | When to Prefer |
|| --- | --- | --- |
|| **Low-level control** | Full control over SQL, connections, statements, and result sets | When you need precise query control, bulk operations, or non-standard SQL |
|| **Resource management** | Connections, statements, and result sets must be closed; use try-with-resources | Always — leaking connections or statements is a common defect |
|| **Batching** | `Statement.addBatch()` / `PreparedStatement.addBatch()` with `executeBatch()` | When inserting or updating large numbers of rows and you want fewer round-trips |
|| **Transaction control** | `Connection.setAutoCommit(false)`, `commit()`, `rollback()` | When you need explicit transaction boundaries outside a framework |
|| **ResultSet handling** | Iterate with `ResultSet.next()`; map columns manually or with a row mapper | When you want full control over mapping and lazy fetching |

> **Exam tip:** JDBC gives you the most control but the most boilerplate. Use it when the ORM abstraction leaks, when batch processing matters, or when you need precise SQL. Always close resources with try-with-resources.

### JDBC Batching Example

```java
String sql = "INSERT INTO audit_log (user_id, action, ts) VALUES (?, ?, ?)";
try (Connection conn = dataSource.getConnection();
     PreparedStatement ps = conn.prepareStatement(sql)) {
    conn.setAutoCommit(false);
    for (var event : events) {
        ps.setLong(1, event.userId());
        ps.setString(2, event.action());
        ps.setTimestamp(3, Timestamp.from(event.ts()));
        ps.addBatch();
    }
    ps.executeBatch();
    conn.commit();
}
```

Batching reduces round-trips but does not remove transaction management. A failed batch should trigger a rollback of the entire batch — do not commit partial results.

## JPA

|| Aspect | Key Feature | When to Prefer |
|| --- | --- | --- |
|| **Entity mapping** | Map Java classes to tables with annotations or XML; managed by an `EntityManager` | When you want object-relational mapping with less boilerplate |
|| **Persistence context** | Entities are managed in a persistence context; changes are flushed on commit or explicit flush | When you want dirty checking and lifecycle management |
|| **JPQL** | Object-oriented query language; operates on entities and their properties, not tables and columns | When queries are simple to moderate and you want type-safe, refactorable queries |
|| **Criteria API** | Type-safe, programmatic query construction | When queries are dynamic and built at runtime from user input or conditions |
|| **Lazy vs eager loading** | Relationships can be fetched lazily (on access) or eagerly (with the parent) | Choose deliberately — wrong defaults cause performance and consistency problems |
|| **N+1 problem** | Fetching a collection of entities and then lazily loading a related collection per entity leads to one query per row | Avoid by using `JOIN FETCH`, entity graphs, or bounded queries with pagination |

> **Exam tip:** JPA reduces boilerplate for CRUD and simple queries, but the convenience comes with operational semantics — persistence context, flushing, lazy loading, and transaction boundaries. Misunderstanding these is a common source of production defects.

### Entity Example

```java
@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id")
    private Customer customer;

    @OneToMany(mappedBy = "order", fetch = FetchType.LAZY, cascade = CascadeType.PERSIST)
    private List<OrderLine> lines = new ArrayList<>();
}
```

Prefer `FetchType.LAZY` for relationships by default. Eager loading is occasionally appropriate for truly mandatory single-valued relationships, but it is a common source of unexpected queries and memory pressure.

## Transactions

|| Propagation | Behaviour | When to Prefer |
|| --- | --- | --- |
|| `REQUIRED` | Join an existing transaction or create a new one | The most common default; use for operations that must run inside a transaction |
|| `REQUIRES_NEW` | Suspend the current transaction and create a new one; the new transaction commits or rolls back independently | When a sub-operation must be committed independently of the outer transaction (use with caution — can break atomicity guarantees) |
|| `MANDATORY` | Require an existing transaction; throw if none exists | When the method must never run outside a transaction boundary |
|| `NEVER` | Throw if a transaction exists | Rare; used to enforce that a method runs outside a transaction |

|| Isolation | Guarantee | Watch-Out |
|| --- | --- | --- |
|| `READ_COMMITTED` | Non-repeatable reads and phantom reads are possible; dirty reads are prevented | The most common default; sufficient for many workloads |
|| `REPEATABLE_READ` | Non-repeatable reads are prevented; phantom reads may still occur | Stronger than read-committed; not a guarantee against all concurrency anomalies |
|| `SERIALIZABLE` | Full serialisable isolation | Strongest guarantee; can cause contention and deadlocks — use when correctness demands it, not by default |

> **Exam tip:** Read-only transactions are a hint to the provider and can improve performance by avoiding dirty checking and flush operations. Mark transactions as read-only when the method does not modify persistent state.

### Read-Only Transaction Example

```java
@Transactional(readOnly = true)
public Optional<Order> findOrderById(Long id) {
    return orderRepository.findById(id);
}
```

Read-only is a hint, not an absolute guarantee. The persistence provider may still issue queries; the benefit is avoiding unnecessary flush and dirty-checking overhead.

## Fetch Plans

|| Technique | What It Does | When to Prefer |
|| --- | --- | --- |
|| `JOIN FETCH` | Fetches the related association in the same query as the parent | When you know you need the related data and want to avoid N+1 queries |
|| Entity graphs | Declare which attributes and associations to fetch for a query or find operation | When fetch plans vary by use case and you want to avoid hardcoding joins in JPQL |
|| `@BatchSize` | Fetches a lazy collection in batches rather than one query per parent | When lazy collections are accessed but you want to limit the query count |
|| `Lazy` loading (default for collections) | The association is loaded when first accessed | Default; be deliberate about when it is appropriate |

### N+1 Detection and Remediation

**Symptom:** Loading a list of parent entities and then accessing a lazy collection on each parent triggers one additional query per parent.

**Detection:** Enable SQL logging during development and look for a pattern where a single query returns N parents followed by N queries for the related collection. Profiling tools and slow-query logs can also expose the pattern.

**Remediation option 1 — `JOIN FETCH`:**

```java
@Query("SELECT o FROM Order o JOIN FETCH o.lines WHERE o.customer.id = :customerId")
List<Order> findOrdersWithLinesByCustomerId(@Param("customerId") Long customerId);
```

Use `JOIN FETCH` when you know the related data is needed. Be aware that `JOIN FETCH` can return duplicate parent rows when multiple collections are fetched in the same query; use `DISTINCT` in JPQL or a `Set` in Java when needed.

**Remediation option 2 — paginated, bounded queries:**

```java
@Query("SELECT o FROM Order o WHERE o.customer.id = :customerId")
Page<Order> findOrdersByCustomerId(@Param("customerId") Long customerId, Pageable pageable);
```

Pagination bounds the result set and limits the cost of fetching and rendering collections. Combine pagination with `JOIN FETCH` only when the fetched association does not explode the row count; otherwise fetch the parent page first and load associations selectively.

**Remediation option 3 — entity graphs or batch fetching:**

Use entity graphs when different use cases need different fetch plans. Use `@BatchSize` when lazy collections are accessed but you want to reduce the query count without forcing a join.

## Pagination

|| Approach | Characteristics | When to Prefer |
|| --- | --- | --- |
|| Offset-based (`LIMIT / OFFSET` or `Pageable`) | Simple to implement; skips rows, so deep pages become expensive | Small to moderate result sets; user-facing lists with limited paging depth |
|| Keyset / cursor-based | Uses a stable ordering and a cursor (last seen value) to fetch the next page; does not skip rows | Large result sets, deep pagination, or infinite scroll where performance matters |

> **Exam tip:** Offset-based pagination is fine for small pages, but deep offset pagination becomes expensive because the database still has to scan and skip rows. For large data sets or deep pages, prefer keyset pagination with a stable, indexed ordering.

### Offset-Based Pagination Example

```java
@Query("SELECT o FROM Order o WHERE o.status = :status ORDER BY o.createdTs DESC")
Page<Order> findOrdersByStatus(@Param("status") String status, Pageable pageable);
```

### Keyset Pagination Concept

Keyset pagination uses the last seen value of an ordered, indexed column as the cursor for the next page:

```java
@Query("SELECT o FROM Order o WHERE o.createdTs < :cursor ORDER BY o.createdTs DESC")
List<Order> findOrdersBeforeCursor(@Param("cursor") LocalDateTime cursor, Pageable pageable);
```

Keyset pagination avoids the cost of skipping rows and scales better for deep pages, but it requires a stable, indexed ordering and does not support random jumps to an arbitrary page number.

## Concurrency and Locking

|| Strategy | What It Does | When to Prefer |
|| --- | --- | --- |
|| Optimistic locking (`@Version`) | Detects concurrent modifications by comparing a version column; throws on stale write | When conflicts are rare and you want to avoid holding database locks |
|| Pessimistic locking (`SELECT ... FOR UPDATE`) | Locks rows in the database for the duration of the transaction | When conflicts are expected and you need to prevent lost updates or enforce ordering |
|| Read-only transactions | Avoids dirty checking and flush overhead; does not add locks | When the operation only reads data |

### Optimistic Locking Example

```java
@Entity
public class Account {
    @Id
    private Long id;

    @Version
    private Long version;

    private BigDecimal balance;
}
```

When two transactions try to update the same entity, the second one fails with an optimistic lock exception because the version column no longer matches. Handle the exception by retrying, refreshing, or surfacing a conflict to the caller — do not silently swallow it.

### Pessimistic Locking Concept

Use pessimistic locking when you must prevent concurrent modifications for the duration of a transaction, for example when decrementing a shared inventory count or processing a queue item:

```java
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("SELECT a FROM Account a WHERE a.id = :id")
Optional<Account> findByIdForUpdate(@Param("id") Long id);
```

Pessimistic locks are held until the transaction completes, so keep the locked transaction short and avoid user interaction inside it.

## Batch Processing

|| Technique | When to Prefer |
|| --- | --- |
|| JDBC batching (`addBatch` / `executeBatch`) | Large insert/update workloads where you want to reduce round-trips and control SQL directly |
|| JPA stateless sessions or bulk operations | When you need to process large numbers of entities without the overhead of a full persistence context |
|| Spring Batch | When the workload needs chunk-oriented processing, retry, skip, and job monitoring |

> **Exam tip:** JPA's `persist` and `merge` are convenient for individual entities, but processing thousands of entities through a managed persistence context can cause memory pressure. For batch workloads, consider JDBC batching, stateless sessions, or Spring Batch rather than persisting every entity through the standard ORM lifecycle.

## ORM Trade-Offs and When to Drop Down

|| Concern | ORM (JPA) | Native SQL / JDBC |
|| --- | --- | --- |
|| CRUD convenience | High — entities, repositories, and derived queries reduce boilerplate | Low — you write SQL and map results manually |
|| Complex queries | JPQL and Criteria can become awkward for very complex or highly optimised queries | Full SQL control; use when the ORM abstraction leaks or performance demands it |
|| Batch processing | Can cause memory pressure through the persistence context | Better control over memory and round-trips |
|| Refactorability | JPQL is more refactorable than raw SQL when entities and names are stable | Raw SQL is coupled to schema names and can break on rename |
|| Predictable SQL | The provider generates SQL; you do not always control the exact plan | You write the SQL, so you know what is sent to the database |

> **Exam tip:** Start with JPA for CRUD and straightforward queries. Drop down to native SQL or JDBC when you need precise query control, batch performance, or when the ORM abstraction gets in the way of a clear, efficient query plan. Do not default to one approach for every workload.

## open-in-view

The `open-in-view` feature (often enabled by default in some Spring configurations) keeps the persistence context and database connection open for the duration of the request, including during view rendering. This can make lazy loading appear to work in views, but it hides the fact that the view layer is triggering database queries and can keep connections open longer than necessary.

Treat `open-in-view` as a trade-off, not a default architectural solution. Prefer explicit fetching and bounded queries so that the service layer returns exactly what the view needs, without relying on lazy loading triggered from the view layer. If you disable `open-in-view`, ensure that your service layer fetches all required data before returning, and use pagination and `JOIN FETCH` where appropriate.
