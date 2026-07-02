from __future__ import annotations

import json
from pathlib import Path


ARTIFACTS = [
    "README.md",
    "service_catalog.md",
    "client_discovery_questions.md",
    "proposal.md",
    "statement_of_work.md",
    "pricing_model.md",
    "demo_script.md",
    "outreach_messages.md",
    "delivery_checklist.md",
    "risk_boundaries.md",
    "offer_pack.json",
]


def generate_offer_pack(source_output: Path, output: Path, business_area: str, client_type: str) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    source_summary = _load_source_summary(source_output)
    payload = {
        "business_area": business_area,
        "client_type": client_type,
        "source_output": str(source_output),
        "source_status": "ready" if source_output.exists() else "missing",
        "source_summary": source_summary,
        "artifacts": ARTIFACTS,
        "positioning": _positioning(business_area, client_type),
    }
    renderers = {
        "README.md": _render_readme,
        "service_catalog.md": _render_service_catalog,
        "client_discovery_questions.md": _render_discovery_questions,
        "proposal.md": _render_proposal,
        "statement_of_work.md": _render_statement_of_work,
        "pricing_model.md": _render_pricing_model,
        "demo_script.md": _render_demo_script,
        "outreach_messages.md": _render_outreach_messages,
        "delivery_checklist.md": _render_delivery_checklist,
        "risk_boundaries.md": _render_risk_boundaries,
    }
    for filename, renderer in renderers.items():
        (output / filename).write_text(renderer(payload), encoding="utf-8")
    (output / "offer_pack.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def _load_source_summary(source_output: Path) -> dict:
    if not source_output.exists():
        return {
            "executive_recommendation": "Run discovery or use this starter pack to scope a first automation pilot.",
            "recommended_projects": [],
        }
    for name in ["business_automation_summary.json", "onboarding_summary.json", "run_summary.json"]:
        path = source_output / name
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                continue
    return {
        "executive_recommendation": "Discovery artifacts were found, but no structured summary was available.",
        "recommended_projects": [],
    }


def _positioning(business_area: str, client_type: str) -> str:
    return (
        f"A practical {business_area} automation pilot for a {client_type} client, "
        "delivered as a small paid discovery-to-prototype engagement with human approval and measurable outcomes."
    )


def _recommendation(payload: dict) -> str:
    summary = payload["source_summary"]
    return summary.get("executive_recommendation") or summary.get("status") or "Start with one low-risk automation pilot."


def _project_lines(payload: dict) -> list[str]:
    projects = payload["source_summary"].get("recommended_projects") or []
    if not projects:
        return ["- 参考にできるOSS候補はまだ確定していません。ヒアリング結果とお客様のデータに合わせて、安全に試せる範囲から選定します。"]
    lines = []
    for project in projects[:5]:
        name = project.get("full_name", "unnamed project")
        url = project.get("url", "")
        lines.append(f"- {name}: {url or 'URLは調査出力フォルダを確認してください'}")
    return lines


def _render_readme(payload: dict) -> str:
    lines = [
        f"# 提案パック（Offer Pack）: {payload['business_area']} 自動化",
        "",
        payload["positioning"],
        "",
        f"このパックは、{payload['client_type']} のお客様へ {payload['business_area']} 領域の小さな自動化PoC（お試し導入）を提案するための一式です。収益を保証するものではありません（No income is guaranteed）。",
        "",
        "## 使う順番",
        "",
        "1. `service_catalog.md` で売れる形のメニューを選びます。",
        "2. `client_discovery_questions.md` を持って最初の面談に行きます。",
        "3. `proposal.md` と `statement_of_work.md` を面談内容に合わせて埋めて送ります。",
        "4. `pricing_model.md` で無理のない価格を決めます。",
        "5. お客様のデータに触れる前に `risk_boundaries.md` を確認します。",
        "",
        "## 調査からの推奨事項",
        "",
        _recommendation(payload),
        "",
    ]
    return "\n".join(lines)


def _render_service_catalog(payload: dict) -> str:
    area = payload["business_area"]
    lines = [
        f"# サービスカタログ: {area} 自動化",
        "",
        "小さな有料メニューとして売ってください。最初の案件は「数か月」ではなく「数日」で納品できる範囲に絞るのが鉄則です。",
        "",
        "| メニュー | お客様の困りごと | 納品物 | 相場の目安 |",
        "|---|---|---|---|",
        f"| {area} 業務ヒアリング＋自動化診断 | 何から自動化すべきか分からない | 業務フロー図、リスク一覧、30日パイロット計画 | 無料〜1万円（固定額） |",
        f"| {area} dry-runお試し導入（初回PoC） | 本格導入の前に効果の証拠がほしい | ローカルdry-run一式、デモ台本、効果スコアカード | 5〜15万円（固定額） |",
        f"| {area} 本格導入・本番連携 | お試しの効果を実業務につなげたい | 連携設計、承認ルール、切り戻し手順 | 15〜50万円（固定額） |",
        "| 月次運用サポート | 導入した自動化を安定して回したい | 実行結果の確認、小修正、月次レポート | 1〜3万円/月 |",
        "",
        "## 参考OSS候補",
        "",
    ]
    lines.extend(_project_lines(payload))
    lines.append("")
    return "\n".join(lines)


def _render_discovery_questions(payload: dict) -> str:
    area = payload["business_area"]
    lines = [
        f"# ヒアリング質問リスト: {area} 自動化",
        "",
        "面談でそのまま読み上げてください。★印は必ず確認します。",
        "",
        "## 業務の成果と痛み",
        "",
        f"1. ★「{area} まわりの業務で、毎週いちばん人の時間を使っている作業は何ですか？」",
        "2. 「その作業が遅れたり、抜けたり、間違ったりすると、何が起きますか？」",
        "3. ★「自動化が役に立ったと言えるのは、どの数字がどうなったときですか？」",
        "",
        "## 現在の業務フロー",
        "",
        "4. 「今はどのツール（メール・Excel・会計ソフトなど）を使っていますか？」",
        "5. 「その業務はどこから始まり、どこで終わりますか？」",
        "6. ★「途中で必ず人の確認（承認）が要るのはどのステップですか？」",
        "7. 「社外に出せないデータ、法律上の制約があるデータはどれですか？」",
        "",
        "## お試し導入の条件",
        "",
        "8. ★「最初はサンプルデータ（または名前を伏せたコピー）だけで試せますか？」",
        "9. 「dry-run（本番送信しないお試し実行）の結果を、本番に進める前に誰が確認しますか？」",
        "10. 「品質が足りなかった場合の中止条件を決めておきませんか？」",
        "",
    ]
    return "\n".join(lines)


def _render_proposal(payload: dict) -> str:
    area = payload["business_area"]
    client_type = payload["client_type"]
    lines = [
        f"# ご提案書: {area} 業務自動化のお試し導入（PoC）",
        "",
        "＿＿＿＿＿＿株式会社",
        "＿＿＿＿部 ＿＿＿＿様",
        "",
        f"（想定顧客タイプ: `{client_type}`）",
        "",
        "ご提案者: ＿＿＿＿（連絡先: ＿＿＿＿）",
        "提出日: ＿＿＿＿年＿＿月＿＿日",
        "",
        "## 1. 要約",
        "",
        _recommendation(payload),
        "",
        f"本提案は、{area} 領域の繰り返し業務1件を対象に、小さく管理されたお試し導入（PoC）から始めるものです。目的は、手作業の削減効果を数字で確かめることと、承認・データ取り扱い・切り戻しのルールを明確にしたまま進めることです。",
        "",
        "## 2. 課題の仮説（ヒアリングに基づき修正します）",
        "",
        f"- {area} の定型業務が担当者様の手作業に依存しており、対応の遅れや確認漏れが発生している。",
        "- 業務の進捗が本人以外から見えず、引き継ぎや繁忙期の応援が難しい。",
        "- 過去に大きなシステム導入を検討したが、費用とリスクが大きく見送った。",
        "",
        "## 3. ご提案の進め方",
        "",
        f"1. 対象業務を1つ選定し、{area} 業務フローを見える化します。",
        "2. リスクが最も低いステップを自動化候補にします。",
        "3. サンプルデータでdry-run（本番送信しないお試し実行）の試作を作ります。",
        "4. 効果スコアカードで結果を測定します。",
        "5. 「本格導入・修正・中止」を貴社にご判断いただきます。",
        "",
        "## 4. 費用とスケジュール",
        "",
        "- 初回PoC: ＿＿万円（税別）※ 相場目安 5〜15万円",
        "- 期間: 3〜5営業日（ヒアリング確定からご報告まで）",
        "- 効果確認後の月次運用サポート（任意）: 月額＿＿万円（税別）※ 相場目安 1〜3万円",
        "",
        "## 5. 参考OSSシグナル",
        "",
    ]
    lines.extend(_project_lines(payload))
    lines.extend(
        [
            "",
            "## 6. 成果の測り方",
            "",
            "- 手作業の受け渡し回数が減ること。",
            "- 1件あたりの処理時間が短くなること。",
            "- ミス率が下がる、または悪化しないこと。",
            "- 人の承認ポイントが業務の中で見えること。",
            "- 引き継ぎ後、貴社担当者様が自分の言葉で業務フローを説明できること。",
            "",
            "## 7. 免責",
            "",
            "- 本PoCは効果検証を目的とし、特定の削減額・売上・成果を保証するものではありません。",
            "- 実際の顧客への送信、本番データの変更、金銭の移動は本PoCに含まれません。",
            "- お預かりしたデータは本件の目的以外に使用せず、終了後は指示に従い削除します。",
            "",
        ]
    )
    return "\n".join(lines)


def _render_statement_of_work(payload: dict) -> str:
    area = payload["business_area"]
    lines = [
        f"# 作業範囲記述書（SOW）: {area} 自動化PoC",
        "",
        "## 納品物",
        "",
        "- 業務フロー図と自動化候補の整理メモ。",
        "- dry-run試作（またはアダプター計画書）。",
        "- 効果スコアカードと測定メモ。",
        "- 納品チェックリストと引き継ぎメモ。",
        "- リスク境界書（何を自動化しないかの明文化）。",
        "",
        "## 範囲外（Out of Scope）",
        "",
        "- 書面の承認なしでの本番システム・実データへのアクセス。",
        "- 法律・税務・人事・医療・金融に関する専門的判断。",
        "- 承認されたお客様環境の外での秘密情報（APIキー等）の取り扱い。",
        "- 売上・削減額・リード獲得数の保証。",
        "",
        "## 検収条件",
        "",
        "- 試作がサンプルデータ（または承認済みのエクスポートデータ)で動作すること。",
        "- お客様が入力・出力・失敗ケースを確認できること。",
        "- 本番利用の前に人の承認ステップが定義されていること。",
        "- 未解決リスクが、担当者と中止条件つきで一覧化されていること。",
        "",
        "## 支払条件",
        "",
        "- 請求書発行後＿＿日以内の銀行振込。",
        "- PoC費用は成果報酬ではなく固定額です。中止判断となった場合も、実施済み作業分は請求対象です。",
        "",
    ]
    return "\n".join(lines)


def _render_pricing_model(payload: dict) -> str:
    lines = [
        "# 価格モデル",
        "",
        "収益を保証するものではありません（No income is guaranteed）。価格はお客様の緊急度・範囲・リスク・あなたの提供能力で決まります。以下は日本国内の副業・個人受託の相場観です。",
        "",
        "| パッケージ | 典型的な範囲 | 相場の目安 |",
        "|---|---|---|",
        "| 業務ヒアリング＋自動化診断 | 面談、業務フロー図、パイロット提案 | 無料〜1万円（固定額） |",
        "| dry-runお試し導入（初回PoC） | 業務1件、サンプルデータ、デモ、スコアカード | 5〜15万円（固定額） |",
        "| 本格導入・本番引き渡し | 承認ゲート、文書化、デプロイチェックリスト | 15〜50万円（PoC後の固定額） |",
        "| 月次運用サポート | 監視、小修正、月次レポート、改善提案 | 1〜3万円/月 |",
        "",
        "## 価格の決め方",
        "",
        "1. 月の削減時間 × 時給換算（2,500〜4,000円）で「月あたりの価値」を出します。",
        "2. 初回PoCは価値の1〜2か月分に設定します（例: 月3万円の価値なら5〜6万円）。",
        "3. 月次サポートは価値の3割以下に抑えます（超えると解約されます）。",
        "",
        "## 価格のルール",
        "",
        "- 実装を約束する前に、診断（ヒアリング）に対して対価をもらうこと。",
        "- 最初の有料パイロットは範囲を狭く保つこと。",
        "- 初期費用と月額サポートを必ず分けること。",
        "- アクセス権・データ形式・承認者が不明なまま、リスクの高い連携に値付けしないこと。",
        "",
    ]
    return "\n".join(lines)


def _render_demo_script(payload: dict) -> str:
    lines = [
        "# デモ台本",
        "",
        "1. 現在の手作業の流れを一文で説明します（「今は◯◯を人が1件ずつ確認していますよね」）。",
        "2. サンプルデータ（または承認済みエクスポート）を見せます。",
        "3. dry-run自動化を実行します。",
        "4. 生成された下書きと、人の承認ポイントを見せます。",
        "5. 効果スコアカードを開き、成功をどう測るか説明します。",
        "6. 「まだ意図的に自動化していないこと」を説明します（信頼につながります）。",
        "",
        "締めの一言: 「このdry-runの結果が役立ちそうでしたら、次のステップは承認と監視をつけた小さな有料パイロットです。」",
        "",
    ]
    return "\n".join(lines)


def _render_outreach_messages(payload: dict) -> str:
    area = payload["business_area"]
    lines = [
        "# 営業メッセージ文例",
        "",
        "## 短いDM",
        "",
        f"「はじめまして。{area} まわりの繰り返し業務を、小さく測定できる自動化のお試し導入（5〜15万円・約1週間）に変えるお手伝いをしています。本格導入の前に、業務フロー診断とdry-run試作で価値とリスクを確認できる進め方です。毎週繰り返している業務を1つ、見える化してみませんか？」",
        "",
        "## メール",
        "",
        f"件名: {area} 業務の小さな自動化お試し導入のご案内",
        "",
        f"「突然のご連絡失礼します。{area} の定型業務について、リスクの大きい一括自動化ではなく、業務フロー図 → dry-run試作 → 効果スコアカード、という小さな段階で進めるお試し導入をご提供しています。効果が数字で見えてから、続けるかどうかをご判断いただけます。」",
        "",
        "「ご興味があれば、繰り返し業務を1つ拝見して、短いパイロット計画（費用目安つき）をお送りします。30分のオンライン面談はいかがでしょうか。」",
        "",
        "## SNS投稿",
        "",
        f"「{area} の実務向け自動化サービスを試験提供中: 業務診断 → dry-run試作 → 効果スコアカード → 安全な引き渡し。検証していないスクリプトに社内システムを渡さずに、測定できる自動化を試したい会社さん向けです。」",
        "",
    ]
    return "\n".join(lines)


def _render_delivery_checklist(payload: dict) -> str:
    lines = [
        "# 納品チェックリスト",
        "",
        "- [ ] お客様側の業務責任者が決まっている。",
        "- [ ] 入力データの提供元が承認されている。",
        "- [ ] dry-run用に機微なデータ（個人情報等）を除去・マスキングした。",
        "- [ ] 試作に人の承認ステップが入っている。",
        "- [ ] 効果スコアカードに基準値と目標値が入っている。",
        "- [ ] 失敗ケースを文書化した。",
        "- [ ] 切り戻し（中止）条件を文書化した。",
        "- [ ] 提案書・SOW・デモ台本・リスク境界書をお客様に渡した。",
        "- [ ] 請求書を発行した（金額・支払期日・振込先を明記）。",
        "",
    ]
    return "\n".join(lines)


def _render_risk_boundaries(payload: dict) -> str:
    lines = [
        "# リスク境界書",
        "",
        "この提案パックは、範囲を限定した業務自動化パイロットのためのものです。収益・リード獲得・法令適合・本番の安全性を約束するものではありません。",
        "",
        "## 必ず守る境界",
        "",
        "- 最初はサンプルデータ、または承認済みのエクスポートデータだけを使う。",
        "- 外部へのメッセージ送信、支払い、アカウント変更、顧客に影響する操作の前には、必ず人の承認（human approval）を挟む。",
        "- 生成ファイルに秘密情報（APIキー・パスワード）を保存しない。",
        "- ライセンス確認の前に、第三者OSSのコードをお客様のシステムへコピーしない。",
        "- 法規制のある判断（法務・医療・金融・人事）を、有資格者の確認なしで自動化しない。",
        "- 引き渡し後の監視・保守の担当者を文書で決める。",
        "",
        "## 人の承認について",
        "",
        "最初のパイロットでは、本番利用の前に必ず人の承認を残してください。承認は「チャットで了解をもらった」ではなく、業務フローの中で見える形（承認キュー・承認記録）にします。",
        "",
    ]
    return "\n".join(lines)
