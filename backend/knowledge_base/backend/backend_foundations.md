# Backend Engineering Foundations

Reliable APIs define explicit contracts, validate inputs at the boundary, use stable error shapes, and keep transport concerns separate from business logic. Idempotency keys prevent duplicated state changes when clients retry requests. Authentication establishes identity while authorization determines whether that identity may perform an action.

Relational data modeling uses keys and constraints to preserve invariants. Transactions group changes that must succeed or fail together. Indexes accelerate common predicates but add write and storage cost. Query plans should be measured with representative workloads before indexes are added.

Scalable systems isolate slow work with queues and background workers while exposing progress to the caller. Caches reduce latency but require explicit invalidation and consistency decisions. Observability connects structured logs, metrics, and traces with request identifiers so failures can be followed across service boundaries.

Distributed systems must account for partial failure, duplicated messages, delayed messages, and network partitions. Timeouts, bounded retries with jitter, circuit breakers, and dead-letter handling are operational controls, not substitutes for correct domain invariants.
