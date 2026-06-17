from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ai_automation_kit import __version__
from ai_automation_kit.templates.docs_rag import run_docs_rag
from ai_automation_kit.templates.delivery_pipeline import run_delivery_pipeline
from ai_automation_kit.templates.excel_to_internal_app import run_excel_to_internal_app
from ai_automation_kit.templates.internal_ai_workflow import run_internal_ai_workflow
from ai_automation_kit.templates.research_agent import run_research_agent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-automation-kit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    research = subparsers.add_parser("research-agent")
    research.add_argument("--config", required=True)
    research.add_argument("--output", required=True)

    discover = subparsers.add_parser("github-discover")
    discover.add_argument("--business-area", default="operations")
    discover.add_argument("--query")
    discover.add_argument("--limit", type=int, default=5)
    discover.add_argument("--output", required=True)
    discover.add_argument("--include-readme", action="store_true")

    docs_rag = subparsers.add_parser("docs-rag")
    docs_rag.add_argument("--config", required=True)
    docs_rag.add_argument("--output", required=True)

    internal = subparsers.add_parser("internal-ai-workflow")
    internal.add_argument("--config", required=True)
    internal.add_argument("--output", required=True)

    excel = subparsers.add_parser("excel-to-internal-app")
    excel.add_argument("--config", required=True)
    excel.add_argument("--output", required=True)

    delivery = subparsers.add_parser("delivery-pipeline")
    delivery.add_argument("--config", required=True)
    delivery.add_argument("--output", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv == ["--version"]:
        print(f"ai-automation-kit {__version__}")
        return 0
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "research-agent":
        run = run_research_agent(config_path=args.config, output_dir=args.output)
        print(f"run_id={run.run_id}")
        print(f"status={run.status}")
        print(f"report={args.output}/report.md")
        return 0 if run.status == "succeeded" else 1
    if args.command == "github-discover":
        output = Path(args.output)
        output.mkdir(parents=True, exist_ok=True)
        config_path = output / "github_discover_config.json"
        config = _build_github_discover_config(
            business_area=args.business_area,
            query=args.query,
            limit=args.limit,
            include_readme=args.include_readme,
        )
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        run = run_research_agent(config_path=config_path, output_dir=output)
        print(f"run_id={run.run_id}")
        print(f"status={run.status}")
        print(f"report={output}/report.md")
        print(f"candidates={output}/github_candidates.md")
        print(f"business_plan={output}/business_automation_plan.md")
        return 0 if run.status == "succeeded" else 1
    if args.command == "docs-rag":
        run = run_docs_rag(config_path=args.config, output_dir=args.output)
        print(f"run_id={run.run_id}")
        print(f"status={run.status}")
        print(f"answer={args.output}/answer.md")
        return 0 if run.status == "succeeded" else 1
    if args.command == "internal-ai-workflow":
        run = run_internal_ai_workflow(config_path=args.config, output_dir=args.output)
        print(f"run_id={run.run_id}")
        print(f"status={run.status}")
        print(f"draft={args.output}/draft_reply.md")
        return 0 if run.status == "succeeded" else 1
    if args.command == "excel-to-internal-app":
        run = run_excel_to_internal_app(config_path=args.config, output_dir=args.output)
        print(f"run_id={run.run_id}")
        print(f"status={run.status}")
        print(f"schema={args.output}/schema.sql")
        return 0 if run.status == "succeeded" else 1
    if args.command == "delivery-pipeline":
        run = run_delivery_pipeline(config_path=args.config, output_dir=args.output)
        print(f"run_id={run.run_id}")
        print(f"status={run.status}")
        print(f"checklist={args.output}/docs/delivery-checklist.md")
        return 0 if run.status == "succeeded" else 1
    return 0


def _build_github_discover_config(
    business_area: str,
    query: str | None,
    limit: int,
    include_readme: bool,
) -> dict:
    safe_limit = max(1, min(25, limit))
    search_queries = [query] if query else _default_business_queries(business_area)
    return {
        "topic": f"GitHub discovery for {business_area} automation",
        "business_context": {"business_area": business_area},
        "github_searches": [
            {
                "query": search_query,
                "sort": "stars",
                "order": "desc",
                "per_page": safe_limit,
            }
            for search_query in search_queries
        ],
        "include_readme": include_readme,
    }


def _default_business_queries(business_area: str) -> list[str]:
    terms = {
        "sales": ["sales automation crm stars:>100", "crm workflow automation stars:>100", "lead generation automation stars:>100"],
        "support": ["customer support helpdesk stars:>100", "support chatbot automation stars:>100", "ticket automation ai stars:>100"],
        "finance": ["invoice accounting finance automation stars:>100", "expense report automation stars:>100", "spreadsheet finance automation stars:>100"],
        "operations": ["workflow automation orchestration stars:>100", "business process automation stars:>100", "agent orchestration automation stars:>100"],
        "marketing": ["marketing automation content stars:>100", "seo content automation stars:>100", "email campaign automation stars:>100"],
        "hr": ["recruiting onboarding hr automation stars:>100", "resume screening automation stars:>100", "employee onboarding automation stars:>100"],
    }
    return terms.get(business_area, [f"{business_area} automation stars:>100", f"{business_area} ai-agent stars:>100"])


if __name__ == "__main__":
    raise SystemExit(main())
