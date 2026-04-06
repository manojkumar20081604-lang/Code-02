import { create } from 'zustand';
import { v4 as uuidv4 } from 'uuid';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'security';
  content: string;
  timestamp: Date;
  actions?: SystemAction[];
  image?: string;
  isThreat?: boolean;
}

export interface SystemAction {
  type: 'open-app' | 'close-app' | 'search' | 'screenshot' | 'camera' | 'lock' | 'shutdown' | 'open-folder' | 'volume' | 'clipboard' | 'security-scan' | 'url-check' | string;
  target?: string;
  success?: boolean;
  error?: string;
  value?: number;
}

export interface ThreatInfo {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  recommendation: string;
  timestamp: Date;
}

export interface GoalStep {
  id: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  result?: string;
}

export interface ThinkingState {
  isThinking: boolean;
  currentThought: string;
  goalSteps: GoalStep[];
  confidence: number;
}

export interface Settings {
  apiProvider: 'openai' | 'anthropic' | 'gemini' | 'ollama';
  apiKey: string;
  baseUrl?: string;
  model: string;
  voiceLanguage: string;
  voiceSpeed: number;
  voice: string;
  minimizeToTray: boolean;
  startWithSystem: boolean;
  continuousMode: boolean;
  cameraEnabled: boolean;
  systemControlsEnabled: boolean;
  jarvisMode: boolean;
  personality: 'friendly' | 'professional' | 'jarvis';
  cyberMode: boolean;
  autoSecurityScan: boolean;
}

interface VoiceAIState {
  messages: Message[];
  isListening: boolean;
  isProcessing: boolean;
  settingsOpen: boolean;
  settings: Settings;
  connectionStatus: 'online' | 'offline' | 'connecting';
  volume: number;
  cameraOpen: boolean;
  commandPaletteOpen: boolean;
  securityScanOpen: boolean;
  isScanning: boolean;
  securityScore: number;
  threats: ThreatInfo[];
  isMonitoring: boolean;
  activeView: 'chat' | 'dashboard' | 'security';
  thinking: ThinkingState;

  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  clearMessages: () => void;
  setListening: (listening: boolean) => void;
  setProcessing: (processing: boolean) => void;
  toggleSettings: () => void;
  updateSettings: (settings: Partial<Settings>) => void;
  setConnectionStatus: (status: 'online' | 'offline' | 'connecting') => void;
  setVolume: (volume: number) => void;
  setCameraOpen: (open: boolean) => void;
  setCommandPaletteOpen: (open: boolean) => void;
  setSecurityScanOpen: (open: boolean) => void;
  setIsScanning: (scanning: boolean) => void;
  setSecurityScore: (score: number) => void;
  setThreats: (threats: ThreatInfo[]) => void;
  setIsMonitoring: (monitoring: boolean) => void;
  setActiveView: (view: 'chat' | 'dashboard' | 'security') => void;
  setThinking: (thinking: Partial<ThinkingState>) => void;
}

const defaultSettings: Settings = {
  apiProvider: 'openai',
  apiKey: '',
  baseUrl: '',
  model: 'gpt-4o',
  voiceLanguage: 'en-US',
  voiceSpeed: 1.0,
  voice: 'alloy',
  minimizeToTray: true,
  startWithSystem: false,
  continuousMode: false,
  cameraEnabled: true,
  systemControlsEnabled: true,
  jarvisMode: false,
  personality: 'friendly',
  cyberMode: true,
  autoSecurityScan: true,
};

export const useStore = create<VoiceAIState>((set) => ({
  messages: [],
  isListening: false,
  isProcessing: false,
  settingsOpen: false,
  settings: defaultSettings,
  connectionStatus: 'offline',
  volume: 50,
  cameraOpen: false,
  commandPaletteOpen: false,
  securityScanOpen: false,
  isScanning: false,
  securityScore: 100,
  threats: [],
  isMonitoring: false,
  activeView: 'chat',
  thinking: {
    isThinking: false,
    currentThought: '',
    goalSteps: [],
    confidence: 0,
  },

  addMessage: (message) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...message,
          id: uuidv4(),
          timestamp: new Date(),
        },
      ],
    })),

  clearMessages: () => set({ messages: [] }),

  setListening: (isListening) => set({ isListening }),

  setProcessing: (isProcessing) => set({ isProcessing }),

  toggleSettings: () => set((state) => ({ settingsOpen: !state.settingsOpen })),

  updateSettings: (newSettings) =>
    set((state) => ({
      settings: { ...state.settings, ...newSettings },
    })),

  setConnectionStatus: (connectionStatus) => set({ connectionStatus }),
  setVolume: (volume) => set({ volume }),
  setCameraOpen: (cameraOpen) => set({ cameraOpen }),
  setCommandPaletteOpen: (commandPaletteOpen) => set({ commandPaletteOpen }),
  setSecurityScanOpen: (securityScanOpen) => set({ securityScanOpen }),
  setIsScanning: (isScanning) => set({ isScanning }),
  setSecurityScore: (securityScore) => set({ securityScore }),
  setThreats: (threats) => set({ threats }),
  setIsMonitoring: (isMonitoring) => set({ isMonitoring }),
  setActiveView: (activeView) => set({ activeView }),
  setThinking: (thinking) => set((state) => ({
    thinking: { ...state.thinking, ...thinking },
  })),
}));
