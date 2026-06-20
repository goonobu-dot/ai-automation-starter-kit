# 顧客デモ台本

この台本は、企業へAI Automation Starter Kitの成果物を見せるときに使います。

## 1. 最初の説明

「今日は大きな本番システムの話ではなく、1つの繰り返し業務を安全に dry-run するデモを見せます。」

## 2. フローを見せる

開くファイル:

```bash
.tmp/quickstart-accounting/beginner_sales/selected_flow_demo.html
```

説明すること:

- どこからデータが入るか
- 何を自動で整理するか
- どこで人間が確認するか
- 何がレポートとして残るか

## 3. 質問する

`client_questions.md` を見ながら、実際の業務に合わせて質問します。

## 4. dry-run 結果を見せる

開くファイル:

- `automation_output/work_queue.csv`
- `automation_output/draft_outputs.md`
- `automation_output/approval_queue.csv`
- `automation_output/status_report.md`

## 5. 次の判断を聞く

最後に、次の3択で確認します。

- 続ける
- 修正してもう一度試す
- 今回は止める

この判断が明確になること自体が、良いPoCです。

