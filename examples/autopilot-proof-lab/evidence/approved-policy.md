# Approved Policy / 承認済みポリシー

## English

Fictional invoice-order review rules for a local proof lab:

- Standard route is allowed only when all required fields are present.
- Amount must be less than or equal to `5000.00` USD for the sample standard path.
- Currency must match between invoice and order.
- Required document status must be `complete`.
- Due date must be on or after the review date.
- Any duplicate invoice reference goes to quarantine.
- Any conflicting amount, currency, or supplier code goes to quarantine.
- Any external dependency failure goes to quarantine.

This policy supports readiness review only. It does not grant permission for unattended payment, submission, or system writes.

## 日本語

ローカル Proof Lab 用の架空ポリシーです。

- 必須項目がそろっている場合のみ標準経路を許可します。
- このサンプルの標準経路では金額は `5000.00` USD 以下です。
- 通貨は請求書と注文書で一致している必要があります。
- 必要書類の状態は `complete` である必要があります。
- 支払期日はレビュー日以降である必要があります。
- 請求書参照の重複は隔離経路に送ります。
- 金額、通貨、仕入先コードの矛盾は隔離経路に送ります。
- 外部依存先の障害は隔離経路に送ります。

これは準備度の確認用であり、無人実行、支払実行、外部更新を許可するものではありません。
