# Design patterns

One test for every pattern here: when the next change arrives, does it land in a single place, and does a test show it still works? Use a pattern because its problem is in front of you. Never use one to look sophisticated.

## 1. Start here: where will the next change go?

The examples come from a booking app.

1. **New rule: a customer may hold at most 5 open bookings.**
   - Goes in one domain constant plus one check in the use case.
   - Pattern: domain model with a service layer.
   - Proof: domain unit test, and an API test that the 6th booking is refused.
2. **New SMS, email or payment vendor.**
   - Goes in a fresh adapter for the port that exists, plus one line that registers it.
   - Pattern: strategy and adapter (ports and adapters).
   - Proof: test the adapter against recorded vendor replies. Use-case tests carry on with the fake.
3. **New failure callers should expect, e.g. "slot already taken".**
   - Goes in a single error case, a code for it in the contract, and a new branch on the client's closed result type.
   - Pattern: result object. Exhaustive matching shows every switch that needs the branch.
   - Proof: API test for the error, client test for the branch.
4. **New screen state.**
   - Goes in one extra case on the closed state type.
   - Pattern: state, written as closed types.
   - Proof: a UI test per state.
5. **A screen stops using the fake backend and uses the real one.**
   - Goes in the repository binding alone.
   - Pattern: repository with dependency injection.
   - Proof: the UI tests you already have, rerun over a fake HTTP layer.
6. **A step every request needs: auth header, timing, decompression.**
   - Goes in one middleware or interceptor.
   - Pattern: chain of responsibility, or decorator.
   - Proof: one test that sends a request through the full pipeline.
7. **Another part must react when a booking changes.**
   - Goes in a new subscriber to the event that exists. The sender is not edited.
   - Pattern: observer.
   - Proof: a test that the subscriber hears about the change.
8. **New field on the wire.**
   - Goes in the contract and one mapper per side. A rename or removal breaks callers, so it needs a new version.
   - Pattern: adapter at the boundary; one source of truth.
   - Proof: regenerated client compiles, mapping test passes, deploy check passes.

If a change forces edits across unrelated files, a pattern is missing or misused. Say that in the review.

## 2. Patterns for whole-system structure

**Always**
- **Layers and the dependency rule.** Edge, use case, domain. Outer layers depend on inner ones.
- **One source of truth, one-way data flow.** Whenever data appears in more than one place.

**Use when the situation fits (and the condition that rules it out)**
- **Ports and adapters.** Use for whatever sits outside the process and could be replaced or faked: vendors, the OS, other services, the clock. Do not use it between two pieces of your own code in one layer.
- **Service layer.** Use when a use case has to coordinate rules, data, a transaction and side effects. A pure rule belongs on the entity. A lone read needs only a projection.
- **Rich domain model.** Use when invariants must hold whoever changes the data. Plain read models do not need it.
- **Repository plus unit of work.** Use for persistence behind a collection-like API with one commit per use case. Do not wrap an ORM that is already a repository: you would hide projections, bulk updates and locks.
- **Read/write split (light CQRS).** Use when reads need shapes the entities do not have, and project straight into read models. Do not build separate read databases or message pipelines until scale forces it.
- **Presentation model (MVVM).** Use for any screen with actions or more than one data source. A static read-only view can skip it.
- **Dependency injection.** Use for all dependencies handed to services, adapters, repositories and view models. Value objects and pure functions need none.
- **Typed options validated on start.** Use for every config value. A constant that is really a business rule goes on the domain type instead.
- **Result object.** Use for failures the caller is expected to handle. Bugs and broken infrastructure should throw.
- **Idempotency key.** Use whenever a write can be retried by a client or job. Reads do not need one.
- **Transactional outbox.** Use when a side effect cannot be allowed to vanish in the gap between commit and send. A best-effort notice that the next refresh repairs does not need it.
- **Timeout, retry with backoff and jitter, circuit breaker.** Use on every call that leaves the process. Never retry a non-idempotent write that lacks a key. Never stack two retry layers on one path.
- **Feature flag.** Use when code ships before it is allowed on, and for staged rollouts. Not for permanent configuration, and not for a flag without a removal condition.
- **Optimistic UI.** Use when an action should feel instant and a rollback is possible. Not for safety-critical actions, which must show the real result.

### Outbox that works in practice

1. Insert the outbox row inside the transaction that makes the change.
2. Attempt delivery as soon as the commit succeeds.
3. Let a background dispatcher retry the leftovers. It takes rows under a lease (`SELECT ... FOR UPDATE SKIP LOCKED`, or your database's version), sends with no transaction open, then stores the outcome, guarded by that lease.
4. Add backoff, a give-up time chosen by what the user would see, and a backlog metric.
5. Give alert-type messages an idempotency key too. Then two overlapping leases still send once.

## 3. Object-level patterns

### Making objects

- **Factory method.** For construction that must enforce invariants or stamp an id or time. Skip it for a bare record with no rules.
- **Builder.** For many optional parts assembled step by step, mostly inside frameworks. In your own code with few parameters, use named parameters.
- **Abstract factory.** For families of objects that change together. You will almost never need it.
- **Singleton.** One shared instance, handed out only by the DI container. A static mutable global is not a singleton. Tests cannot swap it.

### Shaping and wrapping objects

- **Adapter.** When a vendor's shape differs from your port. For your own types, rename instead.
- **Facade.** One simple door into a subsystem; an application service is one. Stop when unrelated methods begin to collect in it.
- **Decorator.** Add timing, metrics or caching around a port while leaving implementations alone. Do not use it for a second retry layer: a path has one retry owner.
- **Composite.** Treat a tree uniformly, as with UI trees.
- **Proxy.** Control access behind the same interface. Do not let it swallow failures the caller must see.

### Behaviour

- **Strategy.** Interchangeable algorithms or vendors picked by config. With two or three fixed cases that never vary, a switch expression is enough.
- **Observer.** Several parties respond to one change, and the source knows none of them. A single fixed reaction is just a call.
- **Command.** Work you need to queue, retry or undo as a value, such as a job. A plain synchronous call needs nothing.
- **Chain of responsibility.** Ordered steps that can stop the flow or pass it along, such as middleware. Business rules are not steps: keep them in the use case where they read in order.
- **State.** Behaviour that changes with a fixed set of states. Use closed types and exhaustive matching.
- **Template method.** Avoid. It is inheritance for reuse. Inject the part that varies.
- **Visitor.** Not needed. Pattern matching over closed types covers it.

## 4. Smells that fail a review

Each line reads: smell, then the damage, then the fix.

- **God class, a "Manager", or a rule-free `Utils` file.** All changes pass through it and no one owns it. Give each unit one job, and give shared code rules plus a test.
- **Logic in the edge.** Nobody can reuse or unit-test it, and edges diverge. Move it to a use case or a view model.
- **Anaemic domain with rules spread over services.** The same check ends up pasted five times. Put the rules on the entity.
- **Generic repository over an ORM.** It buries projections, bulk updates and locks. Use the ORM's unit of work and its query extensions.
- **An interface for every class.** You get twice the files and no real boundary. Put interfaces only where a boundary exists.
- **Service locator in business code.** Dependencies cannot be seen. Inject through the constructor.
- **Static mutable state.** Tests leak into each other and nothing can be overridden. Use a singleton from the DI container.
- **Inheritance to share code.** The base class turns brittle. Compose instead.
- **Primitive obsession.** Ids and phone numbers are loose strings, so swapping them still compiles. Use value objects or typed ids wherever a swap is plausible.
- **Boolean flag arguments.** Call sites read badly and the code paths double. Write two named methods or take an options object.
- **Catch everything and carry on.** Failures vanish, and on safety paths alerts get lost. Catch a typed error and recover in plain view, or rethrow.
- **Speculative generality.** You build abstractions for needs that never arrive. Build for today; clean layers make a second case cheap.
- **A feature's own copy of a generic piece.** The following feature will copy it again. Design the generic port up front.
