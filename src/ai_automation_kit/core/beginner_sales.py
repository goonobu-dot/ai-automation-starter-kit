from __future__ import annotations

import csv
import html
import io
import json
from pathlib import Path

from ai_automation_kit.core.flows import get_flow
from ai_automation_kit.core.flows import list_flows


ARTIFACTS = [
    "README.md",
    "START_HERE_FOR_SIDE_BUSINESS.md",
    "flow_gallery.html",
    "selected_flow_demo.html",
    "proposal_one_pager.md",
    "beginner_pitch_script.md",
    "client_questions.md",
    "roi_simple_calculator.csv",
    "three_day_poc_plan.md",
    "price_menu.md",
    "outreach_messages.md",
    "objection_handling.md",
    "demo_walkthrough.md",
    "client_delivery_checklist.md",
    "positioning.md",
    "differentiation_matrix.md",
    "beginner_sales.json",
]


def generate_beginner_sales_pack(
    flow_id: str | None,
    output: Path,
    client_type: str,
    niche: str,
    industry: str = "operations",
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    selected_flow = _select_flow(flow_id=flow_id, industry=industry)
    gallery_flows = _gallery_flows(selected_flow["industry"])
    payload = {
        "client_type": client_type,
        "niche": niche,
        "industry": selected_flow["industry"],
        "flow": selected_flow,
        "gallery_count": len(gallery_flows),
        "artifacts": ARTIFACTS,
        "beginner_score": _score_beginner_pack(selected_flow, gallery_flows),
        "research_positioning": _research_positioning(),
    }
    renderers = {
        "README.md": _render_readme,
        "START_HERE_FOR_SIDE_BUSINESS.md": _render_start_here,
        "proposal_one_pager.md": _render_proposal,
        "beginner_pitch_script.md": _render_pitch_script,
        "client_questions.md": _render_client_questions,
        "three_day_poc_plan.md": _render_three_day_poc,
        "price_menu.md": _render_price_menu,
        "outreach_messages.md": _render_outreach_messages,
        "objection_handling.md": _render_objection_handling,
        "demo_walkthrough.md": _render_demo_walkthrough,
        "client_delivery_checklist.md": _render_delivery_checklist,
        "positioning.md": _render_positioning,
        "differentiation_matrix.md": _render_differentiation_matrix,
    }
    for filename, renderer in renderers.items():
        (output / filename).write_text(renderer(payload), encoding="utf-8")
    (output / "flow_gallery.html").write_text(_render_flow_gallery(payload, gallery_flows), encoding="utf-8")
    (output / "selected_flow_demo.html").write_text(_render_selected_flow_demo(payload), encoding="utf-8")
    (output / "roi_simple_calculator.csv").write_text(_render_roi_csv(payload), encoding="utf-8")
    (output / "beginner_sales.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def _select_flow(flow_id: str | None, industry: str) -> dict:
    if flow_id:
        return get_flow(flow_id)
    candidates = list_flows(industry=industry)
    if not candidates:
        candidates = list_flows()
    return get_flow(candidates[0]["id"])


def _gallery_flows(industry: str) -> list[dict]:
    industry_flows = list_flows(industry=industry)
    seen = {flow["id"] for flow in industry_flows}
    broader_flows = [flow for flow in list_flows() if flow["id"] not in seen]
    return (industry_flows + broader_flows)[:18]


def _score_beginner_pack(flow: dict, gallery_flows: list[dict]) -> dict:
    categories = {
        "visual_flow_gallery": 15 if gallery_flows else 0,
        "selected_demo": 15,
        "client_discovery": 15,
        "proposal_and_pitch": 15,
        "roi_and_pricing": 15,
        "poc_delivery": 15,
        "risk_boundaries": 10,
    }
    return {
        "total": sum(categories.values()),
        "label": "side_business_ready",
        "categories": categories,
        "notes": [
            "No income is guaranteed.",
            "Use this as a beginner operating system for finding, explaining, scoping, and safely piloting automation work.",
            "Production connectors still require client approval, credentials, and data review.",
        ],
    }


def _research_positioning() -> list[str]:
    return [
        "Open-source automation tools are strong at workflow execution and integrations.",
        "Template libraries are strong at fast starts, but often weak at client discovery, pricing, and delivery packaging.",
        "Agent frameworks are strong for developers, but beginners need visible flows, safe local dry-runs, and sales-ready artifacts.",
        "This pack combines workflow selection, client explanation, proposal assets, ROI framing, and approval-first delivery.",
    ]


def _render_readme(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            f"# 副業営業パック: {flow['name']}",
            "",
            f"このパックは、AIエージェントを使い始めたばかりの人が、{payload['niche']} 分野の {payload['client_type']} のお客様へ「{flow['name']}」の自動化を安全に提案・デモ・受注するための一式です。",
            "",
            "収益を保証するものではありません（No income is guaranteed）。最初の商談を、具体的で、安全で、分かりやすくすることが目的です。",
            "",
            "## 使う順番",
            "",
            "1. `START_HERE_FOR_SIDE_BUSINESS.md` を読みます。",
            "2. `flow_gallery.html` で提案する業務フローを確認し、`selected_flow_demo.html` をお客様に見せる画面として使います。",
            "3. `client_questions.md` を持ってヒアリングに行きます（読み上げるだけで使えます）。",
            "4. `roi_simple_calculator.csv` に控えめな数字を入れて効果を見積もります。",
            "5. `price_menu.md` で価格を決め、`proposal_one_pager.md` を仕上げて送ります。",
            "6. 受注したら `three_day_poc_plan.md` と `client_delivery_checklist.md` で納品します。",
            "",
            "## スコア",
            "",
            f"- Total: `{payload['beginner_score']['total']}/100`",
            f"- Label: `{payload['beginner_score']['label']}`",
            "",
            "## このパックの位置づけ",
            "",
        ]
        + [f"- {item}" for item in payload["research_positioning"]]
        + [""]
    )


def _render_start_here(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            "# 副業はここから（START HERE）",
            "",
            "収益を保証するものではありません（No income is guaranteed）。このパックの目的は、「AIで何かできます」という曖昧な話を、金額とスケジュールの入った具体的な提案に変えることです。",
            "",
            "## 最短の道のり",
            "",
            f"1. 提案する業務を1つに絞ります: `{flow['name']}`。",
            "2. お客様に「今この業務をどう回しているか」を聞きます（client_questions.md を読み上げるだけ）。",
            "3. デモ画面（selected_flow_demo.html）を見せて、before/after を説明します。",
            "4. 控えめな数字で削減時間を見積もります（roi_simple_calculator.csv）。",
            "5. 有料の小さなPoC（お試し導入。相場 5〜15万円）を提案します。",
            "6. 外部送信・本番更新の前には、必ずお客様側の承認者の確認を挟みます。",
            "7. 効果が数字で見えたら、月次運用サポート（相場 1〜3万円/月）に切り替えます。",
            "",
            "## 初心者の鉄則",
            "",
            "最初から大きなシステムを売らないでください。売るのは「1つの業務・1つの見えるデモ・1つの承認ポイント・1つの測れる成果」です。",
            "",
        ]
    )


def _render_proposal(payload: dict) -> str:
    flow = payload["flow"]
    metrics = "、".join(flow["success_metrics"])
    return "\n".join(
        [
            f"# ご提案書: {flow['name']} の業務自動化PoC",
            "",
            "＿＿＿＿＿＿株式会社",
            "＿＿＿＿部 ＿＿＿＿様",
            "",
            "ご提案者: ＿＿＿＿（連絡先: ＿＿＿＿）",
            "提出日: ＿＿＿＿年＿＿月＿＿日",
            "",
            "## 1. 現状の課題（ヒアリングに基づく仮説）",
            "",
            f"貴社では、{'、'.join(flow['tools'])} を使った {flow['name']} に相当する業務を、担当者様が手作業で繰り返しておられると伺いました。このため、(1) 対応の遅れ、(2) 進捗が見えないこと、(3) 確認・催促のやり直し作業、が発生していると考えられます。",
            "",
            "※ 認識が異なる場合は、この欄をヒアリング内容に合わせて修正します。",
            "",
            "## 2. ご提案内容（初回PoC）",
            "",
            "PoC（Proof of Concept）とは、本格導入の前に小さく試して効果を確かめる取り組みです。今回は次の範囲で実施します。",
            "",
            "- 対象業務: 上記1件のみ（範囲は追加しません）",
            "- 実施内容: 業務フローの見える化、サンプルデータでの自動下書き生成、作業キュー・承認リスト・効果レポートの作成",
            "- 安全設計: 外部送信や本番データの変更は一切行いません（dry-run方式）。実行はすべて下書きとして出力し、貴社の承認者様が確認します",
            "",
            "## 3. 費用",
            "",
            "- 初回PoC: ＿＿万円（税別）※ 相場目安 5〜15万円。対象業務の件数と複雑さで調整します",
            "- 効果確認後の月次運用サポート（ご希望時）: 月額＿＿万円（税別）※ 相場目安 1〜3万円/月",
            "- PoCの結果、効果が見込めないと判断された場合、月次契約は不要です",
            "",
            "## 4. スケジュール（目安）",
            "",
            "- 1日目: ヒアリング確定・サンプルデータの受領",
            "- 2〜3日目: 業務フロー作成・dry-run実行・デモ準備",
            "- 5日目まで: 結果報告会（30分）。継続・修正・中止をご判断いただきます",
            "",
            "## 5. 成果の測り方",
            "",
            metrics,
            "",
            "## 6. 免責・お約束",
            "",
            "- 本PoCは効果検証が目的であり、特定の削減額・売上を保証するものではありません。",
            "- 貴社データはお預かりした範囲でのみ使用し、第三者へ提供しません。個人情報を含むデータは、可能な限りマスキングした状態でご提供ください。",
            "- 顧客への実際の送信・本番システムの変更・金銭の移動は、本PoCの範囲に含まれません。実施する場合は別途、承認ルールを定めた上でご契約となります。",
            "",
        ]
    )


def _render_pitch_script(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            "# 営業トーク台本（そのまま読めます）",
            "",
            "## 30秒版（立ち話・電話）",
            "",
            f"「{payload['niche']} の会社さん向けに、毎週繰り返している事務作業をAIで下書き化する、小さなお試し導入をやっています。たとえば {flow['name']} のような業務です。いきなりシステムを入れるのではなく、まず5万円くらいの1週間のお試しで、どれくらい時間が浮くかを数字でお見せします。御社で、毎週誰かが手作業で繰り返している業務はありますか？」",
            "",
            "## 2分版（面談の冒頭）",
            "",
            "「最初に安心していただきたいのですが、今日は大きなシステムの売り込みではありません。私がやっているのは、(1) 御社の繰り返し業務を1つだけ選ぶ、(2) その業務をAIが下書きまでやる形をお見せする、(3) 効果を数字で確認してから続けるか決めていただく、という小さな進め方です。」",
            "",
            "「安全面もシンプルです。お試し期間中、AIはメールを送ったり、データを書き換えたりしません。すべて下書きと確認リストを作るだけで、実行するかどうかは御社の担当者さんが決めます。」",
            "",
            f"「今日は例として {flow['name']} のデモをお持ちしました。5分だけ画面をご覧いただけますか？」",
            "",
        ]
    )


def _render_client_questions(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            f"# ヒアリングシート: {flow['name']}",
            "",
            "そのまま順番に読み上げてください。すべて聞けなくても、★印だけは必ず確認します。",
            "",
            "## 業務の実態",
            "",
            "1. ★「この業務は、月に何回くらい発生しますか？」",
            "2. ★「1件あたり、何分くらいかかっていますか？」",
            "3. 「作業はどこから始まりますか？ メール、Excel、紙、電話のどれでしょうか？」",
            "4. 「元になるデータは、どのファイルやシステムに入っていますか？」",
            "5. 「一番よく起きる失敗ややり直しは何ですか？」",
            "",
            "## 体制と承認",
            "",
            "6. ★「結果を最終確認する方はどなたですか？ その方の確認なしで外に出るものはありますか？」",
            "7. 「社外に出してはいけないデータ（個人情報・取引条件など）はどれですか？」",
            "",
            "## お試し導入の条件",
            "",
            "8. ★「1週間のお試しで『これは役に立つ』と言えるのは、何がどうなったときですか？」",
            "9. 「サンプルデータ（実データのコピーでも、名前を伏せたものでも構いません）をご用意いただけますか？」",
            "10. 「もしお試しの結果が良ければ、月々の運用まで任せたいと思われますか？ それとも社内で回したいですか？」",
            "",
        ]
    )


def _render_roi_csv(payload: dict) -> str:
    rows = [
        ["field", "example_value", "notes"],
        ["monthly_items", "80", "この業務が月に発生する回数。"],
        ["minutes_per_item_before", "8", "現在の1件あたりの手作業時間（分）。"],
        ["minutes_per_item_after", "3", "自動化支援後の控えめな見積り（分）。"],
        ["loaded_hourly_cost", "3000", "時給換算コスト（円）。お客様側の人件費で見積もる。例: 2500〜4000円。"],
        ["monthly_tool_cost", "3000", "ホスティングやSaaS等の月額コスト見積り（円）。"],
        ["estimated_hours_saved", "=(monthly_items*(minutes_per_item_before-minutes_per_item_after))/60", "月あたり削減時間の計算式。"],
        ["estimated_monthly_value", "=estimated_hours_saved*loaded_hourly_cost-monthly_tool_cost", "月あたり価値の見積り。保証値ではない。"],
        ["pilot_fee_floor", "=estimated_monthly_value*1.5", "初回PoC費用の目安（価値の1〜2か月分。相場5〜15万円）。"],
        ["monthly_maintenance_floor", "=estimated_monthly_value*0.25", "月次運用費の目安（価値の3割以下。相場1〜3万円）。"],
    ]
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerows(rows)
    return buffer.getvalue()


def _render_three_day_poc(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            f"# 3日間PoC計画: {flow['name']}",
            "",
            "PoC（お試し導入）は3営業日で完了させます。だらだら延ばさないことが、お互いの信頼につながります。",
            "",
            "## 1日目: 準備",
            "",
            "- ヒアリング内容（対象業務・承認者・成功条件）を文章にして、お客様に確認してもらいます。",
            "- サンプルデータ（マスキング済み）を受け取ります。",
            "- before/after の業務フロー図を作ります。",
            "",
            "## 2日目: dry-run構築",
            "",
            "- `ai-automation-kit flows install` で対象フローを導入します。",
            "- サンプルデータで実行し、作業キュー・下書き・承認リスト・レポートを生成します。",
            "- お客様に見せる画面（demo）を整えます。",
            "",
            "## 3日目: 報告と判断",
            "",
            "- 30分の報告会。生成物と削減時間の見積りを見せます。",
            "- ROI計算表と実測を比べます。",
            "- 「継続（月次運用へ）・修正（もう1周）・中止」をお客様に決めてもらいます。",
            "- 継続の場合、本番連携と月次運用は別見積り・別契約にします。",
            "",
        ]
    )


def _render_price_menu(payload: dict) -> str:
    return "\n".join(
        [
            "# 料金メニューと価格の決め方",
            "",
            "収益を保証するものではありません（No income is guaranteed）。以下は日本国内の副業・個人受託でよく使われる相場観です。地域・業種・あなたの実績に合わせて調整してください。",
            "",
            "| メニュー | 内容 | 相場の目安 | 売りどき |",
            "|---|---|---|---|",
            "| 業務ヒアリング＋自動化診断 | ヒアリング、業務フロー図、効果見積り、リスクメモ | 無料〜1万円 | 興味はあるが半信半疑のお客様 |",
            "| 初回PoC（お試し導入） | dry-runデモ、サンプルデータ実行、承認リスト、効果レポート | 5〜15万円 | 繰り返し業務が1つ特定できたとき |",
            "| 本格導入（本番連携） | 実データ接続の設計、承認ルール整備、切り戻し手順 | 15〜50万円 | PoCで効果が数字で見えたあと |",
            "| 月次運用サポート | 実行結果の確認、小さな修正、月次レポート、改善提案 | 1〜3万円/月 | お客様が業務として頼るようになったとき |",
            "",
            "## 価格の決め方（3ステップ）",
            "",
            "1. **削減価値から出発する**: 月の削減時間 × お客様側の時給換算（例: 2,500〜4,000円）で「月あたりの価値」を出します。",
            "2. **PoCは価値の1〜2か月分**: 例えば月3万円の価値が見込めるなら、PoCは5〜6万円が説明しやすい水準です。",
            "3. **月次は価値の3割以下**: 月次運用費が削減価値を超えると解約されます。価値3万円なら月1万円程度が長続きします。",
            "",
            "## やってはいけない値付け",
            "",
            "- 「成果報酬で削減額の◯％」: 測定でもめます。固定額にしてください。",
            "- 相場を大きく下回る無料奉仕の継続: 承認や責任の線引きが曖昧になり、事故のもとです。",
            "- 本番連携費用をPoCに含める: PoCで中止できる自由を残すことが、受注率をむしろ上げます。",
            "",
        ]
    )


def _render_outreach_messages(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            "# 営業メッセージ文例",
            "",
            "## 短いDM・紹介依頼（そのまま送れます）",
            "",
            f"「はじめまして。{payload['niche']} の会社様向けに、毎週繰り返している事務作業（例: {flow['name']}）をAIで下書き化する小さなお試し導入（5〜15万円・1週間）を行っています。御社で毎週手作業で繰り返している業務が1つでもあれば、無料の30分ヒアリングで効果の見込みをお伝えできます。ご興味ありませんか？」",
            "",
            "## フォローアップ（返信が来たら）",
            "",
            "「ありがとうございます。最初のステップは小さくて、(1) 30分のヒアリング、(2) 業務フロー図と削減時間の見積り、(3) サンプルデータでのデモ、の3つだけです。本物のメール送信やシステム変更は一切しないので、安心してお試しいただけます。来週、30分だけお時間をいただけますか？」",
            "",
            "## 面談後のお礼メール",
            "",
            "件名: 本日のお礼と、お試し導入のご提案",
            "",
            "「本日はお時間をいただきありがとうございました。お話を伺った◯◯業務について、1週間のお試し導入（◯万円・税別）のご提案書を添付します。内容はデモでご覧いただいた通り、サンプルデータでの下書き生成と効果測定までで、実際の送信やデータ変更は含みません。ご不明点があればお気軽にご連絡ください。」",
            "",
        ]
    )


def _render_objection_handling(payload: dict) -> str:
    return "\n".join(
        [
            "# よくある断り文句への返し方",
            "",
            "## 「もうChatGPTを使っているから」",
            "",
            "「ChatGPTは1回ずつの質問には強いのですが、毎週の繰り返し業務は毎回コピペが必要です。私のお試し導入は、その繰り返しを『作業キュー→下書き→承認→レポート』という流れに固定して、誰がやっても同じ品質になる形にします。」",
            "",
            "## 「データを外に出すのが心配」",
            "",
            "「ごもっともです。お試し期間はマスキングしたサンプルデータだけで動かします。さらにこの仕組みは外部送信を一切しない設計なので、結果はすべて社内で確認する下書きとして出てきます。」",
            "",
            "## 「前に自動化で失敗した」",
            "",
            "「よくあるのは、最初から大きく作りすぎるケースです。今回は業務1つ・承認者1人・指標1つに絞り、1週間で『継続・修正・中止』を決めていただきます。中止しても費用はPoC分だけです。」",
            "",
            "## 「高い」",
            "",
            "「この業務は月◯時間かかっていて、時給換算で月◯万円分です。お試し費用◯万円は約◯か月で回収できる計算です。まず数字を一緒に確認しませんか？」",
            "",
            "## 「何を自動化すればいいか分からない」",
            "",
            "「それが一番多いご相談です。毎週発生していて、入口（メールやExcel）と出口（返信や一覧表）がはっきりしていて、遅れると催促が発生する業務が最有力です。30分のヒアリングで一緒に探せます。」",
            "",
        ]
    )


def _render_demo_walkthrough(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            f"# デモの進め方: {flow['name']}",
            "",
            "1. まず、お客様の現在の手作業の流れを口頭で確認します（「今はこう回していますよね？」）。",
            "2. `selected_flow_demo.html` を開き、各ステップを1つずつ説明します。承認ポイントで必ず止まることを強調します。",
            "3. `ai-automation-kit flows install` で対象フローを入れ、サンプルデータで dry-run を実行します。",
            "4. 生成された作業キュー・下書き・承認リスト・レポートを実際に開いて見せます。",
            "5. 「この下書きの品質なら、御社のデータで1週間試す価値がありそうですか？」と聞きます。",
            "6. 反応が良ければ、その場で `proposal_one_pager.md` の金額とスケジュールを確認します。",
            "",
        ]
    )


def _render_delivery_checklist(payload: dict) -> str:
    return "\n".join(
        [
            "# 納品チェックリスト",
            "",
            "- [ ] 対象業務が1つに絞られている。",
            "- [ ] サンプルデータの提供元（担当者）が決まっている。",
            "- [ ] お客様側の承認者が決まっている。",
            "- [ ] 個人情報・機密データのマスキングを確認した。",
            "- [ ] 効果測定の基準値（現状の件数・時間）を記録した。",
            "- [ ] dry-run の生成物をお客様と一緒に確認した。",
            "- [ ] 「継続・修正・中止」の判断を記録した。",
            "- [ ] 本番連携の範囲と費用を、PoCとは別の見積りにした。",
            "- [ ] 月次運用を売る場合、毎月の作業内容を具体的に列挙した。",
            "- [ ] 請求書を発行した（金額・支払期日・振込先を明記）。",
            "",
        ]
    )


def _render_positioning(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            "# ポジショニング（自分の売り方）",
            "",
            f"想定顧客: {payload['niche']} 分野の {payload['client_type']}（中小企業）。AI導入に興味はあるが、何から始めればよいか分からない会社です。",
            "",
            f"看板商品: `{flow['name']}` のお試し導入（初回PoC 5〜15万円 → 月次運用 1〜3万円/月）。",
            "",
            "約束すること: 繰り返し業務1つを見える化し、AIの下書きで安全に楽にし、効果を数字で示すこと。",
            "",
            "言ってはいけないこと: 収益保証、完全自動化、社員の置き換え、確認なしの本番運用。",
            "",
            "代わりに言うこと: 小さな有料お試し、人間の承認つき、測れる業務、控えめな見積り、効果が出たら月次サポート。",
            "",
        ]
    )


def _render_differentiation_matrix(payload: dict) -> str:
    return "\n".join(
        [
            "# 競合との違い（差別化マトリクス）",
            "",
            "| 分類 | 代表的なツール | 得意なこと | このパックが初心者に足すもの |",
            "|---|---|---|---|",
            "| ビジュアル自動化 | n8n、Activepieces、Make、Zapier | 連携とワークフロー実行 | 顧客ヒアリング、提案書、ROI、dry-runの安全設計、納品チェック |",
            "| AIエージェント基盤 | Dify、Flowise、LangGraph、CrewAI | エージェントロジックの構築 | 非エンジニア向けの営業資産と業務パッケージ化 |",
            "| テンプレート集 | n8nテンプレート集、ワークフローギャラリー | 素早い雛形 | 業種特化の提案、断り文句対応、料金メニュー、PoC計画 |",
            "| 本番スターター | Google agent starter packs、Cloudflare agents | デプロイとインフラ | 本番前の顧客合意づくり |",
            "| チャットAI単体 | ChatGPT、Claude、Codex | 柔軟な推論と下書き | 再現可能なファイル・コマンド・承認記録 |",
            "",
        ]
    )


def _render_flow_gallery(payload: dict, flows: list[dict]) -> str:
    cards = []
    for flow in flows:
        cards.append(
            "\n".join(
                [
                    '<article class="card">',
                    f"<h2>{html.escape(flow['name'])}</h2>",
                    f"<p>{html.escape(flow['summary'])}</p>",
                    f"<dl><dt>Industry</dt><dd>{html.escape(flow['industry'])}</dd><dt>Genre</dt><dd>{html.escape(flow['genre'])}</dd><dt>Flow ID</dt><dd><code>{html.escape(flow['id'])}</code></dd></dl>",
                    "</article>",
                ]
            )
        )
    body = "\n".join(cards)
    return _html_page(
        title="Automation Flow Gallery",
        heading="Automation Flow Gallery",
        intro="Choose a workflow that is easy for a client to understand, demo, and measure.",
        body=f'<section class="grid">{body}</section>',
    )


def _render_selected_flow_demo(payload: dict) -> str:
    flow = payload["flow"]
    steps = []
    for index, step in enumerate(flow["steps"], start=1):
        approval = "<strong>Human approval</strong>" if step["human_approval"] else "Automated dry-run"
        steps.append(
            "\n".join(
                [
                    '<article class="step">',
                    f"<span>{index}</span>",
                    f"<h2>{html.escape(step['name'])}</h2>",
                    f"<p>{html.escape(step['tool'])}: {html.escape(step['input'])} -> {html.escape(step['output'])}</p>",
                    f"<p>{approval}</p>",
                    "</article>",
                ]
            )
        )
    metrics = "".join(f"<li>{html.escape(metric)}</li>" for metric in flow["success_metrics"])
    return _html_page(
        title=f"{flow['name']} Demo",
        heading=flow["name"],
        intro=flow["summary"],
        body=f'<section class="steps">{"".join(steps)}</section><section><h2>Success Metrics</h2><ul>{metrics}</ul></section>',
    )


def _html_page(title: str, heading: str, intro: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #1d2430; background: #f6f7f9; }}
    header {{ padding: 32px; background: #ffffff; border-bottom: 1px solid #d9dee7; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    h1 {{ margin: 0 0 8px; font-size: 34px; letter-spacing: 0; }}
    h2 {{ font-size: 18px; letter-spacing: 0; }}
    p {{ line-height: 1.6; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
    .card, .step {{ background: #ffffff; border: 1px solid #d9dee7; border-radius: 8px; padding: 16px; }}
    .steps {{ display: grid; gap: 14px; }}
    .step span {{ display: inline-grid; place-items: center; width: 28px; height: 28px; border-radius: 999px; background: #0f766e; color: white; font-weight: 700; }}
    dt {{ font-weight: 700; margin-top: 10px; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(heading)}</h1>
    <p>{html.escape(intro)}</p>
  </header>
  <main>
    {body}
  </main>
</body>
</html>
"""
