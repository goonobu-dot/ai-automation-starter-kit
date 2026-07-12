# AI Automation Starter Kit

Daily workflow automation: [日本語の初心者ガイド](docs/daily-workflows.ja.html) | [English beginner guide](docs/daily-workflows.html)

AI Automation Starter Kit is a GitHub-data-driven AI agent skill kit for people who want to propose and deliver small, safe business automation projects — especially beginners selling automation to small and medium companies. One command generates client-ready artifacts: demos, discovery questions, proposals, pricing menus, dry-run flow projects, and delivery checklists. Nothing is sent externally: every risky action stays behind a human approval step.

## 日本語の方へ：3ステップで始める

このキットは「AIエージェント初心者が、中小企業へ業務自動化を提案する副業」を想定して作られています。最初から全部読まないでください。次の3ステップだけで始められます。

**ステップ1: インストール**

```bash
git clone https://github.com/goonobu-dot/ai-automation-starter-kit.git
cd ai-automation-starter-kit
python3 -m venv .venv
source .venv/bin/activate
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
```

**ステップ2: 初心者ナビを起動**

```bash
ai-automation-kit beginner
```

日本語のナビが「今のあなたの段階」に合わせて、次にやることを教えてくれます。

**ステップ3: 入口ドキュメントを読む**

[docs/GETTING_STARTED.ja.md（はじめかた）](docs/GETTING_STARTED.ja.md) が唯一の入口です。30分で最初のデモまで完走できます。その先は [docs/INDEX.md（ドキュメント索引）](docs/INDEX.md) から必要なものだけ開いてください。

> **Phase 1A platform note / 対応OS:** Safe monthly office-workspace creation and approval mutation require macOS or Linux. Windows stops before creating or changing this workspace because the required race-resistant no-follow filesystem operations are unavailable in this design. Existing read-only and unrelated kit features are unaffected. / 安全な月次オフィスワークスペースの作成・承認更新は macOS または Linux 専用です。Windows では必要な安全機能がないため、フォルダを作成・変更する前に停止します。既存の読み取り専用機能や他の機能には影響しません。

## Phase 1A: monthly office workspace

If you want a Codex-led monthly office workspace instead of the broader sales or demo flows, start from the two setup notes and the paired manuals below. This is a local-only monthly-report route for beginners who want one safe review loop: create the workspace, place approved files, inspect, answer, generate, approve, and roll to the next month.

- Setup prompt for Codex: [START_WITH_CODEX.ja.md](START_WITH_CODEX.ja.md) / [START_WITH_CODEX.md](START_WITH_CODEX.md)
- Browser manual for the monthly office workspace: [docs/office-workspace.ja.html](docs/office-workspace.ja.html) / [docs/office-workspace.html](docs/office-workspace.html)
- Honest status: Phase 1A is one monthly office workspace and one monthly-report pack. No API key is required, and no external sending occurs.

## English Quick Start

Do not read everything first. Install, run the doctor, and generate one complete demo workspace:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
ai-automation-kit --version
ai-automation-kit doctor --output .tmp/doctor
ai-automation-kit complete-workspace --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/complete-accounting
```

Then open `.tmp/complete-accounting/client_command_center.html` and `.tmp/complete-accounting/FINAL_DELIVERY_GUIDE.md`. To verify the install, run `python3 -m pytest -q` and `python3 scripts/run_all_demos.py`.

The CLI is optional: this project is also an AI agent skill kit. It is not a requirement to use a CLI-based AI agent. Open the [AI Agent Grill Me Skill](docs/AI_AGENT_GRILL_ME_SKILL.md) ([日本語](docs/AI_AGENT_GRILL_ME_SKILL.ja.md)), paste it into ChatGPT, Claude, Gemini, Cursor, Codex, or Claude Code, and ask the AI to read the skill document and interview you one question at a time. Keep real API keys, passwords, and client private data out of chat.

## Documentation

Start from the **[Documentation Index (docs/INDEX.md)](docs/INDEX.md)**. It groups every document into five categories: 🔰 Getting Started, 💼 Sales & Monetization, ⚙️ Execution & Operations, ☁️ Cloud, and 📚 Reference & Archive. Read only the 🔰 category first.

Key documents:

| Purpose | 日本語 | English |
|---|---|---|
| The single entrance (install to first demo) | [はじめかた](docs/GETTING_STARTED.ja.md) | – |
| Choose your route | [初心者ルートマップ](docs/BEGINNER_ROUTE_MAP.ja.md) | [Beginner Route Map](docs/BEGINNER_ROUTE_MAP.md) |
| Plain-language overview | [やさしい解説](docs/BEGINNER_GUIDE.ja.md) | [Beginner Guide](docs/BEGINNER_GUIDE.md) |
| Operating manual | [使い方マニュアル](docs/USER_MANUAL.ja.md) | [User Manual](docs/USER_MANUAL.md) |
| Browser manual (click to open as a web page) | [ブラウザ版マニュアル（クリックで開きます）](https://goonobu-dot.github.io/ai-automation-starter-kit/manual.ja.html) | [Browser Manual](https://goonobu-dot.github.io/ai-automation-starter-kit/manual.html) |
| Codex monthly setup prompt | [Codexではじめる](START_WITH_CODEX.ja.md) | [Start With Codex](START_WITH_CODEX.md) |
| Monthly office workspace manual | [月報オペレーター作業場所マニュアル](docs/office-workspace.ja.html) | [Monthly Operator Workspace Manual](docs/office-workspace.html) |
| Report wizard manual | [レポートウィザード手順書](docs/report-automation-wizard.ja.html) | [Report Wizard Manual](docs/report-automation-wizard.html) |
| Selling automation responsibly | [提案ガイド](docs/SELLING_AUTOMATION_GUIDE.ja.md) | [Selling Automation Guide](docs/SELLING_AUTOMATION_GUIDE.md) |
| Choosing what to sell | [副業ブループリント](docs/SIDE_HUSTLE_BLUEPRINTS.ja.md) | [Side Hustle Blueprints](docs/SIDE_HUSTLE_BLUEPRINTS.md) |
| 2026 side-hustle market update | [副業向けGitHub市場アップデート](docs/SIDE_HUSTLE_MARKET_UPDATE_2026.ja.md) | – |
| Folder-based report automation | [日報・月報AI下書き自動化ガイド](docs/REPORT_AUTOMATION_GUIDE.ja.md) | [Report Automation Guide](docs/REPORT_AUTOMATION_GUIDE.md) |
| Running the client demo | [顧客デモ台本](docs/CLIENT_DEMO_SCRIPT.ja.md) | [Client Demo Script](docs/CLIENT_DEMO_SCRIPT.md) |
| Choosing a flow | [フロー選択ガイド](docs/FLOW_SELECTION_GUIDE.ja.md) | [Flow Selection Guide](docs/FLOW_SELECTION_GUIDE.md) |
| Moving toward real operations | [実運用セットアップ](docs/REAL_WORLD_SETUP_GUIDE.ja.md) | [Real-World Setup Guide](docs/REAL_WORLD_SETUP_GUIDE.md) |
| Connector setup | [連携設定ガイド](docs/CONNECTOR_SETUP_GUIDE.ja.md) | [Connector Setup Guide](docs/CONNECTOR_SETUP_GUIDE.md) |
| Advanced packs | [拡充機能ガイド](docs/AUTOMATION_EXPANSION_GUIDE.ja.md) | [Automation Expansion Guide](docs/AUTOMATION_EXPANSION_GUIDE.md) |
| Cloud deployment | [クラウド導入ガイド](docs/CLOUD_DEPLOYMENT_GUIDE.ja.md) | [Cloud Deployment Guide](docs/CLOUD_DEPLOYMENT_GUIDE.md) |
| First cloud steps | [クラウド挑戦プレイブック](docs/CLOUD_BEGINNER_PLAYBOOK.ja.md) | [Cloud Beginner Playbook](docs/CLOUD_BEGINNER_PLAYBOOK.md) |
| Cloud troubleshooting | [クラウド トラブルシューティング](docs/CLOUD_TROUBLESHOOTING.ja.md) | [Cloud Troubleshooting](docs/CLOUD_TROUBLESHOOTING.md) |
| FAQ | [FAQ](docs/FAQ.ja.md) | [FAQ](docs/FAQ.md) |
| Public demo story | – | [Showcase](docs/SHOWCASE.md) / [Demo page](docs/demo.html) |

## What You Get

The fastest path is `complete-workspace`: one command creates a full local delivery folder with a dry-run flow project, a browser demo site, a client report, sales assets, and a `client_command_center.html` menu page. Around it, focused commands generate:

- **Sales assets** — `beginner-sales` writes `START_HERE_FOR_SIDE_BUSINESS.md`, `flow_gallery.html`, `selected_flow_demo.html`, `proposal_one_pager.md`, `three_day_poc_plan.md`, discovery questions, a price menu, and `roi_simple_calculator.csv`. `offer-pack` writes `proposal.md`, `statement_of_work.md`, `pricing_model.md`, and risk boundaries under `offer_pack/`. `client-ready/` adds `roi_calculator.csv`, `implementation_readiness_score.json`, and `maintenance_plan.md`.
- **Runnable flows** — `flows` installs one of 60+ dry-run automation projects with `flow.yaml`, `workflow_map.mmd`, `operator_ui/index.html`, `.env.example`, `SYSTEM_RUNBOOK.md`, and scripts that generate `automation_output` work queues, approval queues, and `local_outbox` drafts. Nothing is sent externally.
- **Folder-based report automation** — `report-automation` creates a daily, weekly, or monthly report workspace with past-output folders, current-material folders, `START_HERE_REPORT_AUTOMATION.md`, AI prompts, `grill_me_report_questions.md`, drafts, approval checklists, and a client-facing `demo_report_automation.html`.
- **Resumable report wizard** — `report-wizard` adds `report_wizard_state.json`, `03_templates/*_report_template.md`, `04_ai_analysis/{source_manifest.json,schema_proposal.json,provenance.json,ai_agent_review_instructions.md}`, `05_grill_me_questions/session.json`, `06_drafts/*_report_draft.md`, and `07_approval/approval.json` so a human can inspect, answer, build, approve, and resume a local reporting session.
- **Codex-led monthly office workspace** — `office-workspace` creates a monthly office workspace with `00_START_HERE`, `01_APPROVED_PAST_OUTPUTS`, `02_PAST_SUPPORTING_FILES`, `03_CURRENT_INPUTS/<YYYY-MM>`, `04_QUESTIONS`, `05_DRAFTS`, `06_APPROVED_OUTPUTS`, and `07_AUDIT`, then serves a localhost UI for inspect, answer, generate, cancel, approve, and rollover. This Phase 1A route is local-only, monthly-report only, and intended for macOS or Linux.
- **Delivery evidence** — `FINAL_DELIVERY_GUIDE.md`, `completion_checklist.md`, `client_report.md`, `client_demo_package.zip`, `revenue_readiness_scorecard.md`, `paid_poc_scope.md`, and `share_check.md` (scan before sharing).
- **Setup and cloud planning** — `guided-setup`, `guided-review`, and `cloud-plan` write question lists, readiness reports, and provider-specific runbooks such as `workload_architecture.md`, `deploy_runbook.md`, and `human_approval_required.md`.
- **GitHub discovery** — `github-discover` and `onboard` turn public GitHub research into `run_summary.md`, `executive_decision_brief.md`, `pilot_scorecard.csv`, `value_realization_plan.md`, `value_measurement_report.md`, `stakeholder_rollout_map.md`, `risk_exception_register.md`, `operational_audit_plan.md`, `enterprise_readiness.md`, `artifact_index.md`, and an `adapter_starter/` dry-run skeleton.

See the [User Manual](docs/USER_MANUAL.ja.md) for every command and every generated file, with output examples.

## Command Reference

Setup and diagnosis:

```bash
ai-automation-kit --version
ai-automation-kit doctor --output .tmp/doctor
ai-automation-kit beginner
```

The main one-command paths:

```bash
ai-automation-kit complete-workspace --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/complete-accounting
ai-automation-kit quickstart --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/quickstart-accounting
ai-automation-kit beginner-sales --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/beginner-sales
ai-automation-kit onboard --business-area operations --limit 2 --output .tmp/onboarding --create-offer-pack
```

Flow catalog (60+ ready-made business automation flows):

```bash
ai-automation-kit flows list
ai-automation-kit flows list --industry finance
ai-automation-kit flows list --industry reception
ai-automation-kit flows list --industry admin
ai-automation-kit flows list --industry sales-research
ai-automation-kit flows show invoice-document-followup
ai-automation-kit flows install invoice-document-followup --output .tmp/flow-invoice-document-followup
ai-automation-kit flows install ai-reception-line-inquiry --output .tmp/ai-reception-line-inquiry
ai-automation-kit flows install daily-monthly-report-automation --output .tmp/daily-monthly-report-automation
ai-automation-kit flows validate .tmp/flow-invoice-document-followup
ai-automation-kit flows run .tmp/flow-invoice-document-followup
ai-automation-kit flows approve .tmp/flow-invoice-document-followup --approver owner@example.com
```

Sales, packaging, and delivery:

```bash
ai-automation-kit offer-pack --business-area operations --client-type small-business --source-output .tmp/onboarding --output .tmp/offer-pack
ai-automation-kit client-ready --business-area operations --client-type local-business --niche accounting --source-output .tmp/onboarding --output .tmp/client-ready
ai-automation-kit business-launch --industry finance --client-type local-business --niche accounting --output .tmp/business-launch
ai-automation-kit side-hustle-blueprints --industry local-business --operator-level beginner --output .tmp/side-hustle-blueprints
ai-automation-kit report-automation --report-type monthly --client-type local-business --niche construction --output .tmp/monthly-report-pack
ai-automation-kit report-wizard init --workspace .tmp/report-wizard-weekly --report-type weekly --language en
ai-automation-kit report-wizard inspect --workspace .tmp/report-wizard-weekly --past-outputs .tmp/past.md --materials .tmp/current.csv
ai-automation-kit report-wizard confirm --workspace .tmp/report-wizard-weekly
ai-automation-kit report-wizard answer --workspace .tmp/report-wizard-weekly --answer "Operations manager"
ai-automation-kit report-wizard status --workspace .tmp/report-wizard-weekly --json
ai-automation-kit report-wizard build --workspace .tmp/report-wizard-weekly
ai-automation-kit report-wizard approve --workspace .tmp/report-wizard-weekly --approver owner@example.com
ai-automation-kit report-wizard serve --workspace .tmp/report-wizard-weekly --language en --no-open
ai-automation-kit opportunity-catalog --industry finance --output .tmp/opportunity-catalog
ai-automation-kit recommend-flow --industry finance --pain "missing invoice follow up" --tools "Google Sheets Gmail" --output .tmp/recommend-flow
ai-automation-kit flow-guide --industry finance --niche accounting --output .tmp/flow-guide
ai-automation-kit install-bundle --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/client-bundle
ai-automation-kit demo-site --source .tmp/quickstart-accounting --output .tmp/quickstart-accounting/demo_site
ai-automation-kit connector-doctor --project .tmp/quickstart-accounting/flow_project --output .tmp/connector-doctor
ai-automation-kit client-report --flow-project .tmp/quickstart-accounting/flow_project --output .tmp/client-report
ai-automation-kit package-client-demo --source .tmp/quickstart-accounting --output .tmp/client-demo-package
ai-automation-kit share-check --source .tmp/complete-accounting --output .tmp/share-check
```

For the step-by-step local review flow, open [docs/report-automation-wizard.html](docs/report-automation-wizard.html) / [docs/report-automation-wizard.ja.html](docs/report-automation-wizard.ja.html). GitHub Pages hosts the same manual at [English](https://goonobu-dot.github.io/ai-automation-starter-kit/report-automation-wizard.html) / [日本語](https://goonobu-dot.github.io/ai-automation-starter-kit/report-automation-wizard.ja.html), alongside the general browser manuals at [manual.html](https://goonobu-dot.github.io/ai-automation-starter-kit/manual.html) and [manual.ja.html](https://goonobu-dot.github.io/ai-automation-starter-kit/manual.ja.html).

Codex-led monthly office workspace (Phase 1A, macOS/Linux only):

```bash
codex login status
ai-automation-kit office-workspace create --root ./workspaces --name "Construction Monthly" --approver "Operations Manager" --pin 482913 --period 2026-07 --language en
ai-automation-kit office-workspace status --workspace ./workspaces/Construction_Monthly --json
ai-automation-kit office-workspace inspect --workspace ./workspaces/Construction_Monthly --period 2026-07
ai-automation-kit office-workspace serve --root ./workspaces --language en --no-open
```

For the guided prompt and the browser manual, open [START_WITH_CODEX.md](START_WITH_CODEX.md) / [START_WITH_CODEX.ja.md](START_WITH_CODEX.ja.md) and [docs/office-workspace.html](docs/office-workspace.html) / [docs/office-workspace.ja.html](docs/office-workspace.ja.html).

Setup intake, review, and cloud planning:

```bash
ai-automation-kit guided-setup --flow-id ai-reception-line-inquiry --mode beginner --deployment undecided --connectors line,gmail,google-sheets --output .tmp/guided-setup
ai-automation-kit guided-review --answers .tmp/guided-setup/guided_setup_answers.example.json --output .tmp/guided-review
ai-automation-kit cloud-plan --flow-id invoice-document-followup --provider aws --workload scheduled-job --connectors gmail,google-sheets --output .tmp/cloud-plan-aws
ai-automation-kit grill-me --flow-id invoice-document-followup --mode beginner --client-type local-business --deployment cloud --connectors gmail,google-sheets --output .tmp/grill-me
```

Public-pattern expansion packs (menu first, then the pack you need):

```bash
ai-automation-kit command-center --language both --output .tmp/command-center
ai-automation-kit skill-pack --flow-id invoice-document-followup --agent codex --output .tmp/skill-pack
ai-automation-kit approval-gate --flow-id invoice-document-followup --output .tmp/approval-gate
ai-automation-kit mcp-connector-plan --flow-id invoice-document-followup --connectors gmail,google-sheets,slack --output .tmp/mcp-connector-plan
ai-automation-kit agent-team --flow-id invoice-document-followup --output .tmp/agent-team
ai-automation-kit workflow-explainer --flow-id invoice-document-followup --audience client --output .tmp/workflow-explainer
ai-automation-kit eval-loop --flow-id invoice-document-followup --metric hours_saved --output .tmp/eval-loop
ai-automation-kit self-host-pack --flow-id invoice-document-followup --provider docker --output .tmp/self-host-pack
ai-automation-kit connector-catalog --industry local-business --output .tmp/connector-catalog
ai-automation-kit script-ui-pack --flow-id invoice-document-followup --output .tmp/script-ui-pack
ai-automation-kit knowledge-rag-pack --flow-id ai-admin-faq-routing --output .tmp/knowledge-rag-pack
ai-automation-kit automation-hooks --flow-id invoice-document-followup --output .tmp/automation-hooks
ai-automation-kit governance-pack --flow-id invoice-document-followup --output .tmp/governance-pack
ai-automation-kit website-side-hustle --industry hospitality --client-type local-business --niche tourism-hotel --output .tmp/website-side-hustle
```

Execution bridges toward real platforms:

```bash
ai-automation-kit flow-export --flow-id invoice-document-followup --target n8n --output .tmp/flow-export-n8n
ai-automation-kit deployment-pack --flow-id invoice-document-followup --provider coolify --connectors gmail,google-sheets --output .tmp/deployment-coolify
ai-automation-kit runtime-safety --flow-id invoice-document-followup --output .tmp/runtime-safety
ai-automation-kit secrets-bootstrap --flow-id invoice-document-followup --provider infisical --connectors gmail,google-sheets --output .tmp/secrets-bootstrap
ai-automation-kit document-intake --flow-id invoice-document-followup --mode advanced --output .tmp/document-intake
ai-automation-kit observability-pack --flow-id invoice-document-followup --output .tmp/observability-pack
ai-automation-kit state-backend --flow-id invoice-document-followup --backend supabase --output .tmp/state-backend
```

GitHub discovery and reusable templates:

```bash
ai-automation-kit github-discover --business-area operations --limit 2 --output .tmp/operations-discovery
ai-automation-kit research-agent --config examples/research-agent/sample_research.json --output .tmp/research-agent-demo
ai-automation-kit research-agent --config examples/research-agent/github_repos.json --output .tmp/github-repo-demo
ai-automation-kit docs-rag --config examples/docs-rag/sample_docs_rag.json --output .tmp/docs-rag-demo
ai-automation-kit internal-ai-workflow --config examples/internal-ai-workflow/sample_inquiry.json --output .tmp/internal-ai-workflow-demo
ai-automation-kit excel-to-internal-app --config examples/excel-to-internal-app/sample_app.json --output .tmp/excel-to-internal-app-demo
ai-automation-kit delivery-pipeline --config examples/delivery-pipeline/sample_delivery_pipeline.json --output .tmp/delivery-pipeline-demo
python3 scripts/run_all_demos.py
```

Supported business areas for discovery include `sales`, `support`, `finance`, `operations`, `marketing`, and `hr`. Set `GITHUB_TOKEN` in your shell for higher GitHub API rate limits. See `docs/GITHUB_DATA.md` for supported fields and search settings.

Checked-in expected outputs for the template commands:

- `examples/research-agent/expected/report.md`
- `examples/docs-rag/expected/answer.md`
- `examples/internal-ai-workflow/expected/draft_reply.md`
- `examples/excel-to-internal-app/expected/migration-report.md`
- `examples/delivery-pipeline/expected/delivery-checklist.md`

## How This Fits With Local Agent Workbenches

This project pairs well with `goonobu-dot/local-agent-workbench` and `goonobu-dot/claude-code-workbench`. The workbenches give you a local multi-agent cockpit; this starter kit gives those agents a repeatable business automation path from discovery to packaged delivery.

## Safety Defaults

- Runtime outputs go under `.tmp/` and are ignored by Git.
- `.env` files are ignored; `.env.example` contains placeholders only.
- The local flow runtime is dry-run only: it drafts, queues, and reports, but never sends external messages, moves money, or updates production systems.
- `research-agent` rejects localhost and private network HTTP targets, and failed fetches mask sensitive query parameters.
- `internal-ai-workflow` creates pending dry-run approval records instead of sending messages.
- Third-party OSS integrations are adapter-only until license review. See `docs/OSS_INTEGRATIONS.md`.
- No income is guaranteed. The kit packages the work responsibly; it does not promise revenue.

## Public Release Readiness

Before publishing a release, run:

```bash
python3 scripts/public_release_audit.py
python3 scripts/release_smoke.py
```

See [docs/PUBLISHING.md](docs/PUBLISHING.md) and [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) for the full release process.
