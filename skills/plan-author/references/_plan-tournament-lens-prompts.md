# plan-author Lens Prompts

Lens prompts prepend to the standard plan-author prompt. Each lens makes one optimization axis explicit and adds constraints that bias the candidate plan in that direction.

A candidate that abandons its lens (e.g., security-first plan that omits threat modeling) is **disqualified** by the red-teamer before scoring.

---

## security-first

```
You are writing a plan optimized for SECURITY. Every decision must explicitly consider:

- Threat surface: which inputs cross trust boundaries? Who can call this code?
- Authentication: where does the request prove who it is?
- Authorization: where does the request prove it's allowed?
- Input validation: every input has an explicit schema/validator named.
- Secrets: no hard-coded secrets; all via env or secrets manager.
- Least-privilege: services and tokens have minimum required scope.

Hard constraints:
- Authn happens BEFORE any business logic.
- Authz happens BEFORE any data access.
- No input is trusted without validation.
- Secrets are referenced by name, never written into plan files.
- Threat-model section is mandatory in EVERY phase that touches a trust boundary.

If you cannot satisfy a constraint, document the gap explicitly. Do not skip it.
```

---

## performance-first

```
You are writing a plan optimized for PERFORMANCE. Every decision must explicitly consider:

- Latency: p50, p95, p99 targets stated per endpoint/operation.
- Throughput: requests/sec target stated per surface.
- Caching: where, with what TTL, with what invalidation rule.
- Database access: N+1 queries explicitly ruled out per phase.
- Batching: opportunities for bulk operations identified.
- Async/streaming: where appropriate, used; where inappropriate, avoided.

Hard constraints:
- Every read-heavy path names its cache layer (or explains why none).
- Every write path names its throughput envelope.
- p95 latency target stated as a Success Criterion (Check command).
- No "we'll optimize later" — perf characteristics designed in.

Profile-before-conclude: if a perf assumption is in the plan, name the measurement that will verify it.
```

---

## simplicity-first

```
You are writing a plan optimized for SIMPLICITY. The fewest moving parts wins.

Decision rules:
- New infrastructure: justify against the existing stack. Default: reuse.
- New language/framework: justify against what's already in the repo. Default: extend.
- New process: justify against doing nothing. Default: don't.
- Number of phases: ≤3 if at all possible.
- Number of files touched per phase: ≤5.

Hard constraints:
- No new database without explicit per-phase justification.
- No new queue without explicit per-phase justification.
- No new microservice unless monolith path is documented as worse.
- Plan length: ≤200 lines total across all phase files.

Be ruthless. "We might need X later" is not a justification. YAGNI rules.
```

---

## scalability-first

```
You are writing a plan optimized for SCALABILITY (10x growth headroom).

Decision rules:
- Services stateless wherever possible.
- Long operations behind queues (durable, retry-safe).
- Horizontal scaling path stated per service.
- Database sharding/partitioning plan stated if growth predicts hot keys.
- Cache layer separable from compute.

Hard constraints:
- Every stateful component has a documented scale-out plan.
- No long-running HTTP request handlers (>5s) — push to queue.
- No global locks — pessimistic locking is documented as last-resort with rollback plan.

Headroom envelope: design for 10× current load. Document the breaking point at 100× so future you knows what to revisit.
```

---

## accessibility-first

```
You are writing a plan optimized for ACCESSIBILITY (WCAG 2.2 AA + assistive tech).

Decision rules:
- Semantic HTML over div-soup.
- Every interactive element keyboard-reachable.
- Every image/icon has alt text or aria-label.
- Color contrast ratio ≥ 4.5:1 for text.
- Focus management explicit (modal open → focus moved in; close → focus restored).
- Live regions for dynamic content (aria-live).
- Touch targets ≥ 44×44pt.

Hard constraints:
- Validation gate includes accessibility audit via visual-inspection skill or axe-core.
- Every phase touching UI has a "WCAG criteria covered" list.

Accessibility is not a polish task. It is the architecture.
```

---

## cost-first

```
You are writing a plan optimized for COST (cloud bill minimization).

Decision rules:
- Serverless over always-on where the duty cycle is < 30%.
- Free-tier services exploited where they fit.
- Logs/metrics retention bounded explicitly (90 days max default).
- Egress minimized (CDN where applicable).
- Storage tier matches access pattern (cold → archive tier).

Hard constraints:
- Every infrastructure addition has an estimated monthly cost stated.
- Total monthly cost envelope stated for the plan as a whole.
- Idle costs minimized (autoscale-to-zero where possible).

Pricing pages are NOT optional reading. Cite the pricing page version + date used.
```

---

## Adding a new lens

To add a new lens (e.g., `dx-first`, `compliance-first`, `latency-first`):

1. Define the optimization axis in one sentence.
2. Enumerate 4-6 decision rules.
3. Enumerate 3-5 hard constraints.
4. Add a row to the lens table in `plan-author/SKILL.md`.
5. Append the lens prompt body to this file.
