# 02 - ZERO TWO
### AI Cyber Defense Assistant

<p align="center">
  <img src="voiceai/public/icon.svg" width="128" alt="02 Logo">
</p>

> *"At your service."* — J.A.R.V.I.S.

> ⚠️ **DISCLAIMER**: This tool is for **educational and authorized testing only**. Do not use for unauthorized access or attacking systems without permission.

## Features

### Electron Desktop App
- Voice recognition & text-to-speech
- Dark glass-morphism GUI
- System controls (apps, volume, screenshots, clipboard, lock)
- Security panel with threat monitoring
- Multiple AI provider support

### Python Backend (02 AI Brain)
- AI-powered chat with intent classification
- Memory system (short-term + long-term)
- Cyber security tools
- ML phishing detection
- Background monitoring

### Security Features
- URL threat analysis
- File scanning
- Network port scanning
- Email phishing detection
- Continuous threat monitoring
- Real-time alerts

## Quick Start

### Option 1: One-Click Launch
```bash
# Windows
double-click START-02.bat

# Linux/Mac
chmod +x START-02.sh && ./START-02.sh
```

### Option 2: Manual Start

**1. Install Dependencies**
```bash
# Python backend
cd cyber-assistant
pip install flask flask-cors requests openai anthropic numpy pandas scikit-learn

# Electron frontend
cd voiceai
npm install
```

**2. Start Backend**
```bash
cd cyber-assistant
python api_server.py
# Runs on http://localhost:5000
```

**3. Start Frontend**
```bash
cd voiceai
npm run dev
# Opens at http://localhost:5173
```

## API Endpoints

### Core
- `POST /chat` - Chat with 02
- `POST /chat/voice` - Voice-optimized chat
- `GET /status` - System status

### Security Scans
- `POST /scan/system` - Full system scan
- `POST /scan/quick` - Quick threat scan
- `POST /scan/url` - URL threat analysis
- `POST /scan/file` - File threat analysis
- `POST /scan/network` - Network port scan

### ML Detection
- `POST /ml/detect-phishing` - ML phishing detection
- `POST /ml/batch-url-check` - Batch URL check

### Data Science
- `GET /data/summary` - Get data science summary
- `GET /data/report` - Generate analysis report
- `GET /data/charts` - Get all visualization charts
- `GET /data/attacks` - Attack statistics
- `POST /data/prediction` - ML threat prediction
- `GET /data/trend` - Threat trend analysis
- `POST /data/log-threat` - Log new threat
- `GET /data/anomalies` - Detect anomalies

### Pentesting (Educational Use Only)
- `GET /pentest/disclaimer` - View disclaimer
- `POST /pentest/recon` - Run reconnaissance
- `POST /pentest/recon/whois` - WHOIS lookup
- `POST /pentest/recon/ports` - Port scanning
- `POST /pentest/web/analyze` - Web app analysis
- `POST /pentest/web/crawl` - Web crawler
- `POST /pentest/test/hints` - Get testing hints
- `POST /pentest/test/plan` - Generate test plan
- `POST /pentest/report/create` - Create bug finding
- `POST /pentest/report/generate` - Generate report

### Voice Assistant
- `GET /voice/status` - Voice system status
- `POST /voice/verify` - Speaker verification
- `POST /voice/record` - Record voice sample
- `POST /voice/train` - Train voice model
- `POST /voice/command` - Process voice command
- `POST /voice/speak` - Text to speech

### Personal Assistant
- `GET /personal/today` - Today's summary
- `POST /personal/reminder/add` - Add reminder
- `GET /personal/reminder/list` - List reminders
- `POST /personal/note/add` - Add note
- `GET /personal/note/list` - List notes
- `POST /personal/task/add` - Add task
- `GET /personal/task/list` - List tasks
- `GET /personal/plan` - Generate daily plan

### Developer Assistant
- `POST /dev/analyze` - Analyze code
- `POST /dev/fix-error` - Fix common errors
- `POST /dev/readme` - Generate README
- `GET /dev/gitignore` - Generate .gitignore

### Content Creation
- `POST /content/post` - Generate social post
- `POST /content/blog` - Generate blog post
- `POST /content/presentation` - Generate slides
- `GET /content/hashtags` - Suggest hashtags
- `POST /content/email` - Generate email

### File Manager
- `POST /files/search` - Search files
- `POST /files/organize` - Organize by type
- `POST /files/tree` - Get directory tree
- `POST /files/duplicates` - Find duplicates

### Web Assistant
- `GET /web/search` - Web search
- `POST /web/content` - Extract page content
- `POST /web/summarize` - Summarize text
- `POST /web/extract` - Extract structured data

### Monitoring
- `POST /monitor/start` - Start background monitoring
- `POST /monitor/stop` - Stop monitoring
- `GET /monitor/status` - Monitoring status
- `GET /monitor/alerts` - Active alerts

### Memory
- `POST /memory/store` - Store in memory
- `GET /memory/recall` - Recall from memory

## Web Dashboard

```bash
cd cyber-assistant
python dashboard.py
# Opens at http://localhost:5001
```

## Voice Commands

| Command | Action |
|---------|--------|
| "open [app]" | Launch application |
| "close [app]" | Close application |
| "screenshot" | Take screenshot |
| "volume 50" | Set volume |
| "lock screen" | Lock computer |
| "security scan" | Run security scan |
| "check URL [link]" | Analyze URL for threats |
| "start monitoring" | Enable continuous monitoring |

## Project Structure

```
├── voiceai/                    # Electron Desktop App
│   ├── src/
│   │   ├── main/              # Main process
│   │   └── renderer/          # React UI
│   └── package.json
│
├── cyber-assistant/           # Python Backend
│   ├── api_server.py          # Flask API
│   ├── dashboard.py            # Web Dashboard
│   ├── monitor.py             # Background Monitor
│   ├── main.py                # Main Assistant
│   ├── data_science/          # Data Science Module
│   │   ├── analysis.py        # Data analysis
│   │   ├── visualization.py  # Charts & graphs
│   │   ├── prediction.py      # ML prediction
│   │   ├── preprocess.py      # Data cleaning
│   │   ├── utils.py           # Utilities
│   │   └── dataset/
│   │       └── logs.csv       # Threat logs
│   ├── pentest/               # Pentesting Module
│   │   ├── recon.py          # Reconnaissance
│   │   ├── analyzer.py        # Web analyzer
│   │   ├── tester.py         # Vulnerability hints
│   │   └── reporter.py       # Bug report generator
│   ├── voice/                  # Voice Assistant
│   │   ├── voice_assistant.py # Main voice module
│   │   └── voice_samples/      # Voice samples
│   ├── modules/               # Universal AI Modules
│   │   ├── personal.py       # Personal assistant
│   │   ├── developer.py      # Developer help
│   │   ├── content.py        # Content creation
│   │   ├── files.py          # File manager
│   │   └── web.py            # Web assistant
│   └── tools/
│       └── phishing_detector.py  # Phishing detection
│
├── START-02.bat               # Windows Launcher
└── README.md                  # Documentation
```

## Requirements

- Python 3.8+
- Node.js 18+
- npm or yarn

## License

MIT
