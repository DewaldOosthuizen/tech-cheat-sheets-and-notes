# COLLECTIONS

```mermaid
--8<-- "programming/diagrams/java/collection-selection-decision-flow.mmd"
```

> **Exam tip:** `ArrayList` gives O(1) indexed access but O(n) insert/remove in the middle;
> `LinkedList` gives O(1) insert/remove at known positions but O(n) indexed access. Choose based
> on whether the workload is index-lookup-heavy or mutation-heavy.
