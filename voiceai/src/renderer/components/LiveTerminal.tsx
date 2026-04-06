import { useState, useEffect, useRef } from 'react';

interface TerminalLine {
  id: number;
  type: 'input' | 'output' | 'error' | 'system' | 'success';
  content: string;
  timestamp: Date;
}

interface LiveTerminalProps {
  onCommand?: (command: string) => void;
  autoScroll?: boolean;
  maxLines?: number;
}

export default function LiveTerminal({ onCommand, autoScroll = true, maxLines = 500 }: LiveTerminalProps) {
  const [lines, setLines] = useState<TerminalLine[]>([]);
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [isExecuting, setIsExecuting] = useState(false);
  const terminalRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const lineIdRef = useRef(0);

  useEffect(() => {
    if (autoScroll && terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [lines]);

  useEffect(() => {
    addLine('system', '02 Terminal v1.0 - Ready for commands');
    addLine('system', 'Type "help" for available commands');
    addLine('system', '');
  }, []);

  const addLine = (type: TerminalLine['type'], content: string) => {
    const newLine: TerminalLine = {
      id: lineIdRef.current++,
      type,
      content,
      timestamp: new Date()
    };
    
    setLines(prev => {
      const updated = [...prev, newLine];
      if (updated.length > maxLines) {
        return updated.slice(-maxLines);
      }
      return updated;
    });
  };

  const executeCommand = async (command: string) => {
    if (!command.trim()) return;

    addLine('input', `> ${command}`);
    setHistory(prev => [...prev, command]);
    setHistoryIndex(-1);
    setInput('');
    setIsExecuting(true);

    try {
      if (onCommand) {
        const result = await onCommand(command);
        if (result) {
          if (result.success) {
            result.output?.split('\n').forEach(line => addLine('output', line));
          } else {
            addLine('error', result.error || 'Command failed');
          }
        }
      } else {
        const result = await simulateCommand(command);
        if (result.type === 'success') {
          result.output?.forEach(line => addLine('success', line));
        } else if (result.type === 'error') {
          result.output?.forEach(line => addLine('error', line));
        } else {
          result.output?.forEach(line => addLine('output', line));
        }
      }
    } catch (error) {
      addLine('error', `Error: ${error}`);
    }

    setIsExecuting(false);
  };

  const simulateCommand = async (command: string): Promise<{ type: string; output?: string[] }> => {
    const cmd = command.toLowerCase().trim();
    const args = command.split(' ').slice(1).join(' ');

    await new Promise(resolve => setTimeout(resolve, 200));

    if (cmd === 'help') {
      return {
        type: 'output',
        output: [
          'Available commands:',
          '  help          - Show this help',
          '  clear         - Clear terminal',
          '  date          - Show current date/time',
          '  whoami        - Show user info',
          '  pwd           - Show current directory',
          '  ls            - List files',
          '  echo [text]   - Print text',
          '  status        - System status',
          '  scan          - Run security scan',
          '  memory        - Memory stats'
        ]
      };
    }

    if (cmd === 'clear') {
      setLines([]);
      return { type: 'output', output: [] };
    }

    if (cmd === 'date') {
      return {
        type: 'output',
        output: [new Date().toLocaleString()]
      };
    }

    if (cmd === 'whoami') {
      return {
        type: 'output',
        output: ['User: ' + (process.env.USERNAME || 'User'), 'Role: Administrator']
      };
    }

    if (cmd === 'status') {
      return {
        type: 'success',
        output: [
          'System Status:',
          '  CPU: 23% utilized',
          '  Memory: 4.2 GB used',
          '  Disk: 45% used',
          '  Network: Connected',
          '  AI Engine: Online',
          '  Security: Active'
        ]
      };
    }

    if (cmd === 'scan') {
      addLine('system', 'Starting security scan...');
      await new Promise(resolve => setTimeout(resolve, 1000));
      return {
        type: 'success',
        output: [
          'Scan complete!',
          '  Threats found: 0',
          '  Security score: 95/100',
          '  Last scan: Just now'
        ]
      };
    }

    if (cmd === 'memory') {
      return {
        type: 'output',
        output: [
          'Memory Usage:',
          '  Working: 7 items',
          '  Episodic: 45 memories',
          '  Semantic: 128 facts',
          '  Procedural: 23 skills'
        ]
      };
    }

    if (cmd.startsWith('echo ')) {
      return { type: 'output', output: [args] };
    }

    if (cmd === 'ls') {
      return {
        type: 'output',
        output: [
          'drwxr-xr-x  cyber-assistant/',
          'drwxr-xr-x  voiceai/',
          '-rw-r--r--  README.md',
          '-rw-r--r--  package.json'
        ]
      };
    }

    return { type: 'error', output: [`Command not found: ${cmd}`] };
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isExecuting) {
      executeCommand(input);
    }

    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (history.length > 0) {
        const newIndex = historyIndex < history.length - 1 ? historyIndex + 1 : historyIndex;
        setHistoryIndex(newIndex);
        setInput(history[history.length - 1 - newIndex] || '');
      }
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setInput(history[history.length - 1 - newIndex] || '');
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setInput('');
      }
    }
  };

  const getLineColor = (type: TerminalLine['type']) => {
    switch (type) {
      case 'input': return 'text-primary';
      case 'output': return 'text-gray-300';
      case 'error': return 'text-red-400';
      case 'success': return 'text-green-400';
      case 'system': return 'text-cyan-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="bg-[#0d1117] rounded-xl border border-border overflow-hidden h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-[#161b22] border-b border-[#30363d]">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-[#ff5f56]"></div>
            <div className="w-3 h-3 rounded-full bg-[#ffbd2e]"></div>
            <div className="w-3 h-3 rounded-full bg-[#27c93f]"></div>
          </div>
          <span className="text-xs text-gray-400 ml-2">02 Terminal</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span>{lines.length} lines</span>
          <button
            onClick={() => setLines([])}
            className="px-2 py-0.5 hover:bg-surface rounded transition-all"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Terminal output */}
      <div
        ref={terminalRef}
        className="flex-1 p-4 overflow-y-auto font-mono text-sm"
        onClick={() => inputRef.current?.focus()}
      >
        {lines.map(line => (
          <div key={line.id} className={`${getLineColor(line.type)} mb-1 whitespace-pre-wrap`}>
            {line.content}
          </div>
        ))}
        
        {/* Input line */}
        <div className="flex items-center">
          <span className="text-primary mr-2">&gt;</span>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isExecuting}
            className="flex-1 bg-transparent text-gray-200 outline-none font-mono text-sm"
            placeholder={isExecuting ? 'Executing...' : 'Type command...'}
            autoFocus
          />
          {isExecuting && (
            <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          )}
        </div>
      </div>
    </div>
  );
}
