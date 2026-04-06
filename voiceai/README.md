# 02 - Your Personal AI Assistant

**"At your service."**

A powerful desktop AI assistant inspired by J.A.R.V.I.S. from Iron Man. 02 listens to your voice, controls your system, writes code, searches the web, and more.

### J.A.R.V.I.S. Mode
Enable J.A.R.V.I.S. mode in settings for a British accent, formal style, and sophisticated responses.

## Features

- **Voice Control** - Talk to your computer using natural language
- **System Control** - Open/close apps, search the web, take screenshots, lock screen
- **Modern UI** - Glass-morphism design with smooth animations
- **Multiple AI Providers** - Supports OpenAI, Anthropic Claude, and local Ollama
- **Global Hotkey** - Press `Ctrl+Shift+Space` to activate voice anywhere
- **System Tray** - Runs in background, always accessible

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- For voice: Chrome, Edge, or Safari browser (for Web Speech API)

### Installation

```bash
cd voiceai
npm install
```

### Development

```bash
npm run dev
```

This starts both the Vite dev server and Electron app.

### Build

```bash
npm run build
```

The built app will be in the `release` folder.

## Usage

### Voice Commands

- **"Open Chrome"** - Launch an application
- **"Search for latest news"** - Search the web
- **"Take a screenshot"** - Capture your screen
- **"Lock the screen"** - Lock your computer
- **"What's on my desktop"** - List desktop items

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+Space` | Toggle voice |
| `Enter` | Send message |
| `Shift+Enter` | New line in message |

### Settings

1. Click the gear icon in the title bar
2. Select your AI provider (OpenAI, Anthropic, or Ollama)
3. Enter your API key
4. Choose your model
5. Adjust voice speed and language

## Architecture

```
voiceai/
├── src/
│   ├── main/           # Electron main process
│   │   ├── index.ts    # Window management, IPC
│   │   └── preload.ts  # Context bridge
│   ├── renderer/       # React frontend
│   │   ├── components/ # UI components
│   │   ├── hooks/      # Voice recognition
│   │   └── store/      # Zustand state
│   └── shared/        # Shared types
└── public/            # Static assets
```

## Tech Stack

- **Electron** - Desktop framework
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **Vite** - Build tool
- **Web Speech API** - Voice recognition & synthesis

## License

MIT
