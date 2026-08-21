# PERSISTENCE

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
