# Client Demo Script

Use this script when showing AI Automation Starter Kit outputs to a company.

## 1. Opening

Say:

> Today I am not showing a large production system. I am showing a safe dry-run for one repeated workflow. It creates a work queue, draft outputs, an approval queue, and a report without sending external messages or updating production systems.

## 2. Show The Flow

Open:

```text
.tmp/quickstart-accounting/beginner_sales/selected_flow_demo.html
```

Explain:

- where the data enters
- what the automation organizes
- where human approval happens
- what evidence remains after the run

## 3. Ask Questions

Use the generated `client_questions.md` or `discovery_call_script.md`.

Focus on:

- current manual process
- monthly volume
- minutes per item
- current tools
- approval owner
- data that can be safely sampled
- actions that must not be automated

## 4. Show The Dry-Run Evidence

Open files such as:

- `automation_output/work_queue.csv`
- `automation_output/draft_outputs.md`
- `automation_output/approval_queue.csv`
- `automation_output/status_report.md`
- `client_report/client_report.html`

Explain that this is evidence for a decision, not a claim that everything should go live immediately.

## 5. Ask For A Decision

End with three choices:

- continue
- revise and test again
- stop

This continue, revise, or stop decision is the point of a good first PoC.

