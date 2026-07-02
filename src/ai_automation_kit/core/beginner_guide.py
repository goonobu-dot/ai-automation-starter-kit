"""初心者ナビ（beginner コマンド）の本体です。

副業で「中小企業への業務自動化提案」を始める人向けに、
今の段階に合わせて「やること・コマンド・開くファイル・次の一歩」を
標準出力に表示します。TTY 対話（input() など）には依存しません。
"""

from __future__ import annotations

# 各段階の定義。commands には実在する CLI コマンドだけを載せます
# （tests/test_beginner_guide.py が cli.py のサブコマンド一覧と突き合わせて検証します）。
BEGINNER_STEPS: dict = {
    1: {
        "title": "環境準備",
        "goal": "パソコンにこのキットを入れて、正しく動く状態にします。",
        "todo": [
            "Python（このキットを動かすプログラミング言語の実行環境）が入っているか確認します。",
            "このキットをインストールし、環境診断コマンドで問題がないか確認します。",
        ],
        "commands": [
            "pip install -e .  # インストール（pip は Python 用のアプリ追加コマンドです）",
            "ai-automation-kit doctor --output .tmp/doctor  # 環境診断（doctor はお医者さん役のチェック機能です）",
        ],
        "files": [
            "docs/GETTING_STARTED.ja.md  # 最初に読む入門ガイドです",
            ".tmp/doctor/doctor_report.md  # 診断結果のレポートです",
        ],
        "next": "診断結果がすべて OK になったら、段階 2「最初のデモ」に進みます。`ai-automation-kit beginner --step 2` と入力してください。",
    },
    2: {
        "title": "最初のデモ",
        "goal": "お客様に見せられるデモ一式を、まず自分のパソコンで作ってみます。",
        "todo": [
            "complete-workspace コマンドで、デモサイト・提案資料・チェックリストが入った作業フォルダ（ワークスペース）を一度に生成します。",
            "生成されたデモサイト（HTML ファイル）をブラウザで開いて、お客様目線で眺めてみます。",
        ],
        "commands": [
            "ai-automation-kit complete-workspace --industry finance --client-type local-business --niche accounting --output .tmp/first-demo  # デモ一式を生成します",
        ],
        "files": [
            ".tmp/first-demo/FINAL_DELIVERY_GUIDE.md  # 納品までの案内書です",
            ".tmp/first-demo/completion_checklist.md  # 完成チェックリストです",
            "docs/GETTING_STARTED.ja.md  # つまずいたらここに戻ります",
        ],
        "next": "デモの中身を自分の言葉で 1 分説明できるようになったら、段階 3「営業準備」に進みます。`ai-automation-kit beginner --step 3` と入力してください。",
    },
    3: {
        "title": "営業準備",
        "goal": "最初のお客様（中小企業）に見せる営業資料と提案書を用意します。",
        "todo": [
            "beginner-sales コマンドで、初心者向けの営業パック（提案書ひな形・デモ画面・フロー一覧）を生成します。",
            "チュートリアルを読みながら、価格の相場観とヒアリング（お客様への聞き取り）の質問を頭に入れます。",
        ],
        "commands": [
            "ai-automation-kit beginner-sales --industry operations --client-type small-business --output .tmp/sales-pack  # 営業パックを生成します",
        ],
        "files": [
            "docs/TUTORIAL_SME_PROPOSAL.ja.md  # 中小企業への提案副業の実践チュートリアルです",
            ".tmp/sales-pack/proposal_one_pager.md  # 1 枚もの提案書のひな形です",
            "docs/AI_PROMPTS.ja.md  # 提案書を AI で仕上げるためのプロンプト集です",
        ],
        "next": "提案書をお客様の社名入りで 1 通仕上げられたら、段階 4「最初の案件実行」に進みます。`ai-automation-kit beginner --step 4` と入力してください。",
    },
    4: {
        "title": "最初の案件実行",
        "goal": "受注した案件の自動化フロー（作業手順のセット）を実際に動かします。",
        "todo": [
            "flows list で使えるフローの一覧を見て、案件に合うものを選びます。",
            "flows install でフローを作業フォルダに展開し、flows run でドライラン（実際には送信しないお試し実行）します。",
            "生成された下書きを自分の目で確認し、問題なければ flows approve で承認します。承認するまで外部には何も送られません。",
        ],
        "commands": [
            "ai-automation-kit flows list  # 使えるフローの一覧を表示します",
            "ai-automation-kit flows install invoice-document-followup --output .tmp/first-job  # フローを展開します",
            "ai-automation-kit flows run .tmp/first-job  # ドライラン（お試し実行）します",
            "ai-automation-kit flows approve .tmp/first-job --approver your-name  # 内容を確認してから承認します",
        ],
        "files": [
            ".tmp/first-job/automation_output/draft_outputs.md  # 生成された下書きです。必ず目視確認します",
            ".tmp/first-job/automation_output/approval_queue.csv  # 承認待ちの一覧です",
            "docs/USER_MANUAL.ja.md  # 各コマンドの詳しい操作説明書です",
        ],
        "next": "承認まで一通り体験できたら、段階 5「納品と請求」に進みます。`ai-automation-kit beginner --step 5` と入力してください。",
    },
    5: {
        "title": "納品と請求",
        "goal": "成果物をお客様に渡し、報告書を添えて請求までつなげます。",
        "todo": [
            "client-report コマンドで、お客様向けの実施報告書を生成します。",
            "package-client-demo コマンドで、納品物一式を ZIP（ひとつにまとめた圧縮ファイル）にします。",
            "share-check コマンドで、渡してはいけない情報（個人情報や認証情報）が混ざっていないか最終確認します。",
        ],
        "commands": [
            "ai-automation-kit client-report --flow-project .tmp/first-job --output .tmp/delivery  # お客様向け報告書を生成します",
            "ai-automation-kit package-client-demo --source .tmp/first-job --output .tmp/delivery  # 納品用 ZIP を作ります",
            "ai-automation-kit share-check --source .tmp/delivery --output .tmp/share-check  # 共有前の安全確認をします",
        ],
        "files": [
            ".tmp/delivery/client_report.md  # お客様に渡す報告書です",
            "docs/TUTORIAL_SME_PROPOSAL.ja.md  # 請求・継続提案の進め方はこちらの後半にあります",
            "docs/INDEX.md  # 次に読むドキュメントを探す索引です",
        ],
        "next": "納品と請求が終わったら 1 案件完了です。おつかれさまでした。2 件目は段階 3 から繰り返します。`ai-automation-kit beginner --step 3` と入力してください。",
    },
}


def render_beginner_overview() -> str:
    """5 段階の全体ナビを日本語で組み立てます。"""
    lines = [
        "# 初心者ナビ（副業で最初の 1 案件を完了するまでの 5 段階）",
        "",
        "いまのあなたの段階を選んで、`ai-automation-kit beginner --step 番号` と入力してください。",
        "",
    ]
    for number in sorted(BEGINNER_STEPS):
        step = BEGINNER_STEPS[number]
        lines.append(f"{number}. {step['title']} — {step['goal']}")
    lines.extend(
        [
            "",
            "はじめての方は、まず次のコマンドから始めてください。",
            "",
            "    ai-automation-kit beginner --step 1",
            "",
            "迷ったら docs/GETTING_STARTED.ja.md を開くと、全体の流れが分かります。",
        ]
    )
    return "\n".join(lines)


def render_beginner_step(step: int) -> str:
    """指定された段階の詳細ナビを日本語で組み立てます。"""
    if step not in BEGINNER_STEPS:
        raise ValueError(f"step must be 1..5, got {step}")
    data = BEGINNER_STEPS[step]
    lines = [
        f"# 段階 {step}/5: {data['title']}",
        "",
        data["goal"],
        "",
        "## この段階でやること",
        "",
    ]
    lines.extend(f"- {item}" for item in data["todo"])
    lines.extend(["", "## 実行するコマンド", ""])
    lines.extend(f"    {command}" for command in data["commands"])
    lines.extend(["", "## 開くファイル", ""])
    lines.extend(f"- {path}" for path in data["files"])
    lines.extend(["", "## 次の一歩", "", data["next"]])
    return "\n".join(lines)
