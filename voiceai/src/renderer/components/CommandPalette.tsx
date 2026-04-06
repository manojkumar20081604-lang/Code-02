import { useState, useEffect, useMemo } from 'react';
import { useStore } from '../store/useStore';
import { pluginManager } from '../lib/pluginManager';

function CommandPalette() {
  const { commandPaletteOpen, setCommandPaletteOpen, addMessage } = useStore();
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  const commands = useMemo(() => {
    const cmds = pluginManager.getAllCommands();
    return [
      {
        name: 'open',
        description: 'Open an application',
        category: 'System',
        action: () => {
          addMessage({ role: 'system', content: 'Say: "Open [app name]"' });
          setCommandPaletteOpen(false);
        },
      },
      {
        name: 'close',
        description: 'Close an application',
        category: 'System',
        action: () => {
          addMessage({ role: 'system', content: 'Say: "Close [app name]"' });
          setCommandPaletteOpen(false);
        },
      },
      {
        name: 'search',
        description: 'Search the web',
        category: 'Web',
        action: () => {
          addMessage({ role: 'system', content: 'Say: "Search for [query]"' });
          setCommandPaletteOpen(false);
        },
      },
      {
        name: 'screenshot',
        description: 'Take a screenshot',
        category: 'System',
        action: () => {
          window.electronAPI?.screenshot();
          addMessage({ role: 'system', content: 'Taking screenshot...' });
          setCommandPaletteOpen(false);
        },
      },
      {
        name: 'camera',
        description: 'Open camera',
        category: 'Media',
        action: () => {
          useStore.getState().setCameraOpen(true);
          setCommandPaletteOpen(false);
        },
      },
      {
        name: 'volume',
        description: 'Control volume',
        category: 'System',
        action: () => {
          addMessage({ role: 'system', content: 'Say: "Volume [0-100]"' });
          setCommandPaletteOpen(false);
        },
      },
      {
        name: 'clipboard',
        description: 'Read/write clipboard',
        category: 'System',
        action: () => {
          addMessage({ role: 'system', content: 'Say: "Copy [text]" or "Clipboard"' });
          setCommandPaletteOpen(false);
        },
      },
      {
        name: 'system',
        description: 'Get system information',
        category: 'Info',
        action: () => {
          pluginManager.executeCommand('system', [], {
            args: [],
            api: {
              openApp: (app) => window.electronAPI?.openApp(app) || Promise.resolve({ success: false }),
              closeApp: (app) => window.electronAPI?.closeApp(app) || Promise.resolve({ success: false }),
              openUrl: (url) => window.electronAPI?.openUrl(url) || Promise.resolve({ success: false }),
              screenshot: () => window.electronAPI?.screenshot() || Promise.resolve({ success: false }),
              setVolume: (v) => window.electronAPI?.setVolume(v) || Promise.resolve({ success: false }),
              getClipboard: () => window.electronAPI?.getClipboard() || Promise.resolve({ text: '' }),
              setClipboard: (t) => window.electronAPI?.setClipboard(t) || Promise.resolve({ success: false }),
              getSystemInfo: () => window.electronAPI?.getSystemInfo() || Promise.resolve({ success: false }),
            },
            speak: () => {},
          }).then(result => {
            addMessage({ role: 'assistant', content: result.message });
          });
          setCommandPaletteOpen(false);
        },
      },
        {
        name: 'weather',
        description: 'Get weather information',
        category: 'Info',
        action: () => {
          pluginManager.executeCommand('weather', [], {
            args: [],
            api: {
              openApp: (app) => window.electronAPI?.openApp(app) || Promise.resolve({ success: false }),
              closeApp: (app) => window.electronAPI?.closeApp(app) || Promise.resolve({ success: false }),
              openUrl: (url) => window.electronAPI?.openUrl(url) || Promise.resolve({ success: false }),
              screenshot: () => window.electronAPI?.screenshot() || Promise.resolve({ success: false }),
              setVolume: (v) => window.electronAPI?.setVolume(v) || Promise.resolve({ success: false }),
              getClipboard: () => window.electronAPI?.getClipboard() || Promise.resolve({ text: '' }),
              setClipboard: (t) => window.electronAPI?.setClipboard(t) || Promise.resolve({ success: false }),
              getSystemInfo: () => window.electronAPI?.getSystemInfo() || Promise.resolve({ success: false }),
            },
            speak: () => {},
          }).then(result => {
            addMessage({ role: 'assistant', content: result.message });
          });
          setCommandPaletteOpen(false);
        },
      },
      {
        name: 'security scan',
        description: 'Run full security scan',
        category: 'Security',
        action: () => {
          addMessage({ role: 'system', content: 'Running security scan...' });
          setCommandPaletteOpen(false);
          useStore.getState().setSecurityScanOpen(true);
          window.electronAPI?.cyberFullScan().then(result => {
            if (result?.success) {
              useStore.getState().setSecurityScore(result.report.overallScore);
              useStore.getState().setThreats(result.report.threats);
            }
          });
        },
      },
      {
        name: 'cyber shield',
        description: 'Enable continuous monitoring',
        category: 'Security',
        action: () => {
          window.electronAPI?.cyberStartMonitoring(30000);
          useStore.getState().setIsMonitoring(true);
          addMessage({ role: 'system', content: '🛡️ 02 Cyber Shield activated!' });
          setCommandPaletteOpen(false);
        },
      },
      {
        name: 'check url',
        description: 'Analyze URL for threats',
        category: 'Security',
        action: () => {
          addMessage({ role: 'system', content: 'Say: "check URL [link]" to analyze' });
          setCommandPaletteOpen(false);
        },
      },
      ...cmds.map(cmd => ({
        name: cmd.name,
        description: cmd.description,
        category: 'Plugins',
        action: () => {
          addMessage({ role: 'system', content: `Say: "${cmd.name} [args]"` });
          setCommandPaletteOpen(false);
        },
      })),
    ];
  }, [addMessage, setCommandPaletteOpen]);

  const filteredCommands = useMemo(() => {
    if (!query) return commands;
    const lower = query.toLowerCase();
    return commands.filter(
      cmd =>
        cmd.name.toLowerCase().includes(lower) ||
        cmd.description.toLowerCase().includes(lower)
    );
  }, [query, commands]);

  useEffect(() => {
    if (commandPaletteOpen) {
      setQuery('');
      setSelectedIndex(0);
    }
  }, [commandPaletteOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!commandPaletteOpen) {
        if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
          e.preventDefault();
          setCommandPaletteOpen(true);
        }
        return;
      }

      if (e.key === 'Escape') {
        setCommandPaletteOpen(false);
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(i => Math.min(i + 1, filteredCommands.length - 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(i => Math.max(i - 1, 0));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        filteredCommands[selectedIndex]?.action();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [commandPaletteOpen, filteredCommands, selectedIndex, setCommandPaletteOpen]);

  if (!commandPaletteOpen) return null;

  const categories = [...new Set(filteredCommands.map(c => c.category))];

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-start justify-center pt-24 z-50">
      <div className="w-full max-w-lg glass rounded-xl overflow-hidden animate-[slideDown_0.15s_ease-out]">
        <div className="p-3 border-b border-white/10">
          <input
            type="text"
            value={query}
            onChange={e => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Type a command..."
            className="w-full bg-transparent text-text-primary placeholder-text-secondary/50 outline-none text-lg"
            autoFocus
          />
        </div>

        <div className="max-h-96 overflow-y-auto p-2">
          {filteredCommands.length === 0 ? (
            <div className="p-4 text-center text-text-secondary">
              No commands found
            </div>
          ) : (
            categories.map(category => (
              <div key={category} className="mb-2">
                <div className="px-3 py-1 text-xs font-medium text-text-secondary uppercase">
                  {category}
                </div>
                {filteredCommands
                  .filter(c => c.category === category)
                  .map((cmd, i) => {
                    const globalIndex = filteredCommands.indexOf(cmd);
                    return (
                      <button
                        key={cmd.name}
                        onClick={() => cmd.action()}
                        className={`w-full px-3 py-2 rounded-lg text-left flex items-center gap-3 transition-colors ${
                          globalIndex === selectedIndex
                            ? 'bg-primary/20 text-text-primary'
                            : 'text-text-secondary hover:bg-white/5'
                        }`}
                      >
                        <span className="font-mono text-sm">{cmd.name}</span>
                        <span className="text-sm opacity-70">{cmd.description}</span>
                      </button>
                    );
                  })}
              </div>
            ))
          )}
        </div>

        <div className="p-2 border-t border-white/10 flex items-center justify-between text-xs text-text-secondary">
          <div className="flex items-center gap-2">
            <kbd className="px-1.5 py-0.5 rounded bg-white/10">↑↓</kbd>
            <span>Navigate</span>
          </div>
          <div className="flex items-center gap-2">
            <kbd className="px-1.5 py-0.5 rounded bg-white/10">Enter</kbd>
            <span>Select</span>
          </div>
          <div className="flex items-center gap-2">
            <kbd className="px-1.5 py-0.5 rounded bg-white/10">Esc</kbd>
            <span>Close</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CommandPalette;
