export interface Plugin {
  id: string;
  name: string;
  description: string;
  version: string;
  author?: string;
  commands: PluginCommand[];
  onLoad?: () => void | Promise<void>;
  onUnload?: () => void | Promise<void>;
}

export interface PluginCommand {
  name: string;
  description: string;
  aliases?: string[];
  execute: (context: PluginContext) => Promise<PluginResult>;
}

export interface PluginContext {
  args: string[];
  api: {
    openApp: (app: string) => Promise<{ success: boolean }>;
    closeApp: (app: string) => Promise<{ success: boolean }>;
    openUrl: (url: string) => Promise<{ success: boolean }>;
    screenshot: () => Promise<{ success: boolean; path?: string }>;
    setVolume: (volume: number) => Promise<{ success: boolean }>;
    getClipboard: () => Promise<{ text: string }>;
    setClipboard: (text: string) => Promise<{ success: boolean }>;
    getSystemInfo: () => Promise<any>;
  };
  speak: (text: string) => void;
}

export interface PluginResult {
  success: boolean;
  message: string;
  data?: any;
}
