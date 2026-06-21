# AI Grill Me Guide

This guide helps AI beginners use an AI agent when they do not know what to ask.

A grill-me workflow does not mean asking AI to do everything. It means asking the AI to interview you **one question at a time**, challenge vague answers, identify missing information, and stop unsafe shortcuts before you promise or deploy too much.

## Why This Exists

Experienced AI users know they can ask an AI agent for clarification. Beginners often do not know what to ask, what they may safely paste, or how to judge the answer.

This project uses `grill-me` to close that gap.

You can use the skill without running the CLI. Open [AI Agent Grill Me Skill](AI_AGENT_GRILL_ME_SKILL.md), copy the skill text into ChatGPT, Claude, Gemini, Cursor, Codex, Claude Code, or another AI agent, and ask it to interview you one question at a time. The command below is only for users who want the same guidance saved as local files.

```bash
ai-automation-kit grill-me \
  --flow-id invoice-document-followup \
  --mode beginner \
  --client-type local-business \
  --deployment cloud \
  --connectors gmail,google-sheets \
  --output .tmp/grill-me
```

Generated files:

- `START_HERE_GRILL_ME.md`
- `questions_to_answer.md`
- `client_interview_grill.md`
- `cloud_readiness_grill.md`
- `risk_grill.md`
- `proposal_grill.md`
- `ai_agent_prompt.md`
- `grill_me.json`

## Rules

- Ask one question at a time.
- Do not accept vague answers.
- Do not paste real API keys or secrets.
- Do not paste sensitive client data.
- Keep production sending, real webhooks, schedulers, queues, and cloud traffic blocked until human approval is explicit.
- Do not promise full automation, guaranteed revenue, or unmanned operations.

## First Prompt

```text
I am new to AI agents.
I want to use ai-automation-starter-kit to propose a small business automation PoC.

Please ask me one question at a time.
Do not give me a long explanation first.
If my answer is vague, challenge it and ask the next clarifying question.

Do not ask me to paste real API keys or secrets.
Keep production sending, real webhooks, schedulers, queues, and cloud traffic blocked until human approval is explicit.

Start by helping me decide which business workflow is safe and useful to automate first.
```

## Safe To Share With AI

- README links.
- docs links.
- Redacted error messages.
- File names.
- Flow IDs.
- Business type.
- Sample data shape.
- Command output after removing secrets and personal data.

## Do Not Share

- Real API keys.
- Passwords.
- OAuth tokens.
- Private keys.
- Client personal data.
- Regulated medical, legal, or financial decision data.
- Production admin access.

## Better Prompting

Weak:

```text
Automate everything.
```

Better:

```text
Please check whether this workflow is a good automation candidate.
Ask one question at a time and separate client questions, sample data, and human approval points.
```

Weak:

```text
Tell me everything about AWS deployment.
```

Better:

```text
Read the cloud-plan output and ask me what to verify next.
Separate billing, secrets, IAM, logs, rollback, and human approval.
```

## Beginner Blockers This Solves

1. Not knowing which workflow to choose.
2. Not knowing what to ask a client.
3. Not knowing how to handle API keys and secrets.
4. Not knowing what to choose in a cloud provider console.
5. Not knowing what to show an AI when an error appears.
6. Not knowing what is safe to propose.

## Target Outcome

The beginner should be able to explain:

- Which workflow is being automated.
- Why it is a good PoC candidate.
- What input is required.
- What output is created.
- Who approves it.
- What will not be automated.
- What must be checked before cloud deployment.
- How to explain it to the client.
