export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  actions?: SystemAction[];
}

export interface SystemAction {
  type: string;
  target?: string;
  success?: boolean;
  error?: string;
  items?: string[];
  path?: string;
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
}

export interface ElectronAPI {
  minimize: () => void;
  maximize: () => void;
  close: () => void;
  openApp: (appName: string) => Promise<{ success: boolean; error?: string }>;
  closeApp: (appName: string) => Promise<{ success: boolean; error?: string }>;
  getRunningApps: () => Promise<{ success: boolean; apps: string[] }>;
  openUrl: (url: string) => Promise<{ success: boolean }>;
  search: (query: string) => Promise<void>;
  screenshot: () => Promise<{ success: boolean; path?: string }>;
  cameraCapture: () => Promise<{ success: boolean; path?: string }>;
  lock: () => Promise<{ success: boolean }>;
  shutdown: () => Promise<{ success: boolean }>;
  openFolder: (path: string) => Promise<{ success: boolean }>;
  listDesktop: () => Promise<{ success: boolean; items: string[] }>;
  setVolume: (volume: number) => Promise<{ success: boolean; volume: number; error?: string }>;
  getVolume: () => Promise<{ success: boolean; volume: number }>;
  setBrightness: (brightness: number) => Promise<{ success: boolean; brightness: number; error?: string }>;
  getClipboard: () => Promise<{ success: boolean; text: string; error?: string }>;
  setClipboard: (text: string) => Promise<{ success: boolean; error?: string }>;
  getSystemInfo: () => Promise<{ success: boolean; info: SystemInfo }>;
  executeCommand: (command: string) => Promise<{ success: boolean; error?: string }>;
  runCode: (code: string, language: string) => Promise<{ success: boolean; output?: string; errors?: string; error?: string }>;
  readFile: (filePath: string) => Promise<{ success: boolean; content?: string; error?: string }>;
  writeFile: (filePath: string, content: string) => Promise<{ success: boolean; error?: string }>;
  getSetting: (key: string) => Promise<unknown>;
  setSetting: (key: string, value: unknown) => Promise<void>;
  getAllSettings: () => Promise<Partial<Settings>>;
  
  // ═══════════════════════════════════════════════════════════════════════
  // PYTHON BACKEND (02 AI BRAIN)
  // ═══════════════════════════════════════════════════════════════════════
  backendChat: (message: string) => Promise<BackendResponse>;
  backendChatVoice: (message: string) => Promise<BackendResponse>;
  backendStatus: () => Promise<BackendResponse>;
  backendScanSystem: () => Promise<BackendResponse>;
  backendScanUrl: (url: string) => Promise<BackendResponse>;
  backendScanFile: (filepath: string) => Promise<BackendResponse>;
  backendScanNetwork: (target: string) => Promise<BackendResponse>;
  backendAnalyzeEmail: (content: string) => Promise<BackendResponse>;
  backendAutonomousStart: () => Promise<BackendResponse>;
  backendAutonomousStop: () => Promise<BackendResponse>;
  backendAgentStatus: () => Promise<BackendResponse>;
  backendMemoryStore: (key: string, value: any, category: string) => Promise<BackendResponse>;
  backendMemoryRecall: (key: string) => Promise<BackendResponse>;
  backendGenerateReport: () => Promise<BackendResponse>;
  backendHealthCheck: () => Promise<boolean>;
  
  onVoiceToggle: (callback: () => void) => () => void;
  onOpenSettings: (callback: () => void) => () => void;
}

export interface BackendResponse {
  success: boolean;
  data?: any;
  error?: string;
  response?: string;
  intent?: string;
  actions?: any[];
  speakable?: boolean;
}

export interface SystemInfo {
  platform: string;
  hostname: string;
  type: string;
  release: string;
  cpus: number;
  totalMemory: number;
  freeMemory: number;
  uptime: number;
}

export interface ThreatInfo {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  recommendation: string;
  timestamp: Date;
}

export interface SecurityReport {
  overallScore: number;
  threats: ThreatInfo[];
  recommendations: string[];
  lastScan: Date;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}
