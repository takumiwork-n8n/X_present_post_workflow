# Project Constitution: X Post Trend Collector Workflow

## Core Objective
自動的にニュースやトレンドを取得し、X（Twitter）に投稿するための要約とオピニオン付きのドラフトを作成する「AI事業部長」。
目的：リード獲得のための圧倒的時短デモ、および日々のインプレッション確保。

## Architectural Pattern
- **Trigger**: RSS Read (Schedule Triggerなどでキックも可だが、シンプルにRSS Readを先頭にするか、Schedule -> RSS Readの構成)
  - 構成: `Schedule Trigger` -> `RSS Read` -> `Basic LLM Chain` -> `Slack` / `Notion`
- **Logic**: Basic LLM Chain (Gemini or OpenAI)
- **Output**: Slack / Notion / Email (ドラフト送付)

## Data Schema (Input)
```json
{
  "title": "記事のタイトル",
  "link": "記事のURL",
  "content": "記事の本文やスニペット"
}
```

## Data Schema (Output)
```json
{
  "summary_140": "X投稿用の140文字以内の要約",
  "opinion": "辛口かつ本質を突くオピニオン（インプレッション用）",
  "source_url": "元記事リンク"
}
```

## Node Strategy
1. **Schedule Trigger**: 
   - 毎日指定の時間（例: 朝8時）に起動。
2. **RSS Read**:
   - URL: ターゲット層が読むメディアのRSSフィードURL。
3. **Basic LLM Chain**:
   - Model: OpenAI (GPT-4o-mini) または Gemini (1.5 Flash)。コストと速度重視。
   - Prompt: 入力Schemaの要素を渡し、出力SchemaのJSONで返すよう指示する。
4. **Slack / Notion**:
   - Slack: 特定のチャンネルまたはDMに、投稿しやすいフォーマットで送信。
