import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  // Window controls
  minimize: () => ipcRenderer.send('window:minimize'),
  maximize: () => ipcRenderer.send('window:maximize'),
  close: () => ipcRenderer.send('window:close'),

  // System control - Apps
  openApp: (appName: string) => ipcRenderer.invoke('system:open-app', appName),
  closeApp: (appName: string) => ipcRenderer.invoke('system:close-app', appName),
  getRunningApps: () => ipcRenderer.invoke('system:get-running-apps'),

  // System control - Navigation
  openUrl: (url: string) => ipcRenderer.invoke('system:open-url', url),
  search: (query: string) => ipcRenderer.invoke('system:search', query),
  openFolder: (path: string) => ipcRenderer.invoke('system:open-folder', path),
  listDesktop: () => ipcRenderer.invoke('system:list-desktop'),

  // System control - Media
  screenshot: () => ipcRenderer.invoke('system:screenshot'),
  cameraCapture: () => ipcRenderer.invoke('system:camera-capture'),

  // System control - System
  lock: () => ipcRenderer.invoke('system:lock'),
  shutdown: () => ipcRenderer.invoke('system:shutdown'),
  setVolume: (volume: number) => ipcRenderer.invoke('system:set-volume', volume),
  getVolume: () => ipcRenderer.invoke('system:get-volume'),
  setBrightness: (brightness: number) => ipcRenderer.invoke('system:set-brightness', brightness),

  // System control - Clipboard
  getClipboard: () => ipcRenderer.invoke('system:get-clipboard'),
  setClipboard: (text: string) => ipcRenderer.invoke('system:set-clipboard', text),

  // System control - Info
  getSystemInfo: () => ipcRenderer.invoke('system:get-info'),
  executeCommand: (command: string) => ipcRenderer.invoke('system:execute', command),
  runCode: (code: string, language: string) => ipcRenderer.invoke('system:run-code', code, language),
  readFile: (filePath: string) => ipcRenderer.invoke('system:read-file', filePath),
  writeFile: (filePath: string, content: string) => ipcRenderer.invoke('system:write-file', filePath, content),

  // ═══════════════════════════════════════════════════════════════════════
  // CYBER SECURITY
  // ═══════════════════════════════════════════════════════════════════════
  cyberFullScan: () => ipcRenderer.invoke('cyber:full-scan'),
  cyberQuickScan: () => ipcRenderer.invoke('cyber:quick-scan'),
  cyberStartMonitoring: (intervalMs?: number) => ipcRenderer.invoke('cyber:start-monitoring', intervalMs),
  cyberStopMonitoring: () => ipcRenderer.invoke('cyber:stop-monitoring'),
  cyberGetThreats: () => ipcRenderer.invoke('cyber:get-threats'),
  cyberAnalyzeUrl: (url: string) => ipcRenderer.invoke('cyber:analyze-url', url),
  cyberAnalyzeHash: (hash: string) => ipcRenderer.invoke('cyber:analyze-hash', hash),
  cyberGenerateReport: () => ipcRenderer.invoke('cyber:generate-report'),
  cyberCheckApp: (appName: string) => ipcRenderer.invoke('cyber:check-app', appName),
  cyberAlert: (title: string, body: string) => ipcRenderer.invoke('cyber:alert', title, body),
  cyberBlockApp: (appName: string, block: boolean) => ipcRenderer.invoke('cyber:block-app', appName, block),
  cyberCheckLeaks: (email: string) => ipcRenderer.invoke('cyber:check-leaks', email),

  // Settings
  getSetting: (key: string) => ipcRenderer.invoke('settings:get', key),
  setSetting: (key: string, value: unknown) => ipcRenderer.invoke('settings:set', key, value),
  getAllSettings: () => ipcRenderer.invoke('settings:getAll'),

  // ═══════════════════════════════════════════════════════════════════════
  // PYTHON BACKEND (02 AI BRAIN)
  // ═══════════════════════════════════════════════════════════════════════
  backendChat: (message: string) => ipcRenderer.invoke('backend:chat', message),
  backendChatVoice: (message: string) => ipcRenderer.invoke('backend:chat-voice', message),
  backendStatus: () => ipcRenderer.invoke('backend:status'),
  backendScanSystem: () => ipcRenderer.invoke('backend:scan-system'),
  backendScanUrl: (url: string) => ipcRenderer.invoke('backend:scan-url', url),
  backendScanFile: (filepath: string) => ipcRenderer.invoke('backend:scan-file', filepath),
  backendScanNetwork: (target: string) => ipcRenderer.invoke('backend:scan-network', target),
  backendAnalyzeEmail: (content: string) => ipcRenderer.invoke('backend:analyze-email', content),
  backendAutonomousStart: () => ipcRenderer.invoke('backend:autonomous-start'),
  backendAutonomousStop: () => ipcRenderer.invoke('backend:autonomous-stop'),
  backendAgentStatus: () => ipcRenderer.invoke('backend:agent-status'),
  backendMemoryStore: (key: string, value: any, category: string) => ipcRenderer.invoke('backend:memory-store', key, value, category),
  backendMemoryRecall: (key: string) => ipcRenderer.invoke('backend:memory-recall', key),
  backendGenerateReport: () => ipcRenderer.invoke('backend:generate-report'),
  backendHealthCheck: () => ipcRenderer.invoke('backend:health-check'),
  
  // ML & Monitoring
  backendMLPhishing: (url?: string, subject?: string, body?: string) => ipcRenderer.invoke('backend:ml-phishing', url, subject, body),
  backendMonitorStart: (interval?: number) => ipcRenderer.invoke('backend:monitor-start', interval),
  backendMonitorStop: () => ipcRenderer.invoke('backend:monitor-stop'),
  backendMonitorStatus: () => ipcRenderer.invoke('backend:monitor-status'),
  backendMonitorAlerts: () => ipcRenderer.invoke('backend:monitor-alerts'),

  // Events
  onVoiceToggle: (callback: () => void) => {
    ipcRenderer.on('voice:toggle', callback);
    return () => ipcRenderer.removeListener('voice:toggle', callback);
  },
  onOpenSettings: (callback: () => void) => {
    ipcRenderer.on('open-settings', callback);
    return () => ipcRenderer.removeListener('open-settings', callback);
  },
});
