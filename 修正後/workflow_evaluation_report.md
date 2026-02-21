# ワークフロー評価レポート
**対象ファイル**: `workflow_draft.json`
**評価日時**: 2026-02-21T10:59:38+09:00
**評価スキル**: `n8n-validation-expert`, `n8n-workflow-patterns`, `n8n-code-javascript`, `n8n-blast-protocol`

---

## 📊 総合スコア

| カテゴリ | スコア | 判定 |
|---|---|---|
| 構造・接続 | 7/10 | ⚠️ 要修正あり |
| エラーハンドリング | 4/10 | ❌ 不十分 |
| Codeノード品質 | 6/10 | ⚠️ 改善余地あり |
| 表現式・マッピング | 5/10 | ⚠️ リスクあり |
| ベストプラクティス適合 | 5/10 | ⚠️ 改善余地あり |
| **総合** | **27/50** | **⚠️ 要改善** |

---

## 🗺️ ワークフロー概要

**パターン**: Scheduled Task（定期タスク）
**参照スキル**: `n8n-workflow-patterns` > Pattern 5: Scheduled Tasks

```
Schedule Trigger (24h)
  → RSS Read (Yahoo IT)
  → Text Classifier (AI, relevant / non-relevant)
     [relevant] → Limit → HTTP Request (記事URL)
     [non-relevant] → No Operation, do nothing
     [error] → Send a message (Slack Error)
  → Extract Article Text (Code node)
  → Basic LLM Chain (Gemini 2.5 Flash Lite + Structured Output Parser)
  → Slack (投稿)
```

**目的**: Yahoo Japan IT ニュースRSSから記事を取得し、AI分類・要約・オピニオン生成してSlackに通知する自動化ワークフロー。

---

## ✅ 良い点

### 1. Structured Output Parser の活用
RSSデータをJSONスキーマで厳密に構造化している。LLMの出力揺れを防ぐための`hasOutputParser: true` + `outputParserStructured`の接続は正しいパターン。

### 2. Text Classifier でのAI分類
AIによるコンテンツフィルタリング（AI関連 / 非AI関連）を入れている。`retryOnFail: true` + `onError: "continueErrorOutput"` はエラー路の分岐を意識した適切な設定。

### 3. エラー時Slack通知の設定
Text Classifierのエラー出力→Slackへの通知ルートが存在する。エラーを無言で飲み込まない設計は良い。

### 4. Codeノードの基本構造
`Extract Article Text`（Codeノード）は`$input.all()`で全アイテムを処理し、`{json: result}`形式で返している。`n8n-code-javascript`の必須フォーマットを正しく遵守している。

---

## 🚨 Critical Issues（本番稼働前に必ず修正）

### Issue #1: `Limit`ノードのパラメータ未設定
**深刻度**: ERROR（ブロック）

```json
"parameters": {},
"type": "n8n-nodes-base.limit"
```

**問題**: `Limit`ノードのパラメータが空。`maxItems`が未設定のため、RSS全件（最大30件超）がそのまま後続に流れる可能性がある。HTTP Requestを全件実行し、Gemini APIコストが爆発する。

**修正**:
```json
"parameters": {
  "maxItems": 1
}
```

> ※ 1件のみ処理するなら `maxItems: 1` を設定すること。

---

### Issue #2: `Extract Article Text` のエラー処理が不完全
**深刻度**: ERROR（データロス）

```json
"onError": "continueRegularOutput"
```

**問題**: Codeノードでエラーが発生した場合、`continueRegularOutput`はエラーを無視して次のノードに進む。`__PRELOADED_STATE__`が見つからない場合にも`{error: 'PRELOADED_STATE not found'}`という不正なデータがLLM Chainに流れ込み、Geminiがゴミ入力を処理してしまう可能性がある。

**修正案**:
```javascript
// 現状: エラーデータをそのままpushしている
results.push({ json: { error: 'PRELOADED_STATE not found' } });

// 推奨: エラーがある場合はスキップ（空配列を返す）
if (startIndex === -1) {
  // continue; → ログだけ出してスキップ
  console.log('PRELOADED_STATE not found for item:', item.json.link);
  continue;
}
```

---

### Issue #3: Slack チャンネル名の不整合
**深刻度**: WARNING（実行時エラーの可能性）

| ノード | channelId.value | mode |
|---|---|---|
| `Slack`（最終投稿） | `テスト通知` | name |
| `Send a message`（エラー通知） | `#テスト通知` | name |

**問題**: 同じチャンネルを指しているはずだが、一方は`#`なし、もう一方は`#`あり。n8n の Slack ノードでは`name`モード時の`#`の扱いがバージョンによって異なる。実行時に`channel_not_found`エラーが発生するリスクがある。また、Slackノード自体の`typeVersion`が`2.2`と`2.4`で異なっている。

**修正**: 両ノードで同一フォーマット（例：`テスト通知`で統一、`#`なし）に揃える。

---

## ⚠️ Warnings（修正推奨）

### Warning #1: HTTP Requestノードに認証・エラーハンドリングなし
**参照スキル**: `n8n-workflow-patterns` > Error Handler Pattern

```json
"parameters": {
  "url": "={{ $json.link }}",
  "options": {}
}
```

- `onError`設定なし → スクレイピング失敗（404, 403, タイムアウト）でワークフロー全体が停止

**推奨設定**:
```json
"onError": "continueRegularOutput",
"retryOnFail": true,
"maxTries": 2
```

---

### Warning #2: LLM ChainにもエラーハンドリングがないBasic LLM Chain
- `onError`設定なし → Gemini APIレート制限、タイムアウトでワークフロー停止
- Gemini 2.5 Flash Liteは比較的新しいモデルのため、可用性リスクに注意

**推奨**: `retryOnFail: true`, `onError: "continueRegularOutput"` を追加

---

### Warning #3: Structured Output Parserのスキーマ内にn8n式が含まれている
**参照スキル**: `n8n-code-javascript` > #2 Expression Syntax Confusion

```json
"jsonSchemaExample": "{ \"source_url\": \"{{ $json.articleUrl }}\" }"
```

**問題**: `jsonSchemaExample`はスキーマ例（固定値）のため、`{{ $json.articleUrl }}`はn8n式として評価されず、**文字列リテラルとしてGeminiに送られる**。source_urlの値が動的にならない。

**修正**: LLM Chainのプロンプト側で`source_url`をすでに注入しているため（`"source_url": "{{ $json.articleUrl }}"` in promptText）、スキーマ例の値はプレースホルダー文字列に修正すること。

```json
"jsonSchemaExample": "{ \"source_url\": \"https://example.com/article\" }"
```

---

### Warning #4: Codeノード内でのHTMLスクレイピングの脆弱性
**参照スキル**: `n8n-code-javascript` > #4 Missing Null Checks

```javascript
const jsonStr = html.slice(startIndex + startMarker.length, endIndex).trim();
```

`endIndex`が`-1`（`</script>`が見つからない場合）になるとき、`html.slice(..., -1)`は最後の文字を除いた文字列になる。`endIndex === -1`のガード節が必要。

```javascript
// 追加すべきガード
if (endIndex === -1) {
  results.push({ json: { error: 'End script tag not found' } });
  continue;
}
```

---

## 💡 Suggestions（オプション改善）

### Suggestion #1: `No Operation, do nothing`ノードを削除するか、ログ出力に変更
非AI記事を無言でスキップするより、カウントを取るCodeノードに変えると後でデバッグが容易になる。

### Suggestion #2: n8n Workflow Patterns推奨の「エラートリガー」追加
```
[参照 n8n-workflow-patterns > Error Handler Pattern]
```
Global Error Triggerを追加し、予期しないワークフロー停止時に必ずSlack通知が飛ぶようにする。

### Suggestion #3: Geminiモデルのバージョン固定確認
`models/gemini-2.5-flash-lite`は実験的モデルの可能性がある。安定版（`gemini-1.5-flash`など）への切り替えを検討。

### Suggestion #4: `Limit`ノード後に`Split in Batches`パターンを検討
現状は上位N件に絞るだけだが、将来的に複数記事を処理したい場合、`Split in Batches`パターンが推奨。

---

## 🔧 BLAST Protocol 適合チェック

| フェーズ | 適合状況 |
|---|---|
| S - Strategy (設計) | ✅ 明確な目的（IT news → Slack）が存在 |
| B - Blueprint (スキーマ定義) | ⚠️ JSONスキーマは存在するが`gemini.md`なし |
| L - Link (接続確認) | ⚠️ Limit未設定、チャンネル名不整合あり |
| A - Architect (実装) | ✅ Code nodeのみ使用（カスタムノードなし） |
| S - Stylize (エラーハンドリング) | ❌ HTTP Request, LLM ChainのonError未設定 |
| T - Trigger (検証) | 未実施（ドラフト段階） |

---

## 📋 修正優先度サマリー

| 優先度 | 問題 | 修正コスト |
|---|---|---|
| 🔴 P0 | LimitノードのmaxItems未設定（API課金爆発リスク） | 5分 |
| 🔴 P0 | Extract Article TextのエラーデータがLLMに流入 | 15分 |
| 🟡 P1 | Slackチャンネル名の`#`不整合 | 5分 |
| 🟡 P1 | HTTP Request / LLM ChainのonError未設定 | 10分 |
| 🟡 P1 | Structured Output Parserの式リテラル問題 | 10分 |
| 🟢 P2 | endIndex === -1のガード節追加 | 10分 |
| 🟢 P2 | Global Error Triggerの追加 | 15分 |

---

## 結論

このワークフローは**コア機能の設計は正しい**。RSS→分類→スクレイピング→LLM→Slackというパイプラインは有効。ただし、**本番稼働させると2つのP0問題（Limitパラメータ未設定・エラーデータのLLM流入）でAPI課金の無駄遣いまたは誤動作が発生する**。

今日これを直せ。所要時間：**30分以内に全P0/P1を解消できる。**
