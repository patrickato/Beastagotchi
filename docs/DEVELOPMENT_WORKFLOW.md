# Development Workflow

## Principle

Develop in meaningful, testable increments. Automate as much validation as possible before asking a physical-device tester to perform repetitive checks.

## Typical change cycle

1. Record/confirm the requirement in an issue, roadmap or continuity ledger.
2. Implement on a feature/fix branch.
3. Add/update source tests and reference audits.
4. Run source/CI validation.
5. Generate off-screen renders or test artifacts for visual changes.
6. If the change touches real collectors/services, run target Pi off-screen validation.
7. If the user-facing experience changed meaningfully, schedule one physical visual/interaction gate.
8. Record the outcome in a validation report/checkpoint.
9. Merge only with rollback/recovery implications understood.

## Continuity discipline

The completion matrix and continuity ledger are anti-forgetting tools. Do not delete a planned item simply because development moved to a different subsystem. Mark it deferred/reserved/rejected with a reason.

## Heat/resource discipline

Before reducing visible functionality, find unnecessary work:

- duplicated polling;
- hidden-page rendering;
- inactive services still looping;
- unnecessary framebuffer writes;
- expensive effects that can cache static layers;
- collectors running faster than the underlying fact changes;
- duplicate decoding/transform work across UIs.

Use Resource Governor for genuine pressure/recovery, not as the normal solution to inefficient code.
