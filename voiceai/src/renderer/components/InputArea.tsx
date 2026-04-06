import { useState } from 'react';
import { useStore } from '../store/useStore';
import { useVoice, speak } from '../hooks/useVoice';

interface InputAreaProps {
  isVoiceSupported: boolean;
}

function InputArea({ isVoiceSupported }: InputAreaProps) {
  const [input, setInput] = useState('');
  const { addMessage, setProcessing, settings } = useStore();
  const { toggleListening, isListening, interimTranscript, isSupported } = useVoice();

  const handleSubmit = async () => {
    if (!input.trim()) return;

    const text = input;
    setInput('');
    addMessage({ role: 'user', content: text });
    setProcessing(true);

    try {
      const response = await fetchAIResponse(text);
      addMessage({ role: 'assistant', content: response.text, actions: response.actions });
      speak(response.text);
    } catch (error) {
      addMessage({ role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' });
    } finally {
      setProcessing(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="glass rounded-xl p-4">
      <div className="flex items-end gap-3">
        <div className="flex-1 relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message or command..."
            className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-sm text-text-primary placeholder-text-secondary/50 resize-none focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
            rows={1}
          />
          {isListening && interimTranscript && (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-text-secondary/50 text-sm italic">
              {interimTranscript}...
            </div>
          )}
        </div>

        <button
          onClick={handleSubmit}
          disabled={!input.trim()}
          className="p-3 rounded-lg bg-primary hover:bg-primary/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>

        {isSupported && (
          <button
            onClick={toggleListening}
            className={`p-3 rounded-lg transition-all ${
              isListening
                ? 'bg-red-500 glow-accent animate-pulse'
                : 'bg-accent/20 hover:bg-accent/30'
            }`}
          >
            <svg className={`w-5 h-5 ${isListening ? 'text-white' : 'text-accent'}`} fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.2 14.47 16 12 16s-4.52-1.8-4.93-4.15c-.08-.49-.49-.85-.98-.85-.61 0-1.09.54-1 1.14.49 3 2.89 5.35 5.91 5.78V20c0 .55.45 1 1 1s1-.45 1-1v-2.08c3.02-.43 5.42-2.78 5.91-5.78.1-.6-.39-1.14-1-1.14z" />
            </svg>
          </button>
        )}
      </div>

      <div className="mt-2 flex items-center gap-4 text-xs text-text-secondary">
        <span>Press Enter to send</span>
        <span className="opacity-50">|</span>
        <span>{isListening ? 'Listening...' : 'Ctrl+Shift+Space for voice'}</span>
      </div>
    </div>
  );
}

async function fetchAIResponse(userMessage: string): Promise<{ text: string; actions: any[] }> {
  const settings = useStore.getState().settings;
  
  if (!settings.apiKey) {
    return {
      text: "Please configure your API key in settings to use the AI assistant.",
      actions: []
    };
  }

  const systemPrompt = `You are VoiceAI, a helpful desktop assistant. You can control the system by using these commands:
- "open [app name]" - Open applications like Chrome, Notepad, Calculator
- "close [app name]" - Close running applications
- "search for [query]" - Search the web using Google
- "take screenshot" - Capture the screen
- "lock screen" - Lock the computer
- "show desktop items" - List what's on the desktop

Be helpful and concise. Execute commands mentioned in your response.`;

  try {
    let endpoint = '';
    let body: any = {};
    let headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (settings.apiProvider === 'openai' || settings.apiProvider === 'ollama') {
      endpoint = `${settings.baseUrl || 'https://api.openai.com/v1'}/chat/completions`;
      body = {
        model: settings.model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userMessage }
        ],
        stream: false,
      };
      headers['Authorization'] = `Bearer ${settings.apiKey}`;
    } else if (settings.apiProvider === 'anthropic') {
      endpoint = 'https://api.anthropic.com/v1/messages';
      body = {
        model: settings.model,
        max_tokens: 1024,
        messages: [{ role: 'user', content: userMessage }],
        system: systemPrompt,
      };
      headers['x-api-key'] = settings.apiKey;
      headers['anthropic-version'] = '2023-06-01';
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    
    let text = '';
    if (settings.apiProvider === 'openai' || settings.apiProvider === 'ollama') {
      text = data.choices?.[0]?.message?.content || '';
    } else if (settings.apiProvider === 'anthropic') {
      text = data.content?.[0]?.text || '';
    }

    const actions = await parseAndExecuteCommands(text);

    return { text, actions };
  } catch (error) {
    console.error('AI API error:', error);
    throw error;
  }
}

async function parseAndExecuteCommands(text: string): Promise<any[]> {
  const actions: any[] = [];
  const lowerText = text.toLowerCase();

  if (window.electronAPI) {
    const openMatch = lowerText.match(/open\s+(?:the\s+)?(?:app\s+)?(.+?)(?:\.|,|$)/i);
    if (openMatch && !lowerText.includes('openai')) {
      const appName = openMatch[1].trim();
      const result = await window.electronAPI.openApp(appName);
      actions.push({ type: 'open-app', target: appName, success: result.success });
    }

    const closeMatch = lowerText.match(/close\s+(?:the\s+)?(.+?)(?:\.|,|$)/i);
    if (closeMatch) {
      const appName = closeMatch[1].trim();
      const result = await window.electronAPI.closeApp(appName);
      actions.push({ type: 'close-app', target: appName, success: result.success });
    }

    const searchMatch = lowerText.match(/search\s+(?:for\s+)?(.+?)(?:\.|,|$)/i);
    if (searchMatch) {
      const query = searchMatch[1].trim();
      await window.electronAPI.openUrl(`https://www.google.com/search?q=${encodeURIComponent(query)}`);
      actions.push({ type: 'search', target: query, success: true });
    }

    if (lowerText.includes('take') && lowerText.includes('screenshot')) {
      const result = await window.electronAPI.screenshot();
      actions.push({ type: 'screenshot', success: result.success, path: result.path });
    }

    if ((lowerText.includes('lock') && (lowerText.includes('screen') || lowerText.includes('computer')))) {
      const result = await window.electronAPI.lock();
      actions.push({ type: 'lock', success: result.success });
    }

    if (lowerText.includes("what's on my desktop") || (lowerText.includes('show') && lowerText.includes('desktop'))) {
      const result = await window.electronAPI.listDesktop();
      if (result.success && result.items.length > 0) {
        text += `\n\nDesktop contains: ${result.items.slice(0, 5).join(', ')}${result.items.length > 5 ? '...' : ''}`;
      }
      actions.push({ type: 'list-desktop', items: result.items, success: result.success });
    }
  }

  return actions;
}

export default InputArea;
