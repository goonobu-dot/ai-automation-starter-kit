"""フロー図解（flow_diagram.html）の生成モジュールです。

フロー定義（core/flows.py の get_flow() が返す dict）から、
お客様（中小企業の経営者）に見せられる日本語の単一 HTML 図解を作ります。
CDN や外部ファイルへの依存はなく、ブラウザで開くだけで表示でき、印刷にも使えます。
"""

from __future__ import annotations

import html as _html
from pathlib import Path

# ステップ id ごとの日本語の役割説明（お客様向けの平易な言い換え）。
_STEP_ROLE_JA = {
    "intake": "元になるデータを集めます",
    "normalize": "内容を整理して仕分けします",
    "draft": "対応の下書きを作ります",
    "approve": "人が内容を確認して承認します",
    "report": "結果を報告書にまとめます",
}

_CSS = """
  body { font-family: "Hiragino Sans", "Yu Gothic", "Meiryo", sans-serif;
         margin: 0; padding: 24px; background: #f5f7fa; color: #1f2933; }
  .sheet { max-width: 720px; margin: 0 auto; background: #ffffff;
           border: 1px solid #d9e2ec; border-radius: 12px; padding: 32px; }
  h1 { font-size: 22px; margin: 0 0 8px; }
  h2 { font-size: 16px; margin: 28px 0 12px; border-left: 4px solid #2f6fed; padding-left: 8px; }
  .summary { color: #52606d; font-size: 14px; line-height: 1.7; }
  .step-card { border: 1px solid #cbd2d9; border-radius: 10px; padding: 14px 16px; }
  .step-card.approval { border: 2px solid #d97706; background: #fffbeb; }
  .step-no { font-size: 12px; font-weight: bold; color: #2f6fed; }
  .step-name { font-size: 15px; font-weight: bold; margin: 2px 0 6px; }
  .step-meta { font-size: 13px; color: #52606d; line-height: 1.7; }
  .badge { display: inline-block; background: #d97706; color: #ffffff;
           font-size: 12px; font-weight: bold; border-radius: 999px;
           padding: 2px 10px; margin-left: 8px; }
  .arrow { text-align: center; font-size: 20px; color: #9aa5b1; margin: 4px 0; }
  ul { margin: 8px 0; padding-left: 20px; font-size: 14px; line-height: 1.8; }
  .before-after { display: flex; gap: 12px; }
  .before-after .col { flex: 1; border: 1px solid #cbd2d9; border-radius: 10px; padding: 12px 14px;
                       font-size: 13px; line-height: 1.7; }
  .before-after .after { border-color: #2f6fed; background: #eff5ff; }
  .col-title { font-weight: bold; margin-bottom: 6px; }
  .safety { margin-top: 28px; border: 2px solid #059669; background: #ecfdf5;
            border-radius: 10px; padding: 14px 16px; font-size: 14px; line-height: 1.8; }
  .safety-title { font-weight: bold; color: #047857; margin-bottom: 4px; }
  @media print { body { background: #ffffff; padding: 0; }
                 .sheet { border: none; padding: 8px; } }
"""


def render_flow_diagram_html(flow: dict) -> str:
    """フロー定義から日本語 HTML 図解を組み立てて文字列で返します。"""
    esc = _html.escape
    parts = [
        "<!DOCTYPE html>",
        '<html lang="ja">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{esc(flow['name'])} の仕組み図解</title>",
        f"<style>{_CSS}</style>",
        "</head>",
        "<body>",
        '<div class="sheet">',
        f"<h1>{esc(flow['name'])}</h1>",
        '<p class="summary">この資料は、自動化の仕組みを図でご説明するものです。'
        "むずかしい設定は不要で、日々の作業がどう変わるかをご覧いただけます。</p>",
        f'<p class="summary">概要: {esc(flow["summary"])}</p>',
        "<h2>処理の流れ（上から順に進みます）</h2>",
    ]
    steps = flow["steps"]
    for number, step in enumerate(steps, start=1):
        approval = bool(step.get("human_approval"))
        card_class = "step-card approval" if approval else "step-card"
        badge = '<span class="badge">&#128100; 人の承認が必要</span>' if approval else ""
        role = _STEP_ROLE_JA.get(step.get("id", ""), "")
        role_html = f"<div class='step-meta'>{esc(role)}。</div>" if role else ""
        parts.extend(
            [
                f'<div class="{card_class}">',
                f'<div class="step-no">STEP {number} / {len(steps)}</div>',
                f'<div class="step-name">{esc(step["name"])}{badge}</div>',
                role_html,
                '<div class="step-meta">'
                f"使う道具: {esc(step['tool'])}<br>"
                f"入力（受け取るもの）: {esc(step['input'])} &rarr; 出力（できあがるもの）: {esc(step['output'])}"
                "</div>",
                "</div>",
            ]
        )
        if number < len(steps):
            parts.append('<div class="arrow">&#9660;</div>')
    parts.append("<h2>使用するツール（道具）一覧</h2>")
    parts.append("<ul>")
    parts.extend(f"<li>{esc(tool)}</li>" for tool in flow["tools"])
    parts.append("</ul>")
    parts.extend(
        [
            "<h2>自動化前 と 自動化後 の違い</h2>",
            '<div class="before-after">',
            '<div class="col"><div class="col-title">自動化前</div>'
            "担当者がデータを手作業で集め、一件ずつ内容を確認し、返信や報告書をゼロから作っています。"
            "件数が増えるほど時間がかかり、対応漏れも起きやすくなります。</div>",
            '<div class="col after"><div class="col-title">自動化後</div>'
            "データ集めと下書き作りをシステムが行い、人は「下書きの確認と承認」に集中できます。"
            "作業時間が短くなり、対応漏れを防ぎ、対応の記録も自動で残ります。</div>",
            "</div>",
            '<div class="safety">',
            '<div class="safety-title">&#9989; 安全設計について</div>',
            "このシステムは下書きを作るだけで、送信は必ず人が行います。"
            "お客様への連絡やお金に関わる操作が、確認なしに自動で実行されることはありません。",
            "</div>",
            "</div>",
            "</body>",
            "</html>",
        ]
    )
    return "\n".join(part for part in parts if part)


def write_flow_diagram(flow: dict, output: Path) -> Path:
    """図解 HTML を output/flow_diagram.html に書き出し、そのパスを返します。"""
    output.mkdir(parents=True, exist_ok=True)
    path = output / "flow_diagram.html"
    path.write_text(render_flow_diagram_html(flow), encoding="utf-8")
    return path
