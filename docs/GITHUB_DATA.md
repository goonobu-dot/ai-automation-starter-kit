# GitHub Data Inputs

`research-agent` can use GitHub public data in two ways.

## Known Repositories

Use `github_repositories` when you already know the repositories you want to evaluate.

```json
{
  "topic": "GitHub repo research",
  "github_repositories": ["octocat/Hello-World"]
}
```

Output:

- `report.md`, `report.html`, and `report.json`
- `github_repositories.json`
- run records under `runs/`

## Repository Search

Use `github_searches` when you want GitHub to find candidate repositories by topic, stars, language, or other search qualifiers.

```json
{
  "topic": "High-star GitHub repositories for AI automation ideas",
  "github_searches": [
    {
      "query": "topic:ai-agents stars:>1000",
      "sort": "stars",
      "order": "desc",
      "per_page": 5
    }
  ],
  "include_readme": false
}
```

Output:

- `run_summary.json`
- `run_summary.md`
- `value_realization_plan.json`
- `value_realization_plan.md`
- `value_measurement_report.json`
- `value_measurement_report.md`
- `stakeholder_rollout_map.json`
- `stakeholder_rollout_map.md`
- `risk_exception_register.json`
- `risk_exception_register.md`
- `operational_audit_plan.json`
- `operational_audit_plan.md`
- `enterprise_readiness.json`
- `enterprise_readiness.md`
- `report.md`, `report.html`, and `report.json`
- `github_searches.json`
- `github_candidates.json`
- `github_candidates.csv`
- `github_candidates.md`
- `adoption_shortlist.json`
- `adoption_shortlist.md`
- `manual_review_pack.json` when candidates exist but none pass the adapter gate
- `manual_review_pack.md` when candidates exist but none pass the adapter gate
- `adapter_blueprint.json`
- `adapter_blueprint.md`
- `adapter_starter/README.md`
- `adapter_starter/adapter.py`
- `adapter_starter/smoke_test.py`
- `adapter_starter/sample_input.json`
- `candidate_briefs/<owner>__<repo>.md`
- run records under `runs/`

Supported repository search sort values are `stars`, `forks`, `help-wanted-issues`, and `updated`.

## Candidate Ranking

Every GitHub repository collected through `github_repositories` or `github_searches` is scored into a reusable candidate ranking.

The score uses:

- stars and forks for adoption signal
- `updated_at` for activity signal
- license type for reuse risk
- language and topics for operability signal
- open issue volume as a lightweight maintenance risk

The output labels each repository as:

- `strong`: good first candidate for adapter or workflow extraction
- `review`: useful, but inspect README, examples, license, and issues first
- `avoid`: keep as reference unless manual review changes the risk picture

The output also assigns a production gate:

- `ready_for_adapter`: low license risk plus strong automation fit
- `manual_review_required`: useful candidate, but inspect manually before prototyping
- `blocked_until_license_review`: do not reuse until license review clears it
- `reference_only`: keep as an idea source, not an implementation candidate

Use `run_summary.md` first for the shortest status and next file to read. Use `value_realization_plan.md` before assigning implementation work; it states the KPI hypothesis, current-process baseline, dry-run measurement, 90-day rollout, and go/no-go evidence needed to justify adoption. Use `value_measurement_report.md` to define baseline fields, pilot measurements, metric targets, and continuation thresholds. Use `stakeholder_rollout_map.md` to assign executive sponsor, process owner, operator, reviewer, security owner, and legal owner responsibilities before the pilot starts. Use `risk_exception_register.md` to track unresolved risks, owners, required evidence, and stop conditions. Use `operational_audit_plan.md` to define post-pilot audit scope, sampling cadence, required evidence, and stop triggers. Use `enterprise_readiness.md` before production planning; it keeps release blocked until license review, dry-run, approval, audit log, and secret review controls are complete. Use `adoption_shortlist.md` for the safest first candidates. Use `manual_review_pack.md` when no repository is safe enough for immediate adapter prototyping. Use `candidate_briefs/` when assigning one repository to an engineer or agent for deeper review.

Each candidate brief also includes:

- adoption decision such as `prototype`, `manual_review`, `legal_review`, or `reference`
- adoption effort
- deployment shape such as `python_adapter`, `node_adapter`, or `service_wrapper`
- a 30-day implementation plan
- a risk register for license, maintenance, issue volume, and unsafe rollout risks

When a ready candidate exists, `adapter_blueprint.md` turns the top shortlist project into an adapter-only implementation contract. It defines expected inputs, outputs, required controls, blocked actions, and acceptance criteria so an engineer or agent can start a safe prototype without guessing the production boundary.

The generated `adapter_starter/` folder then provides a runnable Python dry-run skeleton:

- `adapter.py`: adapter contract implementation with no external side effects
- `sample_input.json`: synthetic payload for the selected business area
- `smoke_test.py`: local smoke test for the adapter contract
- `README.md`: promotion rules and usage notes

If repository search returns no candidates, the run writes `query_recovery.md`, `query_recovery.json`, `value_realization_plan.md`, `value_measurement_report.md`, `stakeholder_rollout_map.md`, `risk_exception_register.md`, and `operational_audit_plan.md`. Those files list the empty queries, safer fallback searches for the selected business area, next actions for broadening the search, the measurable recovery target for candidate quality, the owner for the next discovery batch, the stop condition that blocks implementation until a candidate exists, and the audit trace required for recovery.

## README Download

Set `include_readme` to `true` when you want the kit to download README files for collected repositories:

```json
{
  "topic": "GitHub repo research with READMEs",
  "github_repositories": ["octocat/Hello-World"],
  "include_readme": true
}
```

Output:

- `github_readmes.json`
- `github_readmes/<owner>__<repo>.md`

README failures are logged in `failed_fetches.json` without dropping the repository from the candidate ranking.

## Authentication

Public unauthenticated requests work, but they have lower limits. Set `GITHUB_TOKEN` for higher limits:

```bash
export GITHUB_TOKEN=your_token_here
ai-automation-kit research-agent --config examples/research-agent/github_search.json --output .tmp/github-search-demo
```

Do not commit `.env` files or tokens. This project ignores `.env` and `.env.*` while allowing `.env.example`.

## References

- GitHub REST Search API: https://docs.github.com/en/rest/search/search
- GitHub REST Repositories API: https://docs.github.com/rest/repos/repos
- GitHub REST API rate limits: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
