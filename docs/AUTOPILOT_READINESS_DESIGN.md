# Autopilot Readiness Builder: Human-First Design

Updated: July 13, 2026

Status: Design proposal. Review is required before implementation.

## 1. What this system is for

A company may want to automate an office process before its source files,
decision rules, exceptions, permissions, and recovery procedures are clear.
Giving an AI system permission to act under those conditions can make a normal
case look successful while allowing unusual cases to fail silently.

The Autopilot Readiness Builder does not try to force every process into full
automation. It helps people understand the work, resolve what can be resolved,
and reach one of four honest conclusions:

1. the standard path is ready for automation;
2. it can become ready after specific gaps are resolved;
3. AI assistance is useful, but a human decision must remain;
4. the process should not be automated under the current conditions.

A decision not to automate is not a failed engagement. It prevents avoidable
harm and becomes a documented business result.

## 2. Who uses it

### Internal improvement teams

- They know which work is painful but do not know what must be defined first.
- They need to turn employee experience into reviewable operating rules.
- They want to test the process against historical data before production.

### Beginners offering automation as a service

- They need a reliable discovery path for a first client.
- They must avoid promising automation that cannot be operated safely.
- They need useful deliverables even when implementation is rejected.

### Employees who perform the work

- They can explain their work in ordinary language, not software terminology.
- They should not receive a large technical questionnaire.
- They need to understand why a question matters before answering it.

## 3. Human-first principles

### Ask one primary question at a time

The AI adapts the next question to the previous answer. Every question includes
plain-language reasoning, an example, and an honest "I do not know" path.

### Start with the employee's language

The first conversation does not use terms such as idempotency or compensation.
It asks:

- What tells you that this work should begin?
- What happens if the same file arrives twice?
- How do you know the result is complete?
- If the system makes a wrong change, can you undo it?
- Who do you ask when the case is unusual?

The system translates those answers into technical requirements later.

### AI proposes rules; people confirm them

The AI may extract a rule candidate from approved examples or policies. A
candidate never becomes executable policy until an authorized business owner
confirms it.

### Preserve unknowns

Missing information remains missing. The system records the responsible owner,
the next action, and the expected completion evidence instead of inventing an
answer.

### Explain refusals

The system must not stop with a vague statement such as "insufficient safety."
It gives a specific reason and path forward:

> The vendor activation process has no tested reversal procedure. Define and
> test vendor deactivation and payment hold procedures before unattended vendor
> activation can be considered.

## 4. The user journey

```text
Choose an objective
  -> Describe the current work
  -> Add source files and approved examples
  -> Let AI inspect the evidence
  -> Answer one missing question at a time
  -> Confirm decision rules and exceptions
  -> Run historical shadow tests
  -> Compare human and system outcomes
  -> Receive a readiness decision
  -> Remediate, remain assisted, stop, or prepare a controlled pilot
```

## 5. The first screen

The first screen asks what the person is trying to achieve:

- improve an internal process;
- propose automation to a client;
- move an existing assisted process toward unattended operation;
- assess feasibility without committing to implementation.

The system changes its language and deliverables to match that objective. It
does not ask the beginner to choose infrastructure or an orchestration engine.

## 6. Nine areas the AI investigates

### 6.1 Start condition

- What event starts the work?
- Can that event be detected reliably?
- Is the trigger a time, file arrival, form, or system status?
- Can the same request arrive more than once?

### 6.2 Inputs

- Which files are required or optional?
- Where are they stored?
- Which fields must exist?
- How are stale, duplicate, and incorrect files recognized?
- Do the files contain personal, confidential, or regulated information?

### 6.3 Outputs

- What does a correct finished result look like?
- Where is it stored?
- Which fields, sections, or filenames are mandatory?
- What proves the work is complete?
- Who relies on the result?

### 6.4 Decision rules

- Which decisions can be expressed through values, dates, and statuses?
- What is the order of priority?
- What is allowed, rejected, or escalated?
- Which choices currently depend on experience or judgment?
- Which rules come from law, contract, policy, or professional responsibility?

### 6.5 Exceptions

- What makes a case unusual?
- How are missing or conflicting facts handled?
- Which amount, volume, or deadline limits matter?
- Which cases involve complaints, safety, employment, legal, financial, or
  security concerns?
- Who owns an exception and how quickly must they respond?

### 6.6 External actions and permissions

- Which systems are read and which are changed?
- What is the smallest permission the automation needs?
- Is there a dedicated service identity?
- What action, amount, and volume limits apply?
- Which actions always stay outside automation?

### 6.7 Failure and recovery

- Which failures are temporary and safe to retry?
- Which failures must stop immediately?
- How many retries are allowed?
- Where is failed work quarantined?
- How is a completed action reversed or compensated?
- Which actions cannot be undone?
- Who owns the emergency stop?

### 6.8 Accountability and obligations

- Who owns the business process?
- Who owns the system and data?
- Do legal, finance, HR, security, or compliance specialists need to review it?
- How long must evidence and decisions be retained?
- How can an affected person request explanation or correction?

### 6.9 Business value

- How long does the work take today?
- How many cases occur each month?
- How often do mistakes and rework occur?
- What improvement is expected?
- What will implementation and maintenance cost?
- Is automation better than improving the manual process?

## 7. Mandatory readiness gates

A high score cannot compensate for a failed mandatory gate.

| Gate | Pass condition | Failure response |
|---|---|---|
| Inputs | Required evidence and formats are identifiable | Return to evidence preparation |
| Completion | A correct result can be tested | Add approved examples and checks |
| Policy | Standard-case rules are confirmed | Remain assisted |
| Exceptions | Exceptions can be detected | Do not enter production |
| Owner | Every exception has an accountable owner | Assign an owner first |
| Permission | Least-privilege access is available | Do not connect the system |
| Duplicate control | A case has a stable unique identity | Prohibit external writes |
| Recovery | Reversal or compensation is tested | Prohibit unattended actions |
| Emergency stop | Stop procedure and owner are confirmed | Do not enter production |
| Permission to use data | Legal, contractual, and policy use is confirmed | Stop or seek specialist review |
| Shadow test | Historical and shadow checks meet the contract | Improve or reject automation |

## 8. Automation levels

### L0: Not ready

Evidence, responsibility, policy, recovery, or authority is missing. The system
creates a refusal report and remediation path.

### L1: Assisted drafting

AI organizes evidence, asks questions, and prepares drafts. This corresponds to
the current Human Approval Edition.

### L2: Shadow mode

The system makes the proposed decisions without changing an external system.
Its result is compared with the real human outcome.

### L3: Conditional autopilot readiness

The assessment indicates that a future runtime could automate declared standard
cases and quarantine exceptions.

### L4: Unattended standard-path readiness

The assessment indicates that a future runtime could operate the confirmed
standard path without per-case approval, while stop, quarantine, recovery, and
audit controls remain active.

L3 and L4 are readiness labels for a future, separate Autopilot runtime. They
do not activate unattended execution in the current 22-pack project. Every
current pack keeps its human approval requirement.

A future no-per-case-approval runtime requires a separate action contract,
authorized business, legal, and security review, and a separate implementation.
The readiness result cannot remove a current approval requirement.

## 9. How the decision is made

The system does not use one model confidence score as the final decision.

1. Verify evidence integrity.
2. Evaluate mandatory gates deterministically.
3. Connect every conclusion to evidence.
4. Separate missing, conflicting, and inferred information.
5. Evaluate high-risk actions separately.
6. Review historical and shadow-test outcomes.
7. Show the maximum permitted level and the reason.

AI recommends a level. The organization confirms its policies and
responsibilities.

## 10. Existing pack restrictions cannot be overridden

An assessment may make a workflow stricter, but it cannot remove a prohibited
action or approval requirement from one of the 22 current packs.

For example, a high readiness result does not allow the current vendor pack to
change banking information, and it does not allow the current access pack to
grant permissions. Those operations would require a separate, specialist-
reviewed runtime contract.

## 11. Different meanings of "not possible"

### Not possible yet

The organization can return after preparing missing evidence, policy, or
recovery procedures.

### Not economically useful

It is technically possible, but volume is low, exceptions are frequent, or
maintenance cost exceeds the expected benefit.

### Human responsibility must remain

Employment, contracts, money, access, safety, and regulatory decisions may
require a person even when preparation is automated.

### Technically unavailable

The source cannot be read reliably, no supported connection exists, or the
only external action is irreversible.

### Not permitted by the organization

The proposed use conflicts with a policy, customer agreement, retention rule,
or data-location requirement.

## 12. The remediation roadmap

For every failed gate, AI creates:

- the gap;
- why it matters;
- the responsible owner;
- required evidence;
- practical steps;
- an acceptance check;
- a target date;
- the level that becomes possible after remediation.

Example:

```text
Gap: Requests do not have a stable unique identifier.
Risk: A retry could create a duplicate record.
Owners: Process owner and system administrator.
Remediation: Define a key using request ID and reporting period.
Acceptance: Replay 100 historical cases without duplicate creation.
Potential level after resolution: L3 conditional autopilot readiness.
```

## 13. Minimum shadow-test contract

An L3 or L4 recommendation requires at least:

- normal, near-limit, missing-data, duplicate, conflicting, expired, and
  external-failure cases;
- 100 representative cases or the most recent three months, whichever is
  larger, unless the volume does not exist and an owner records an extended L2
  monitoring plan;
- at least one case for every declared exception route;
- zero critical false negatives for high-risk consequences;
- rejection or quarantine of stale, changed, and incomplete evidence;
- replay without duplicate side effects;
- at least one recovery or compensation simulation;
- separate results by risk tier and case class.

An organization may require stricter criteria. A high average accuracy cannot
erase a critical-case failure.

## 14. Decision expiration

A previous decision becomes stale and returns to reassessment when any material
item changes:

- required inputs or fields;
- decision rules, limits, or exception routes;
- pack definition or prohibited actions;
- connector, permission, or authentication method;
- applicable law, contract, or policy;
- material AI model or extraction component;
- process owner, emergency-stop owner, or recovery procedure.

A readiness decision cannot authorize a pilot when its evidence or policy hash
no longer matches the approved snapshot.

## 15. Human confirmation record

Confirmation of a rule, gate, or final decision records:

- confirmer identity and role;
- confirmation time;
- source of the person's authority;
- pack manifest hash;
- evidence snapshot hash;
- prior decision hash;
- reason, limitations, and expiration conditions.

## 16. Screens

### Home

Start a feasibility assessment, resume an assessment, or open a decision.

### One-question interview

Show the question, why it matters, examples, evidence, and "I do not know."

### Evidence preparation

Show required, available, missing, unusable, and owner-pending evidence in text,
not by color alone.

### Current workflow map

Visualize human steps, evidence, decisions, exceptions, and outputs.

### Rule confirmation

Show condition, result, exception, evidence, and confirmer. AI-extracted rules
remain visibly marked as candidates.

### Shadow comparison

Place the human outcome, proposed outcome, difference, cause, and correction
side by side.

### Readiness decision

Show level, passed gates, failed gates, human boundaries, recommendation, and
next actions.

### Pilot preparation

Only after a positive result, confirm permissions, limits, stop controls,
recovery, and operating ownership.

## 17. Generated deliverables

- `current_workflow.md`
- `automation_scope.md`
- `source_inventory.csv`
- `decision_table.csv`
- `exception_register.csv`
- `connector_permissions.md`
- `recovery_plan.md`
- `kill_switch_plan.md`
- `shadow_test_cases.csv`
- `comparison_report.md`
- `readiness_decision.json`
- `readiness_report.html`
- `improvement_roadmap.md`
- `proposal_scope.md`

An organization receives useful evidence even when the decision is L0.

## 18. Applying it to all 22 packs

Every current pack can be assessed, but the pack name alone does not determine
the level. The decision depends on each organization's evidence, action scope,
policy, exceptions, permissions, recovery, and obligations.

- Reports and executive summaries are candidates for unattended local saving.
- Inquiry, sales, projects, meeting actions, internal requests, and handovers
  may support conditional low-risk routing or staging.
- Finance, attendance, expenses, invoices, employment, contracts, purchasing,
  compliance, access, quality, vendor, and grant workflows normally automate
  preparation while preserving consequential human decisions.

## 19. Production progression

1. Assess with sanitized or sample evidence.
2. Reproduce historical outcomes.
3. Compare human and AI results.
4. Run read-only shadow mode.
5. Pilot a small number of low-risk actions.
6. Expand volume and scope gradually.
7. Reassess rules, evidence, permissions, and ownership regularly.

Readiness is not permanent. Material change invalidates the old decision.

## 20. How it should be sold

Do not promise to automate everything.

Use a bounded promise:

> We identify the safe standard path, resolve missing requirements, automate
> what can be controlled, and stop or escalate what cannot be supported by the
> evidence.

An L0 result still delivers the current workflow, missing requirements,
remediation plan, responsibility map, and economic conclusion.

## 21. Success criteria

The product succeeds when:

- people understand what they need to provide next;
- missing evidence and ambiguous judgment stay visible;
- unsafe or uneconomic work is refused with a reason;
- solvable gaps receive an actionable route;
- human and AI outcomes can be compared;
- automated scope and human responsibility are explicit;
- a decision not to implement remains useful and explainable.

This is the governing philosophy for future Autopilot design and
implementation.
