import { Plugin, PluginContext, PluginCommand } from './plugin-types';

const builtInCommands: Record<string, PluginCommand> = {
  system: {
    name: 'system',
    description: 'Get system information',
    execute: async (ctx) => {
      const info = await ctx.api.getSystemInfo();
      const uptime = Math.floor(info.info.uptime / 60);
      return {
        success: true,
        message: `System: ${info.info.type} ${info.info.release}\nHostname: ${info.info.hostname}\nCPU: ${info.info.cpus} cores\nMemory: ${info.info.freeMemory}GB free of ${info.info.totalMemory}GB\nUptime: ${uptime} minutes`,
        data: info,
      };
    },
  },
  volume: {
    name: 'volume',
    description: 'Control system volume',
    aliases: ['vol', 'sound'],
    execute: async (ctx) => {
      const level = parseInt(ctx.args[0]);
      if (isNaN(level)) {
        const current = await window.electronAPI?.getVolume();
        return { success: true, message: `Current volume: ${current?.volume || 50}%` };
      }
      await ctx.api.setVolume(level);
      return { success: true, message: `Volume set to ${level}%` };
    },
  },
  clipboard: {
    name: 'clipboard',
    description: 'Read or write to clipboard',
    aliases: ['copy', 'paste'],
    execute: async (ctx) => {
      if (ctx.args.length === 0) {
        const clip = await ctx.api.getClipboard();
        return { success: true, message: `Clipboard: ${clip.text || '(empty)'}` };
      }
      const text = ctx.args.join(' ');
      await ctx.api.setClipboard(text);
      return { success: true, message: `Copied to clipboard: ${text.slice(0, 50)}${text.length > 50 ? '...' : ''}` };
    },
  },
  screenshot: {
    name: 'screenshot',
    description: 'Take a screenshot',
    aliases: ['snap', 'capture'],
    execute: async (ctx) => {
      const result = await window.electronAPI?.screenshot();
      if (result?.success) {
        ctx.speak('Screenshot saved');
        return { success: true, message: `Screenshot saved to ${result.path}` };
      }
      return { success: false, message: 'Failed to take screenshot' };
    },
  },
  weather: {
    name: 'weather',
    description: 'Get weather for a location',
    aliases: ['temp', 'forecast'],
    execute: async (ctx) => {
      const location = ctx.args.join(' ') || 'current location';
      try {
        const response = await fetch(`https://wttr.in/${encodeURIComponent(location)}?format=j1`);
        const data = await response.json();
        const current = data.current_condition[0];
        return {
          success: true,
          message: `Weather in ${location}: ${current.weatherDesc[0].value}, ${current.temp_C}°C (${current.temp_F}°F), Humidity: ${current.humidity}%`,
        };
      } catch {
        return { success: false, message: 'Could not fetch weather data' };
      }
    },
  },
  time: {
    name: 'time',
    description: 'Get current time',
    aliases: ['date', 'now'],
    execute: async () => {
      const now = new Date();
      return {
        success: true,
        message: `Current time: ${now.toLocaleTimeString()}\nDate: ${now.toLocaleDateString()}`,
      };
    },
  },
  calculator: {
    name: 'calculator',
    description: 'Calculate a math expression',
    aliases: ['calc', 'math'],
    execute: async (ctx) => {
      const expr = ctx.args.join('');
      try {
        const result = eval(expr);
        return { success: true, message: `${expr} = ${result}` };
      } catch {
        return { success: false, message: 'Invalid expression' };
      }
    },
  },
  reminder: {
    name: 'reminder',
    description: 'Set a reminder',
    aliases: ['remind', 'alarm'],
    execute: async (ctx) => {
      const [minutes, ...msgParts] = ctx.args;
      const mins = parseInt(minutes);
      if (isNaN(mins)) {
        return { success: false, message: 'Usage: remind <minutes> <message>' };
      }
      const message = msgParts.join(' ') || 'Reminder!';
      setTimeout(() => {
        ctx.speak(message);
      }, mins * 60 * 1000);
      return { success: true, message: `Reminder set for ${mins} minute(s): ${message}` };
    },
  },
  todo: {
    name: 'todo',
    description: 'Manage todo list',
    aliases: ['todos', 'tasks'],
    execute: async (ctx) => {
      const subcmd = ctx.args[0]?.toLowerCase();
      const item = ctx.args.slice(1).join(' ');
      const todos = JSON.parse(localStorage.getItem('todos') || '[]');
      
      switch (subcmd) {
        case 'add':
          todos.push({ id: Date.now(), text: item, done: false });
          localStorage.setItem('todos', JSON.stringify(todos));
          return { success: true, message: `Added: ${item}` };
        case 'list':
          if (todos.length === 0) return { success: true, message: 'No todos yet!' };
          const list = todos.map((t: any, i: number) => `${t.done ? '✓' : '○'} ${i + 1}. ${t.text}`).join('\n');
          return { success: true, message: `Todos:\n${list}` };
        case 'done':
          const idx = parseInt(item) - 1;
          if (todos[idx]) {
            todos[idx].done = true;
            localStorage.setItem('todos', JSON.stringify(todos));
            return { success: true, message: `Marked complete: ${todos[idx].text}` };
          }
          return { success: false, message: 'Invalid todo number' };
        case 'clear':
          localStorage.setItem('todos', '[]');
          return { success: true, message: 'All todos cleared' };
        default:
          return { success: true, message: 'Usage: todo [add|list|done|clear] [item]' };
      }
    },
  },
};

class PluginManager {
  private plugins: Map<string, Plugin> = new Map();
  private commandMap: Map<string, PluginCommand> = new Map();

  constructor() {
    this.registerBuiltInCommands();
  }

  private registerBuiltInCommands() {
    Object.entries(builtInCommands).forEach(([name, cmd]) => {
      this.commandMap.set(name, cmd);
      cmd.aliases?.forEach(alias => this.commandMap.set(alias, cmd));
    });
  }

  async loadPlugin(plugin: Plugin): Promise<void> {
    this.plugins.set(plugin.id, plugin);
    plugin.commands.forEach(cmd => {
      this.commandMap.set(cmd.name, cmd);
      cmd.aliases?.forEach(alias => this.commandMap.set(alias, cmd));
    });
    await plugin.onLoad?.();
  }

  async unloadPlugin(pluginId: string): Promise<void> {
    const plugin = this.plugins.get(pluginId);
    if (plugin) {
      plugin.commands.forEach(cmd => {
        this.commandMap.delete(cmd.name);
        cmd.aliases?.forEach(alias => this.commandMap.delete(alias));
      });
      await plugin.onUnload?.();
      this.plugins.delete(pluginId);
    }
  }

  async executeCommand(name: string, args: string[], context: PluginContext): Promise<PluginResult> {
    const command = this.commandMap.get(name.toLowerCase());
    if (!command) {
      return { success: false, message: `Unknown command: ${name}` };
    }
    return command.execute({ ...context, args });
  }

  getAllCommands(): PluginCommand[] {
    return Array.from(this.commandMap.values()).filter(
      (cmd, i, arr) => arr.findIndex(c => c.name === cmd.name) === i
    );
  }

  getPlugins(): Plugin[] {
    return Array.from(this.plugins.values());
  }
}

export const pluginManager = new PluginManager();
