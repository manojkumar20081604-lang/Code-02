import { useEffect, useState } from 'react';
import { useStore } from './store/useStore';
import { useVoice } from './hooks/useVoice';
import TitleBar from './components/TitleBar';
import ChatArea from './components/ChatArea';
import InputArea from './components/InputArea';
import StatusBar from './components/StatusBar';
import SettingsPanel from './components/SettingsPanel';
import AIAvatar from './components/AIAvatar';
import CameraPanel from './components/CameraPanel';
import CommandPalette from './components/CommandPalette';
import SecurityPanel from './components/SecurityPanel';
import Dashboard from './components/Dashboard';

declare global {
  interface Window {
    electronAPI?: {
      minimize: () => void;
      maximize: () => void;
      close: () => void;
      openApp: (app: string) => Promise<{ success: boolean; error?: string }>;
      closeApp: (app: string) => Promise<{ success: boolean; error?: string }>;
      getRunningApps: () => Promise<{ success: boolean; apps: string[] }>;
      openUrl: (url: string) => Promise<{ success: boolean }>;
      search: (query: string) => Promise<void>;
      screenshot: () => Promise<{ success: boolean; path?: string }>;
      cameraCapture: () => Promise<{ success: boolean; path?: string }>;
      lock: () => Promise<{ success: boolean }>;
      shutdown: () => Promise<{ success: boolean }>;
      openFolder: (path: string) => Promise<{ success: boolean }>;
      listDesktop: () => Promise<{ success: boolean; items: string[] }>;
      setVolume: (volume: number) => Promise<{ success: boolean; volume: number }>;
      getVolume: () => Promise<{ success: boolean; volume: number }>;
      setBrightness: (brightness: number) => Promise<{ success: boolean; brightness: number }>;
      getClipboard: () => Promise<{ success: boolean; text: string }>;
      setClipboard: (text: string) => Promise<{ success: boolean }>;
      getSystemInfo: () => Promise<{ success: boolean; info: any }>;
      executeCommand: (command: string) => Promise<{ success: boolean }>;
      runCode: (code: string, language: string) => Promise<{ success: boolean; output?: string; errors?: string; error?: string }>;
      readFile: (filePath: string) => Promise<{ success: boolean; content?: string; error?: string }>;
      writeFile: (filePath: string, content: string) => Promise<{ success: boolean; error?: string }>;
      getSetting: (key: string) => Promise<any>;
      setSetting: (key: string, value: any) => Promise<void>;
      getAllSettings: () => Promise<any>;
      onVoiceToggle: (callback: () => void) => () => void;
      onOpenSettings: (callback: () => void) => () => void;
    };
    backendAPI?: {
      chat: (message: string) => Promise<any>;
      status: () => Promise<any>;
      modules: () => Promise<any>;
      jarvis: (action: string, data?: any) => Promise<any>;
    };
  }
}

function App() {
  const { settingsOpen, toggleSettings, updateSettings, isProcessing, cameraOpen, commandPaletteOpen, setCommandPaletteOpen, activeView, setActiveView } = useStore();
  const { toggleListening, isSupported } = useVoice();
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected'>('disconnected');

  useEffect(() => {
    // Check backend connection
    checkBackendConnection();
    
    // Setup listeners
    if (window.electronAPI) {
      const unsubVoice = window.electronAPI.onVoiceToggle(() => {
        toggleListening();
      });

      const unsubSettings = window.electronAPI.onOpenSettings(() => {
        toggleSettings();
      });

      window.electronAPI.getAllSettings().then((settings) => {
        if (settings) {
          updateSettings(settings);
        }
      });

      window.electronAPI.getVolume().then((result) => {
        if (result.success) {
          useStore.getState().setVolume(result.volume);
        }
      });

      return () => {
        unsubVoice();
        unsubSettings();
      };
    }
  }, [toggleListening, toggleSettings, updateSettings]);

  const checkBackendConnection = async () => {
    try {
      const response = await fetch('http://localhost:5000/health');
      if (response.ok) {
        setBackendStatus('connected');
      }
    } catch {
      setBackendStatus('disconnected');
    }
  };

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      <TitleBar />
      
      {/* View Toggle */}
      <div className="flex items-center justify-center gap-4 py-2 px-4 bg-surface/50 border-b border-border">
        <button
          onClick={() => setActiveView('chat')}
          className={`px-4 py-2 rounded-lg transition-all ${activeView === 'chat' ? 'bg-primary text-white' : 'bg-surface hover:bg-surface/80'}`}
        >
          💬 Chat
        </button>
        <button
          onClick={() => setActiveView('dashboard')}
          className={`px-4 py-2 rounded-lg transition-all ${activeView === 'dashboard' ? 'bg-primary text-white' : 'bg-surface hover:bg-surface/80'}`}
        >
          📊 Dashboard
        </button>
        <button
          onClick={() => setActiveView('security')}
          className={`px-4 py-2 rounded-lg transition-all ${activeView === 'security' ? 'bg-primary text-white' : 'bg-surface hover:bg-surface/80'}`}
        >
          🛡️ Security
        </button>
        
        {/* Backend Status */}
        <div className={`ml-auto flex items-center gap-2 px-3 py-1 rounded-full text-xs ${backendStatus === 'connected' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
          <div className={`w-2 h-2 rounded-full ${backendStatus === 'connected' ? 'bg-green-400' : 'bg-red-400'}`}></div>
          {backendStatus === 'connected' ? 'AI Connected' : 'AI Offline'}
        </div>
      </div>
      
      <main className="flex-1 flex flex-col overflow-hidden">
        {activeView === 'chat' && (
          <>
            <div className="flex items-center justify-center py-4">
              <AIAvatar isProcessing={isProcessing} />
            </div>
            <ChatArea />
            <InputArea isVoiceSupported={isSupported} />
          </>
        )}
        
        {activeView === 'dashboard' && <Dashboard />}
        {activeView === 'security' && <SecurityPanel />}
      </main>

      <StatusBar />
      
      {settingsOpen && <SettingsPanel />}
      <CameraPanel />
      <CommandPalette />
    </div>
  );
}

export default App;
