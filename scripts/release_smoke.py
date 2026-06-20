from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / ".tmp" / "release-smoke"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the public-readiness smoke suite.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Directory for smoke outputs.")
    parser.add_argument("--skip-github", action="store_true", help="Skip live GitHub API checks.")
    args = parser.parse_args()

    output = Path(args.output)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    env = _env_with_src()
    _run([sys.executable, "scripts/public_release_audit.py"], env=env)
    _run([sys.executable, "-m", "pytest", "-q"], env=env)
    _run([sys.executable, "scripts/run_all_demos.py"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "doctor", "--output", str(output / "doctor")], env=env)
    _run_flow_smoke(output, env)
    _run_beginner_sales_smoke(output, env)
    _run_operator_console_smoke(output, env)

    wheelhouse = output / "wheelhouse"
    _run([sys.executable, "-m", "pip", "wheel", ".", "-w", str(wheelhouse)], env=env)
    _verify_wheel_install(wheelhouse, output)

    if not args.skip_github:
        _run_github_smokes(output, env)

    print(f"release smoke passed: {output}")
    return 0


def _run_flow_smoke(output: Path, env: dict[str, str]) -> None:
    flow_output = output / "flow-invoice-document-followup"
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "list"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "show", "invoice-document-followup"], env=env)
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "flows",
            "install",
            "invoice-document-followup",
            "--output",
            str(flow_output),
        ],
        env=env,
    )
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "validate", str(flow_output)], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "run", str(flow_output)], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "approve", str(flow_output), "--approver", "release@example.com"], env=env)
    _run([sys.executable, "scripts/run_dry_run.py"], cwd=flow_output, env=env)
    _run([sys.executable, "scripts/run_automation.py"], cwd=flow_output, env=env)
    _run([sys.executable, "scripts/approve_all.py", "--approver", "release@example.com"], cwd=flow_output, env=env)
    _run([sys.executable, "-m", "pytest", "tests/test_flow_contract.py", "-q"], cwd=flow_output, env=env)
    _require_file(flow_output / ".env.example")
    _require_file(flow_output / "config" / "connectors.json")
    _require_file(flow_output / "docs" / "SYSTEM_RUNBOOK.md")
    _require_file(flow_output / "flow.yaml")
    _require_file(flow_output / "workflow_map.mmd")
    _require_file(flow_output / "scripts" / "run_dry_run.py")
    _require_file(flow_output / "automation_output" / "work_queue.csv")
    _require_file(flow_output / "automation_output" / "draft_outputs.md")
    _require_file(flow_output / "automation_output" / "approval_queue.csv")
    _require_file(flow_output / "automation_output" / "status_report.md")
    _require_file(flow_output / "automation_output" / "run_log.json")
    _require_file(flow_output / "automation_output" / "approved_actions.csv")
    _require_file(flow_output / "local_outbox" / "email_drafts.md")
    _require_file(flow_output / "local_outbox" / "slack_messages.md")


def _run_beginner_sales_smoke(output: Path, env: dict[str, str]) -> None:
    beginner_output = output / "beginner-sales-accounting"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "beginner-sales",
            "--flow-id",
            "invoice-document-followup",
            "--client-type",
            "local-business",
            "--niche",
            "accounting",
            "--output",
            str(beginner_output),
        ],
        env=env,
    )
    _require_file(beginner_output / "README.md")
    _require_file(beginner_output / "START_HERE_FOR_SIDE_BUSINESS.md")
    _require_file(beginner_output / "flow_gallery.html")
    _require_file(beginner_output / "selected_flow_demo.html")
    _require_file(beginner_output / "proposal_one_pager.md")
    _require_file(beginner_output / "roi_simple_calculator.csv")
    _require_file(beginner_output / "three_day_poc_plan.md")
    _require_file(beginner_output / "client_delivery_checklist.md")
    _require_file(beginner_output / "differentiation_matrix.md")


def _run_operator_console_smoke(output: Path, env: dict[str, str]) -> None:
    quickstart_output = output / "quickstart-accounting"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "quickstart",
            "--flow-id",
            "invoice-document-followup",
            "--client-type",
            "local-business",
            "--niche",
            "accounting",
            "--output",
            str(quickstart_output),
        ],
        env=env,
    )
    _require_file(quickstart_output / "START_HERE.md")
    _require_file(quickstart_output / "flow_project" / "flow.yaml")
    _require_file(quickstart_output / "beginner_sales" / "selected_flow_demo.html")
    _require_file(quickstart_output / "demo_site" / "index.html")

    guide_output = output / "flow-guide-finance"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "flow-guide",
            "--industry",
            "finance",
            "--niche",
            "accounting",
            "--output",
            str(guide_output),
        ],
        env=env,
    )
    _require_file(guide_output / "recommended_flows.md")

    connector_output = output / "connector-doctor"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "connector-doctor",
            "--project",
            str(quickstart_output / "flow_project"),
            "--output",
            str(connector_output),
        ],
        env=env,
    )
    _require_file(connector_output / "connector_doctor.md")

    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "run", str(quickstart_output / "flow_project")], env=env)
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "flows",
            "approve",
            str(quickstart_output / "flow_project"),
            "--approver",
            "release@example.com",
        ],
        env=env,
    )
    report_output = output / "client-report"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "client-report",
            "--flow-project",
            str(quickstart_output / "flow_project"),
            "--output",
            str(report_output),
        ],
        env=env,
    )
    _require_file(report_output / "client_report.md")
    _require_file(report_output / "client_report.html")

    site_output = output / "operator-demo-site"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "demo-site",
            "--source",
            str(quickstart_output),
            "--output",
            str(site_output),
        ],
        env=env,
    )
    _require_file(site_output / "index.html")

    bundle_output = output / "install-bundle"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "install-bundle",
            "--flow-id",
            "invoice-document-followup",
            "--client-type",
            "local-business",
            "--niche",
            "accounting",
            "--output",
            str(bundle_output),
        ],
        env=env,
    )
    _require_file(bundle_output / "bundle_index.md")
    _require_file(bundle_output / "client_ready" / "maintenance_plan.md")

    package_output = output / "client-demo-package"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "package-client-demo",
            "--source",
            str(quickstart_output),
            "--output",
            str(package_output),
        ],
        env=env,
    )
    _require_file(package_output / "client_demo_manifest.json")
    _require_file(package_output / "client_demo_package.zip")

    complete_output = output / "complete-accounting"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "complete-workspace",
            "--flow-id",
            "invoice-document-followup",
            "--client-type",
            "local-business",
            "--niche",
            "accounting",
            "--approver",
            "release@example.com",
            "--output",
            str(complete_output),
        ],
        env=env,
    )
    _require_file(complete_output / "FINAL_DELIVERY_GUIDE.md")
    _require_file(complete_output / "completion_checklist.md")
    _require_file(complete_output / "delivery_manifest.json")
    _require_file(complete_output / "revenue_readiness_scorecard.md")
    _require_file(complete_output / "sales_closing_script.md")
    _require_file(complete_output / "paid_poc_scope.md")
    _require_file(complete_output / "value_measurement_sheet.csv")
    _require_file(complete_output / "pre_contract_checklist.md")
    _require_file(complete_output / "client_proposal_email.md")
    _require_file(complete_output / "first_30_days_plan.md")
    _require_file(complete_output / "proof_of_value_template.md")
    _require_file(complete_output / "quickstart" / "flow_project" / "automation_output" / "run_log.json")
    _require_file(complete_output / "quickstart" / "flow_project" / "local_outbox" / "email_drafts.md")
    _require_file(complete_output / "connector_doctor" / "connector_doctor.md")
    _require_file(complete_output / "client_report" / "client_report.html")
    _require_file(complete_output / "client_demo_package" / "client_demo_package.zip")


def _run_github_smokes(output: Path, env: dict[str, str]) -> None:
    onboard_output = output / "onboard-operations"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "onboard",
            "--business-area",
            "operations",
            "--limit",
            "1",
            "--output",
            str(onboard_output),
            "--create-offer-pack",
        ],
        env=env,
    )
    _require_file(onboard_output / "onboarding_summary.md")
    _require_file(onboard_output / "onboarding_summary.json")
    _require_file(onboard_output / "doctor" / "doctor_report.md")
    _require_file(onboard_output / "github_discover_config.json")
    _require_file(onboard_output / "offer_pack" / "README.md")
    _require_file(onboard_output / "offer_pack" / "proposal.md")
    _require_file(onboard_output / "offer_pack" / "statement_of_work.md")
    _require_file(onboard_output / "offer_pack" / "pricing_model.md")

    offer_output = output / "offer-pack-operations"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "offer-pack",
            "--business-area",
            "operations",
            "--client-type",
            "small-business",
            "--source-output",
            str(onboard_output),
            "--output",
            str(offer_output),
        ],
        env=env,
    )
    _require_file(offer_output / "README.md")
    _require_file(offer_output / "service_catalog.md")
    _require_file(offer_output / "client_discovery_questions.md")
    _require_file(offer_output / "proposal.md")
    _require_file(offer_output / "statement_of_work.md")
    _require_file(offer_output / "pricing_model.md")
    _require_file(offer_output / "risk_boundaries.md")

    client_ready_output = output / "client-ready-accounting"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "client-ready",
            "--business-area",
            "operations",
            "--client-type",
            "local-business",
            "--niche",
            "accounting",
            "--source-output",
            str(onboard_output),
            "--output",
            str(client_ready_output),
        ],
        env=env,
    )
    _require_file(client_ready_output / "README.md")
    _require_file(client_ready_output / "client_intake.md")
    _require_file(client_ready_output / "roi_calculator.csv")
    _require_file(client_ready_output / "proposal_tiers.md")
    _require_file(client_ready_output / "implementation_readiness_score.json")
    _require_file(client_ready_output / "security_review.md")
    _require_file(client_ready_output / "tool_stack_recommendation.md")
    _require_file(client_ready_output / "maintenance_plan.md")
    _require_file(client_ready_output / "marketplace_profile.md")
    _require_file(client_ready_output / "case_study_template.md")

    adapter_output = output / "github-operations"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "github-discover",
            "--business-area",
            "operations",
            "--limit",
            "2",
            "--output",
            str(adapter_output),
        ],
        env=env,
    )
    _require_file(adapter_output / "run_summary.md")
    _require_file(adapter_output / "run_summary.json")
    _require_file(adapter_output / "executive_decision_brief.md")
    _require_file(adapter_output / "executive_decision_brief.json")
    _require_file(adapter_output / "pilot_scorecard.md")
    _require_file(adapter_output / "pilot_scorecard.json")
    _require_file(adapter_output / "pilot_scorecard.csv")
    _require_file(adapter_output / "enterprise_readiness.md")
    _require_file(adapter_output / "enterprise_readiness.json")
    _require_file(adapter_output / "value_realization_plan.md")
    _require_file(adapter_output / "value_realization_plan.json")
    _require_file(adapter_output / "value_measurement_report.md")
    _require_file(adapter_output / "value_measurement_report.json")
    _require_file(adapter_output / "stakeholder_rollout_map.md")
    _require_file(adapter_output / "stakeholder_rollout_map.json")
    _require_file(adapter_output / "risk_exception_register.md")
    _require_file(adapter_output / "risk_exception_register.json")
    _require_file(adapter_output / "operational_audit_plan.md")
    _require_file(adapter_output / "operational_audit_plan.json")
    _run([sys.executable, "adapter_starter/smoke_test.py"], cwd=adapter_output, env=env)

    review_output = output / "github-support"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "github-discover",
            "--business-area",
            "support",
            "--limit",
            "2",
            "--output",
            str(review_output),
        ],
        env=env,
    )
    _require_file(review_output / "run_summary.md")
    _require_file(review_output / "run_summary.json")
    _require_file(review_output / "executive_decision_brief.md")
    _require_file(review_output / "executive_decision_brief.json")
    _require_file(review_output / "pilot_scorecard.md")
    _require_file(review_output / "pilot_scorecard.json")
    _require_file(review_output / "pilot_scorecard.csv")
    _require_file(review_output / "enterprise_readiness.md")
    _require_file(review_output / "enterprise_readiness.json")
    _require_file(review_output / "value_realization_plan.md")
    _require_file(review_output / "value_realization_plan.json")
    _require_file(review_output / "value_measurement_report.md")
    _require_file(review_output / "value_measurement_report.json")
    _require_file(review_output / "stakeholder_rollout_map.md")
    _require_file(review_output / "stakeholder_rollout_map.json")
    _require_file(review_output / "risk_exception_register.md")
    _require_file(review_output / "risk_exception_register.json")
    _require_file(review_output / "operational_audit_plan.md")
    _require_file(review_output / "operational_audit_plan.json")
    _require_file(review_output / "manual_review_pack.md")
    _require_file(review_output / "manual_review_pack.json")


def _env_with_src() -> dict[str, str]:
    env = os.environ.copy()
    src_path = str(ROOT / "src")
    env["PYTHONPATH"] = src_path if not env.get("PYTHONPATH") else f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
    return env


def _verify_wheel_install(wheelhouse: Path, output: Path) -> None:
    wheels = sorted(wheelhouse.glob("ai_automation_starter_kit-*.whl"))
    if not wheels:
        raise FileNotFoundError(f"No ai_automation_starter_kit wheel found in {wheelhouse}")

    venv_dir = output / "install-venv"
    _run([sys.executable, "-m", "venv", str(venv_dir)], env=os.environ.copy())
    python_bin = _venv_python(venv_dir)
    _run([str(python_bin), "-m", "pip", "install", str(wheels[-1])], env=os.environ.copy())
    cli_bin = _venv_console_script(venv_dir, "ai-automation-kit")
    _run([str(cli_bin), "--version"], env=os.environ.copy())
    _run([str(cli_bin), "doctor", "--output", str(output / "installed-doctor")], env=os.environ.copy())


def _venv_python(venv_dir: Path) -> Path:
    posix_python = venv_dir / "bin" / "python"
    if posix_python.exists():
        return posix_python
    return venv_dir / "Scripts" / "python.exe"


def _venv_console_script(venv_dir: Path, name: str) -> Path:
    posix_script = venv_dir / "bin" / name
    if posix_script.exists():
        return posix_script
    return venv_dir / "Scripts" / f"{name}.exe"


def _run(command: list[str], env: dict[str, str], cwd: Path | None = None) -> None:
    print("$ " + " ".join(command))
    subprocess.run(command, cwd=cwd or ROOT, env=env, check=True)


def _require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Expected release smoke artifact was not created: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
