import os
import requests
import json

# Fetching the same token used previously for Slack/n8n API
# Note: N8N API url should be configurable, assuming local or standard port
N8N_URL = os.environ.get("N8N_HOST", "http://localhost:5678/api/v1")
N8N_API_KEY = os.environ.get("N8N_API_KEY", "") # Need user's API Key if required

def create_workflow():
    payload = {
        "name": "X Post Trend Collector",
        "nodes": [
            {
                "parameters": {
                    "rule": {
                        "interval": [
                            {
                                "field": "hours",
                                "hoursInterval": 24
                            }
                        ]
                    }
                },
                "id": "schedule_node",
                "name": "Schedule Trigger",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1,
                "position": [
                    0,
                    0
                ]
            },
            {
                "parameters": {
                    "url": "https://news.yahoo.co.jp/rss/topics/it.xml"
                },
                "id": "rss_node",
                "name": "RSS Read",
                "type": "n8n-nodes-base.rssFeedRead",
                "typeVersion": 1.2,
                "position": [
                    200,
                    0
                ]
            },
            {
                "parameters": {
                    "promptType": "define",
                    "text": "以下は最新のITニュースRSSデータの1件です。\nタイトル: {{$json.title}}\nリンク: {{$json.link}}\n内容: {{$json.contentSnippet}}\n\nこれを元に、以下のJSONフォーマットで回答してください。\n{\n  \"summary_140\": \"X（Twitter）でRTされやすく、ターゲット（忙しい経営者やエンジニア）の目を引く140文字以内のニュース要約\",\n  \"opinion\": \"このニュースに対する、辛口で本質を突くようなオピニオン。単なる感想ではなく、ビジネス的な示唆を含めること。\",\n  \"source_url\": \"{{$json.link}}\"\n}\n\nなお、出力は必ずJSONのみとし、余計なマークダウンやテキストは含めないでください。"
                },
                "id": "llm_node",
                "name": "Basic LLM Chain",
                "type": "@n8n/n8n-nodes-langchain.chainLlm",
                "typeVersion": 1.4,
                "position": [
                    400,
                    0
                ]
            },
            {
                "parameters": {
                    "model": "gemini-1.5-flash"
                },
                "id": "gemini_model",
                "name": "Google Gemini Chat Model",
                "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
                "typeVersion": 1,
                "position": [
                    400,
                    200
                ]
            },
            {
               "parameters": {
                    "options": {}
                },
                "id": "json_parse_node",
                "name": "JSON Parse",
                "type": "n8n-nodes-base.jsonParse",
                "typeVersion": 1,
                "position": [
                    600,
                    0
                ]
            },
            {
                "parameters": {
                    "channel": "C0123456789", 
                    "text": "=【🚨 今日のトレンドニュース】\n📝 要約:\n{{$json.summary_140}}\n\n💡 オピニオン:\n{{$json.opinion}}\n\n🔗 ソース:\n{{$json.source_url}}",
                    "otherOptions": {}
                },
                "id": "slack_node",
                "name": "Slack",
                "type": "n8n-nodes-base.slack",
                "typeVersion": 2.2,
                "position": [
                    800,
                    0
                ]
            }
        ],
        "connections": {
            "Schedule Trigger": {
                "main": [
                    [
                        {
                            "node": "RSS Read",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "RSS Read": {
                "main": [
                    [
                        {
                            "node": "Basic LLM Chain",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Google Gemini Chat Model": {
                "ai_languageModel": [
                    [
                        {
                            "node": "Basic LLM Chain",
                            "type": "ai_languageModel",
                            "index": 0
                        }
                    ]
                ]
            },
            "Basic LLM Chain": {
                "main": [
                    [
                        {
                            "node": "Slack",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "settings": {}
    }
    
    headers = {
        "Content-Type": "application/json",
    }
    if N8N_API_KEY:
        headers["X-N8N-API-KEY"] = N8N_API_KEY

    try:
        response = requests.post(
            f"{N8N_URL}/workflows",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        print("Workflow created successfully:", response.json().get('id'))
        
        # Save to local file as backup
        with open("workflow_draft.json", "w") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print("Failed to create workflow via API:", e)
        if hasattr(e, 'response') and e.response is not None:
             print(e.response.text)
        print("Saving to local file workflow_draft.json instead.")
        with open("workflow_draft.json", "w") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    create_workflow()
