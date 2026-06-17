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

- `report.md`, `report.html`, and `report.json`
- `github_searches.json`
- `github_candidates.json`
- `github_candidates.csv`
- `github_candidates.md`
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
