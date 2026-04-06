import { useState } from 'react';
import { useStore } from '../store/useStore';

function SettingsPanel() {
  const { settings, updateSettings, toggleSettings, setConnectionStatus } = useStore();
  const [apiKey, setApiKey] = useState(settings.apiKey);
  const [testing, setTesting] = useState(false);

  const handleSave = async () => {
    updateSettings({ apiKey });
    if (window.electronAPI) {
      await window.electronAPI.setSetting('apiKey', apiKey);
      await window.electronAPI.setSetting('apiProvider', settings.apiProvider);
      await window.electronAPI.setSetting('model', settings.model);
    }
    toggleSettings();
  };

  const testConnection = async () => {
    setTesting(true);
    setConnectionStatus('connecting');
    
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      
      if (settings.apiProvider === 'openai') {
        headers['Authorization'] = `Bearer ${apiKey}`;
      } else if (settings.apiProvider === 'anthropic') {
        headers['x-api-key'] = apiKey;
        headers['anthropic-version'] = '2023-06-01';
      }

      const endpoint = settings.apiProvider === 'anthropic'
        ? 'https://api.anthropic.com/v1/messages'
        : `${settings.baseUrl || 'https://api.openai.com/v1'}/models`;

      const response = await fetch(endpoint, {
        method: 'GET',
        headers,
      });

      setConnectionStatus(response.ok ? 'online' : 'offline');
    } catch {
      setConnectionStatus('offline');
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="w-full max-w-md glass rounded-xl p-6 animate-[slideIn_0.2s_ease-out]">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-text-primary">02 Settings</h2>
          <button
            onClick={toggleSettings}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="space-y-6">
          {/* J.A.R.V.I.S. Mode Toggle */}
          <div className="flex items-center justify-between p-4 glass rounded-lg">
            <div>
              <h3 className="text-sm font-medium text-text-primary">J.A.R.V.I.S. Mode</h3>
              <p className="text-xs text-text-secondary mt-1">British accent, formal style</p>
            </div>
            <button
              onClick={() => updateSettings({ jarvisMode: !settings.jarvisMode })}
              className={`w-12 h-6 rounded-full transition-colors ${
                settings.jarvisMode ? 'bg-primary' : 'bg-white/10'
              }`}
            >
              <div
                className={`w-5 h-5 rounded-full bg-white transition-transform ${
                  settings.jarvisMode ? 'translate-x-6' : 'translate-x-0.5'
                }`}
              />
            </button>
          </div>

          {/* Personality */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Personality Mode
            </label>
            <select
              value={settings.personality}
              onChange={(e) => updateSettings({ personality: e.target.value as any })}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary/50"
            >
              <option value="friendly">Friendly - Casual and helpful</option>
              <option value="professional">Professional - Formal and precise</option>
              <option value="jarvis">J.A.R.V.I.S. - Like Tony Stark's AI</option>
            </select>
          </div>

          {/* API Provider */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              AI Provider
            </label>
            <select
              value={settings.apiProvider}
              onChange={(e) => updateSettings({ apiProvider: e.target.value as any })}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary/50"
            >
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="ollama">Ollama (Local)</option>
            </select>
          </div>

          {/* API Key */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-..."
              className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-secondary/50 focus:outline-none focus:border-primary/50"
            />
          </div>

          {/* Base URL (for Ollama) */}
          {settings.apiProvider === 'ollama' && (
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Base URL
              </label>
              <input
                type="text"
                value={settings.baseUrl}
                onChange={(e) => updateSettings({ baseUrl: e.target.value })}
                placeholder="http://localhost:11434/v1"
                className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-secondary/50 focus:outline-none focus:border-primary/50"
              />
            </div>
          )}

          {/* Model */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Model
            </label>
            <select
              value={settings.model}
              onChange={(e) => updateSettings({ model: e.target.value })}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary/50"
            >
              {settings.apiProvider === 'openai' && (
                <>
                  <option value="gpt-4o">GPT-4o</option>
                  <option value="gpt-4o-mini">GPT-4o Mini</option>
                  <option value="gpt-4-turbo">GPT-4 Turbo</option>
                </>
              )}
              {settings.apiProvider === 'anthropic' && (
                <>
                  <option value="claude-sonnet-4-20250514">Claude Sonnet 4</option>
                  <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
                  <option value="claude-3-5-haiku-20241022">Claude 3.5 Haiku</option>
                </>
              )}
              {settings.apiProvider === 'ollama' && (
                <>
                  <option value="llama3.2:3b">Llama 3.2 3B</option>
                  <option value="qwen2.5-coder:7b">Qwen 2.5 Coder 7B</option>
                  <option value="codellama:7b">Code Llama 7B</option>
                </>
              )}
            </select>
          </div>

          {/* Voice Settings */}
          <div className="border-t border-white/10 pt-6">
            <h3 className="text-sm font-medium text-text-primary mb-4">Voice Settings</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-text-secondary mb-2">
                  Speech Rate: {settings.voiceSpeed}x
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="2"
                  step="0.1"
                  value={settings.voiceSpeed}
                  onChange={(e) => updateSettings({ voiceSpeed: parseFloat(e.target.value) })}
                  className="w-full accent-primary"
                />
              </div>

              <div>
                <label className="block text-sm text-text-secondary mb-2">
                  Language / Accent
                </label>
                <select
                  value={settings.voiceLanguage}
                  onChange={(e) => updateSettings({ voiceLanguage: e.target.value })}
                  className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary/50"
                >
                  <option value="en-US">English (US) - American</option>
                  <option value="en-GB">English (UK) - British (Best for J.A.R.V.I.S.)</option>
                  <option value="en-AU">English (AU) - Australian</option>
                  <option value="es-ES">Spanish</option>
                  <option value="fr-FR">French</option>
                  <option value="de-DE">German</option>
                  <option value="zh-CN">Chinese</option>
                  <option value="ja-JP">Japanese</option>
                </select>
              </div>

              <div>
                <label className="block text-sm text-text-secondary mb-2">
                  Voice
                </label>
                <select
                  value={settings.voice}
                  onChange={(e) => updateSettings({ voice: e.target.value })}
                  className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary/50"
                >
                  <option value="alloy">Alloy (Neutral)</option>
                  <option value="echo">Echo (Male)</option>
                  <option value="fable">Fable (British)</option>
                  <option value="onyx">Onyx (Deep)</option>
                  <option value="nova">Nova (Female)</option>
                  <option value="shimmer">Shimmer (Soft)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              onClick={testConnection}
              disabled={testing || !apiKey}
              className="flex-1 px-4 py-2 glass rounded-lg text-sm text-text-primary hover:bg-white/10 disabled:opacity-50 transition-colors"
            >
              {testing ? 'Testing...' : 'Test Connection'}
            </button>
            <button
              onClick={handleSave}
              className="flex-1 px-4 py-2 bg-primary rounded-lg text-sm text-white hover:bg-primary/80 transition-colors"
            >
              Save & Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPanel;
