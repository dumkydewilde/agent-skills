---
name: principles
description: "The twenty-one engineering principles dstack works from, one rule each, grouped as core, architecture, verification, delegation, and meta. Use at the start of any multi-step task, when dstack-mode's todolist says to read the principles, or when another skill names a principle by bolded name and you need its full rule."
---

# Principles

Twenty-one rules, one per file under `references/`. This page is the index. Each entry names when the principle applies and states its rule in one line.

**Read the leaf file in full for any principle you actually apply.** The one-line rule here is a pointer, not the principle. Citing a principle you did not read is the failure mode this skill exists to prevent.

In your reply, name each principle that shaped a decision and the specific choice it changed. A citation with no decision behind it means you skipped the leaf; it must trace to a real choice the leaf's rule drove.

## Core

- **Laziness Protocol** ([`references/laziness-protocol.md`](references/laziness-protocol.md)). Refactoring, sizing a diff, or tempted to add abstractions, layers, or signal threading. Bias to deletion and the smallest change that solves the problem.
- **Foundational Thinking** ([`references/foundational-thinking.md`](references/foundational-thinking.md)). Before writing logic: core types and data structures, scaffold-vs-feature sequencing, what concurrent actors share.
- **Redesign from First Principles** ([`references/redesign-from-first-principles.md`](references/redesign-from-first-principles.md)). Integrating a new requirement into an existing design. Redesign as if it had been foundational from day one.
- **Subtract Before You Add** ([`references/subtract-before-you-add.md`](references/subtract-before-you-add.md)). Sequencing an addition, refactor, or rewrite. Remove dead weight first, then build on the simpler base.
- **Minimize Reader Load** ([`references/minimize-reader-load.md`](references/minimize-reader-load.md)). Reviewing or shaping code that is hard to trace. Count layers and hidden state, collapse one-caller wrappers, shrink mutable scope.
- **Outcome-Oriented Execution** ([`references/outcome-oriented-execution.md`](references/outcome-oriented-execution.md)). Planned rewrites and migrations with explicit phase boundaries. Converge on the target architecture, do not preserve throwaway compatibility states.
- **Experience First** ([`references/experience-first.md`](references/experience-first.md)). Product, UX, or feature-scope tradeoffs. Choose user delight over implementation convenience.
- **Exhaust the Design Space** ([`references/exhaust-the-design-space.md`](references/exhaust-the-design-space.md)). A novel interaction or architectural decision with no precedent. Build 2-3 competing prototypes and compare before committing.
- **Build the Lever** ([`references/build-the-lever.md`](references/build-the-lever.md)). Any non-trivial work. Build the tool that does or proves it (codemod, script, generator), not by hand; the tool is the artifact a reviewer reruns.

## Architecture

- **Model the Domain** ([`references/model-the-domain.md`](references/model-the-domain.md)). Writing stateful logic, or code that branches a lot or repeats a shape assumption across files. Encode the domain in a structure instead of scattered conditionals.
- **Boundary Discipline** ([`references/boundary-discipline.md`](references/boundary-discipline.md)). Wiring validation, error handling, or framework adapters. Guards at system boundaries, trust internal types, keep business logic pure.
- **Type System Discipline** ([`references/type-system-discipline.md`](references/type-system-discipline.md)). Designing types or a signature in any typed language. Make illegal states unrepresentable, brand primitives, parse external data at boundaries.
- **Make Operations Idempotent** ([`references/make-operations-idempotent.md`](references/make-operations-idempotent.md)). Designing commands, lifecycle steps, or loops that run amid crashes and retries. Converge to the same end state.
- **Migrate Callers Then Delete Legacy APIs** ([`references/migrate-callers-then-delete-legacy-apis.md`](references/migrate-callers-then-delete-legacy-apis.md)). Introducing a new internal API while old callers exist. Migrate and delete in one wave.
- **Separate Before Serializing Shared State** ([`references/separate-before-serializing-shared-state.md`](references/separate-before-serializing-shared-state.md)). Concurrent actors might write the same file, branch, key, or object. Eliminate the sharing first.

## Verification

- **Prove It Works** ([`references/prove-it-works.md`](references/prove-it-works.md)). After a task, before declaring done. Verify against the real artifact, not a proxy or "it compiles".
- **Fix Root Causes** ([`references/fix-root-causes.md`](references/fix-root-causes.md)). Debugging. Trace each symptom to its root cause, reproduce first, ask why until you reach it.
- **Sequence Work into Verifiable Units** ([`references/sequence-verifiable-units.md`](references/sequence-verifiable-units.md)). Multi-step work and how you stack commits and PRs. Break work into small units that each end in a check, verify each before the next.

## Delegation

- **Guard the Context Window** ([`references/guard-the-context-window.md`](references/guard-the-context-window.md)). Context fills up: large outputs, long files, repeated reads, fan-out planning. Route bulk to subagents, keep summaries in the main thread.
- **Never Block on the Human** ([`references/never-block-on-the-human.md`](references/never-block-on-the-human.md)). Tempted to ask "should I do X?" on reversible work. Proceed, present the result, let the human course-correct.

## Meta

- **Encode Lessons in Structure** ([`references/encode-lessons-in-structure.md`](references/encode-lessons-in-structure.md)). You catch yourself writing the same instruction a second time. Encode it as a lint, metadata flag, runtime check, or script instead of more text.
