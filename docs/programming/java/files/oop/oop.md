# OOP

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
