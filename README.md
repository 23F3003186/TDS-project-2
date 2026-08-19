---
title: Hybrid Quiz Solver
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Hybrid Quiz Solver

An intelligent quiz-solving agent using LangGraph with Gemini and OpenAI fallback.

## Features

- 🖥️ **Interactive Web UI**: Built-in dashboard at `/` for live task dispatching, diagnostics, and code generation
- 🔄 **Smart API Key Rotation**: Dynamic round-robin cycling across multiple Gemini keys
- 🛡️ **Automatic OpenAI Fallback**: Zero-downtime failover to OpenAI if Gemini quotas exhaust
- 📊 **Visualization Engine**: Matplotlib/Seaborn charting with Base64 PNG encoding
- 🎯 **Multi-Tool Agent**: Playwright web scraping, Python sandbox, Gemini Vision OCR, Speech STT
- 📝 **Timestamped & Gist Logging**: Dual-stream console/file logging and automatic GitHub Gist sync

## API & Web Endpoints

### Interactive Web UI
```bash
GET /
```
Access the responsive web dashboard with live health stats, interactive task dispatcher, and dynamic cURL/Python/JavaScript code generator.

### Health Check
```bash
GET /healthz
```

### Submit Quiz
```bash
POST /quiz
Content-Type: application/json

{
  "email": "your_email@example.com",
  "secret": "your_secret",
  "url": "https://quiz-url.com/q1.html"
}
```

## Environment Variables

Set these in Space Settings → Variables and secrets:

- `GOOGLE_API_KEY` - Primary Gemini key
- `GOOGLE_API_KEY_2` - Additional Gemini key (optional)
- `GOOGLE_API_KEY_3` - Additional Gemini key (optional)
- `GOOGLE_API_KEY_4` - Additional Gemini key (optional)
- `OPENAI_API_KEY` - OpenAI fallback key
- `OPENAI_MODEL` - OpenAI model (default: gpt-4o-mini)
- `TDS_EMAIL` - Your email
- `TDS_SECRET` - Your secret key

## Performance

- Average: ~73 seconds per question
- Supports 50+ question chains
- 3-minute timeout per question

## Architecture

```
Quiz URL → Agent → Tools (Web Scraper, Code Executor, etc.)
                ↓
           Gemini (with rotation)
                ↓
           Rate limit? → OpenAI Fallback
                ↓
           Submit Answer → Next Question
```
