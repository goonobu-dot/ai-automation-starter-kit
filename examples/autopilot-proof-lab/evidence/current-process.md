# Current Process / 現在手順

## English

This fictional workflow reviews invoice-order pairs before a human reviewer decides whether the draft looks safe.

1. Intake receives a local export with invoice fields and order fields.
2. The reviewer checks supplier code, currency, amount, due date, and required document status.
3. If the pair is complete and within the approved rule set, the draft can stay on the standard path.
4. If data is missing, duplicated, contradictory, expired, or unavailable, the case moves to quarantine.
5. A human reviews the quarantine queue and decides what to do next.

Important boundary:

- This sample does not approve payment.
- This sample does not send messages.
- This sample does not update any external system.

## 日本語

この架空サンプルでは、請求書と注文書の組み合わせを確認し、人が安全性を判断します。

1. ローカルのエクスポートを受け取り、請求書項目と注文書項目を見ます。
2. 担当者は仕入先コード、通貨、金額、支払期日、必要書類の有無を確認します。
3. 情報がそろっていて、承認済みルール内なら標準経路に残します。
4. 欠損、重複、矛盾、期限切れ、外部障害があれば隔離経路に送ります。
5. 隔離キューは人が確認し、次の対応を決めます。

安全境界:

- 支払承認はしません。
- 外部送信はしません。
- 外部システム更新はしません。
