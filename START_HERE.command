#!/bin/zsh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

clear
echo "業務自動化の見本を準備します。"
echo "APIキーや顧客データは必要ありません。"
echo ""

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 が見つかりませんでした。"
  echo "この画面を閉じず、Codexに『Python 3の準備を手伝って』と依頼してください。"
  echo ""
  read -r "?Enterキーを押すと終了します。"
  exit 1
fi

python3 scripts/first_start.py --open
status=$?

if [[ $status -ne 0 ]]; then
  echo ""
  echo "準備を完了できませんでした。上のエラーをCodexへ見せてください。"
  read -r "?Enterキーを押すと終了します。"
  exit $status
fi

echo ""
echo "準備が完了しました。ブラウザの『次はこれだけ』から進んでください。"
read -r "?Enterキーを押すとこの画面を閉じます。"
