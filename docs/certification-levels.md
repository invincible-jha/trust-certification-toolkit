# AumOS Certification Levels

All criteria on this page are the complete, publicly documented requirements for the AumOS
Certified badge program. There are no hidden thresholds or additional private checks.

## How levels are determined

A certification level is awarded when **both** of the following are true:

1. The overall pass rate across all protocols that were run meets or exceeds the minimum
   threshold for that level.
2. Each protocol required at that level was run and passed at least one MUST-level check.

The highest level whose criteria are fully satisfied is awarded. All checks are run locally
on the implementer's own machine — no data is sent to any external service.

---

## Bronze

| Criterion | Value |
|-----------|-------|
| Minimum overall pass rate | 60% |
| Required protocols | ATP |
| Badge color | #CD7F32 |

The Bronze level confirms that the core trust assignment and enforcement model is in place.
An implementation must satisfy ATP conformance — that agents are assigned explicit trust
levels, that those levels are enforced at decision points, and that level changes require
owner authorization.

**Required protocol: ATP (Agent Trust Protocol)**

- Agents can be assigned a trust level.
- Trust level is enforced when an agent requests a privileged operation.
- Trust level changes require explicit owner authorization.
- Structured denial responses are returned when trust is insufficient.

---

## Silver

| Criterion | Value |
|-----------|-------|
| Minimum overall pass rate | 75% |
| Required protocols | ATP, AEAP, AOAP |
| Badge color | #C0C0C0 |

Silver adds economic accountability and observability on top of the Bronze trust model.

**Required protocols: ATP + AEAP + AOAP**

ATP requirements are as above, plus:

**AEAP (Agent Economic Action Protocol)**

- A static spend limit is enforced per agent per period.
- Spend requests that exceed the static limit are denied.
- Spend events are recorded with a unique identifier.
- The remaining budget can be queried at any time.

**AOAP (Agent Observability and Accountability Protocol)**

- Audit entries can be appended with a unique entry identifier.
- The audit log can be exported as JSON.
- Audit entries can be queried by event type.

---

## Gold

| Criterion | Value |
|-----------|-------|
| Minimum overall pass rate | 90% |
| Required protocols | ATP, AIP, AEAP, AMGP, AOAP |
| Badge color | #FFD700 |

Gold adds identity management and memory governance to the Silver requirements.

**Required protocols: ATP + AIP + AEAP + AMGP + AOAP**

ATP, AEAP, and AOAP requirements are as above, plus:

**AIP (Agent Identity Protocol)**

- New agent identities can be registered with a public key.
- Registered identities can be looked up by agent identifier.
- Credentials are validated before identity claims are granted.
- Identities can be revoked by an authorized owner.

**AMGP (Agent Memory Governance Protocol)**

- Memory records can be written with an explicit retention policy.
- Memory records can be queried by retention policy.
- Memory records can be deleted on owner request.

---

## Platinum

| Criterion | Value |
|-----------|-------|
| Minimum overall pass rate | 95% |
| Required protocols | ATP, AIP, ASP, AEAP, AMGP, AOAP, ALCP |
| Badge color | #E5E4E2 |

Platinum covers all seven AumOS governance protocols at near-complete conformance.

**Required protocols: ATP + AIP + ASP + AEAP + AMGP + AOAP + ALCP**

All Gold requirements apply, plus:

**ASP (Agent Scope Protocol)**

- Declared capability scopes are enforced at runtime.
- Out-of-scope operations are denied with a structured response.
- Scope declarations can be queried.

**ALCP (Agent Lifecycle Protocol)**

- Agents can be created and initialized with a defined scope.
- Agents can be suspended without data loss.
- Agents can be terminated with an audit record.

---

## Protocol identifiers reference

| ID | Full name |
|----|-----------|
| `atp` | Agent Trust Protocol |
| `aip` | Agent Identity Protocol |
| `asp` | Agent Scope Protocol |
| `aeap` | Agent Economic Action Protocol |
| `amgp` | Agent Memory Governance Protocol |
| `aoap` | Agent Observability and Accountability Protocol |
| `alcp` | Agent Lifecycle Protocol |
